from __future__ import annotations

from typing import Any, Generator, Union

from pydantic import BaseModel

from ._decision import decision_tree


__all__ = (
    "ObjectRule",
    "ObjectRuleMatch",
    "ObjectRuleParameter",
    "ObjectRuleLiteralParameter",
    "ObjectRuleOptionalParameter",
    "ObjectRulePositionalParameter",
    "ObjectRulePositionalParameterObjectValue",
    "ObjectRulePositionalParameterStringValue",
    "ObjectRulePositionalParameterValue",
    "ObjectRulePositionalParameterIntegerValue",
    "ObjectRuleUnionParameter",

    "match"
)


class ObjectRuleMatchError(Exception):
    pass


class ObjectRuleNotFoundError(ObjectRuleMatchError):
    pass


class ObjectRuleParameterMatchError(ObjectRuleMatchError):
    pass


class ObjectRulePositionalParameterMatchError(ObjectRuleParameterMatchError):
    pass


class ObjectRuleUnionParameterMatchError(ObjectRuleParameterMatchError):
    pass


class NotEnoughArgumentsError(ObjectRuleParameterMatchError):
    pass


class ObjectRuleMatch(BaseModel):
    rule: ObjectRule
    literals: list[str]
    positionals: dict[str, Any]


def _wrap_matcher(function):
    def wrapped(arguments):
        try:
            for item in function(arguments):
                yield (item, (item[1],), {})
        except ObjectRuleParameterMatchError:
            return

    return wrapped


class ObjectRule(BaseModel):
    name: str
    parameters: list[ObjectRuleParameter]

    def match(
        self,
        arguments: list[str],
        root: bool = False
    ) -> tuple[ObjectRuleMatch, list[str]]:
        literals = []
        positionals = {}
        generators = [
            _wrap_matcher(parameter.match)
            for parameter in self.parameters
        ]

        decisions = list(decision_tree(generators)(arguments))

        if not decisions:
            raise ObjectRuleParameterMatchError

        decision = decisions[0]
        remaining_arguments = None

        for matches, remaining_arguments in decision:
            for item in matches:
                if isinstance(item, ObjectRuleLiteralParameterMatch):
                    literals.append(item.value)
                elif isinstance(item, ObjectRulePositionalParameterMatch):
                    positionals[item.name] = item.value
                else:
                    raise RuntimeError

        return (
            ObjectRuleMatch(
                rule=self,
                literals=literals,
                positionals=positionals
            ),
            remaining_arguments
        )


class ObjectRuleLiteralParameterMatch(BaseModel):
    value: str


class ObjectRulePositionalParameterMatch(BaseModel):
    name: str
    value: Any


ObjectRuleParameterMatch = Union[
    ObjectRuleLiteralParameterMatch,
    ObjectRulePositionalParameterMatch
]


class ObjectRuleLiteralParameter(BaseModel):
    value: str

    def match(
        self,
        arguments: list[str]
    ) -> Generator[
        tuple[
            list[ObjectRuleLiteralParameterMatch],
            list[str]
        ],
        None,
        None
    ]:
        try:
            value, *arguments = arguments
        except ValueError:
            raise NotEnoughArgumentsError

        if value.lower() != self.value.lower():
            raise ObjectRuleParameterMatchError

        yield [ObjectRuleLiteralParameterMatch(value=value)], arguments


class ObjectRulePositionalParameterObjectValue(ObjectRule):
    def match(
        self,
        arguments: list[str]
    ) -> tuple[ObjectRuleMatch, list[str]]:
        try:
            value, *arguments = arguments
        except ValueError:
            raise NotEnoughArgumentsError

        if value.lower() != self.name.lower():
            raise ObjectRuleParameterMatchError

        return super().match(arguments)


class ObjectRulePositionalParameterStringValue(BaseModel):
    def match(
        self,
        arguments: list[str]
    ) -> tuple[str, list[str]]:
        try:
            value, *arguments = arguments
        except ValueError:
            raise NotEnoughArgumentsError

        return value, arguments


class ObjectRulePositionalParameterIntegerValue(BaseModel):
    def match(
        self,
        arguments: list[str]
    ) -> tuple[int, list[str]]:
        try:
            value, *arguments = arguments
        except ValueError:
            raise NotEnoughArgumentsError

        try:
            value = int(value)
        except ValueError:
            raise ObjectRulePositionalParameterMatchError

        return value, arguments


ObjectRulePositionalParameterValue = Union[
    ObjectRulePositionalParameterObjectValue,
    ObjectRulePositionalParameterStringValue,
    ObjectRulePositionalParameterIntegerValue
]


class ObjectRulePositionalParameter(BaseModel):
    name: str
    value: list[ObjectRulePositionalParameterValue]

    def match(
        self,
        arguments: list[str]
    ) -> Generator[
        tuple[
            list[ObjectRulePositionalParameterMatch],
            list[str]
        ],
        None,
        None
    ]:
        error = None

        for value in self.value:
            try:
                result, remaining_arguments = value.match(arguments)

                yield (
                    [
                        ObjectRulePositionalParameterMatch(
                            name=self.name,
                            value=result
                        )
                    ],
                    remaining_arguments
                )
            except ObjectRuleParameterMatchError as exception:
                error = exception

        if error:
            raise error


class ObjectRuleUnionParameter(BaseModel):
    members: list[list[ObjectRuleParameter]]

    def match(
        self,
        arguments: list[str]
    ) -> Generator[
        tuple[
            list[ObjectRuleParameterMatch],
            list[str]
        ],
        None,
        None
    ]:
        for member in self.members:
            if member == []:
                yield [], arguments
                continue

            generators = [
                _wrap_matcher(parameter.match)
                for parameter in member
            ]

            for decision in decision_tree(generators)(arguments):
                remaining_arguments = None
                result = []

                for matches, remaining_arguments in decision:
                    result.extend(matches)

                yield result, remaining_arguments


ObjectRuleParameter = Union[
    ObjectRuleLiteralParameter,
    ObjectRulePositionalParameter,
    ObjectRuleUnionParameter
]


def _find_rules(
    name: str,
    rules: list[ObjectRule]
) -> list[ObjectRule]:
    return [rule for rule in rules if rule.name == name]


def match(arguments: list[str], rules: list[ObjectRule]) -> ObjectRuleMatch:
    name, *arguments = arguments
    candidates = _find_rules(name, rules)

    if not candidates:
        raise ObjectRuleNotFoundError(name)

    error = None

    for candidate in candidates:
        try:
            return candidate.match(arguments, root=True)
        except ObjectRuleMatchError as exception:
            error = exception

    raise error
