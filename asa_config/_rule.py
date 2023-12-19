from __future__ import annotations

from typing import Any, Union

from pydantic import BaseModel


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


class ObjectRule(BaseModel):
    name: str
    parameters: list[ObjectRuleParameter]


class ObjectRuleLiteralParameter(BaseModel):
    value: str


class ObjectRulePositionalParameterObjectValue(ObjectRule):
    pass


class ObjectRulePositionalParameterStringValue(BaseModel):
    pass


class ObjectRulePositionalParameterIntegerValue(BaseModel):
    pass


ObjectRulePositionalParameterValue = Union[
    ObjectRulePositionalParameterObjectValue,
    ObjectRulePositionalParameterStringValue,
    ObjectRulePositionalParameterIntegerValue
]


class ObjectRulePositionalParameter(BaseModel):
    name: str
    value: list[ObjectRulePositionalParameterValue]


class ObjectRuleUnionParameter(BaseModel):
    members: list[list[ObjectRuleParameter]]


ObjectRuleParameter = Union[
    ObjectRuleLiteralParameter,
    ObjectRulePositionalParameter,
    ObjectRuleUnionParameter
]


class ObjectRuleMatch(BaseModel):
    rule: ObjectRule
    literals: list[str]
    positionals: dict[str, Any]


def match(
    arguments: list[str],
    rules: list[ObjectRule],
    greedy: bool = True
) -> tuple[ObjectRuleMatch, list[str]]:
    pass
