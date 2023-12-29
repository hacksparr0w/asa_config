from __future__ import annotations

from collections import OrderedDict
from typing import Any, Generator, Union

from pydantic import BaseModel

from ._decision import decision_tree


__all__ = (
    "IntegerRule",
    "LiteralRule",
    "MatchError",
    "Matcher",
    "NoneRule",
    "Object",
    "ObjectRule",
    "OptionalRule",
    "ObjectRuleProperty",
    "Rule",
    "StringRule",
    "TupleRule",
    "UnionRule",

    "match"
)


MatchGenerator = Generator[tuple[Any, list[str]], None, None]


class Matcher:
    def match(self, arguments: list[str]) -> MatchGenerator:
        raise NotImplementedError


class MatchError(Exception):
    pass


def _wrap_matcher(matcher: Matcher):
    def wrapped(arguments: list[str]):
        try:
            for item in matcher.match(arguments):
                yield item, (item[1],), {}
        except MatchError:
            pass

    return wrapped


class Object(BaseModel):
    name: str
    properties: OrderedDict[str, Any]


class IntegerRule(BaseModel, Matcher):
    def match(self, arguments: list[str]) -> MatchGenerator:
        try:
            value, *rest = arguments
            value = int(value)
        except ValueError as reason:
            raise MatchError from reason

        yield value, rest


class LiteralRule(BaseModel, Matcher):
    value: str

    def match(self, arguments: list[str]) -> MatchGenerator:
        try:
            value, *rest = arguments
        except ValueError as reason:
            raise MatchError from reason

        if value.lower() != self.value.lower():
            raise MatchError

        yield value, rest


class ObjectRuleProperty(BaseModel):
    name: str
    value: Rule


class ObjectRule(BaseModel, Matcher):
    name: str
    properties: list[ObjectRuleProperty]
    subobjects: list[ObjectRule]

    def match(self, arguments: list[str]) -> MatchGenerator:
        try:
            name, *arguments = arguments
        except ValueError as reason:
            raise MatchError from reason

        if name != self.name:
            raise MatchError

        matchers = [_wrap_matcher(prop.value) for prop in self.properties]

        for decision in decision_tree(matchers)(arguments):
            properties = OrderedDict()
            rest = None

            for prop, (value, rest) in zip(self.properties, decision):
                properties[prop.name] = value

            yield Object(name=self.name, properties=properties), rest


class StringRule(BaseModel, Matcher):
    def match(self, arguments: list[str]) -> MatchGenerator:
        try:
            value, *rest = arguments
        except ValueError as reason:
            raise MatchError from reason

        yield value, rest


class TupleRule(BaseModel, Matcher):
    values: list[Rule]

    def match(self, arguments: list[str]) -> MatchGenerator:
        matchers = [_wrap_matcher(rule) for rule in self.values]

        for decision in decision_tree(matchers)(arguments):
            result = []
            rest = None

            for value, rest in decision:
                result.append(value)

            yield tuple(result), rest


class UnionRule(BaseModel, Matcher):
    values: list[Rule]

    def match(self, arguments: list[str]) -> MatchGenerator:
        error = None

        for rule in self.values:
            try:
                yield from rule.match(arguments)

                error = None
            except MatchError as reason:
                error = reason

        if error:
            raise error


class NoneRule(BaseModel, Matcher):
    def match(self, arguments: list[str]) -> MatchGenerator:
        yield None, arguments


OptionalRule = lambda value: UnionRule(values=[value, NoneRule()])


Rule = Union[
    IntegerRule,
    LiteralRule,
    NoneRule,
    ObjectRule,
    StringRule,
    TupleRule,
    UnionRule
]


def match(arguments: list[str], rules: list[ObjectRule]) -> Object:
    for rule in rules:
        try:
            result, _ = next(rule.match(arguments))

            return result
        except (MatchError, StopIteration):
            continue

    raise MatchError
