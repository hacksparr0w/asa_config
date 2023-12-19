from __future__ import annotations

import json

from io import IOBase, StringIO
from enum import StrEnum, auto
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

from ._rule import (
    ObjectRule,
    ObjectRuleLiteralParameter,
    ObjectRulePositionalParameter,
    ObjectRulePositionalParameterIntegerValue,
    ObjectRulePositionalParameterObjectValue,
    ObjectRulePositionalParameterStringValue,
    ObjectRuleUnionParameter
)


__all__ = (
    "JsonObjectRule",
    "JsonObjectRuleLiteralParameter",
    "JsonObjectRuleOptionalParameter",
    "JsonObjectRuleParameter",
    "JsonObjectRuleParameterType",
    "JsonObjectRulePositionalParameter",
    "JsonObjectRulePositionalParameterIntegerValue",
    "JsonObjectRulePositionalParameterObjectValue",
    "JsonObjectRulePositionalParameterStringValue",
    "JsonObjectRulePositionalParameterValue",
    "JsonObjectRulePositionalParameterValueType",
    "JsonObjectRuleUnionParameter",

    "load"
)


class JsonObjectRule(BaseModel):
    name: str
    parameters: list[JsonObjectRuleParameter]

    def convert(self) -> ObjectRule:
        return ObjectRule(
            name=self.name,
            parameters=[parameter.convert() for parameter in self.parameters]
        )


class JsonObjectRuleParameterType(StrEnum):
    LITERAL = auto()
    OPTIONAL = auto()
    POSITIONAL = auto()
    UNION = auto()


class JsonObjectRulePositionalParameterValueType(StrEnum):
    INTEGER = auto()
    OBJECT = auto()
    STRING = auto()


class JsonObjectRuleLiteralParameter(BaseModel):
    type: Annotated[
        Literal[JsonObjectRuleParameterType.LITERAL],
        Field(default=JsonObjectRuleParameterType.LITERAL)
    ]

    value: str

    def convert(self) -> ObjectRuleLiteralParameter:
        return ObjectRuleLiteralParameter(value=self.value)


class JsonObjectRuleOptionalParameter(BaseModel):
    type: Annotated[
        Literal[JsonObjectRuleParameterType.OPTIONAL],
        Field(default=JsonObjectRuleParameterType.OPTIONAL)
    ]

    parameters: list[JsonObjectRuleParameter]

    def convert(self) -> ObjectRuleUnionParameter:
        return ObjectRuleUnionParameter(
            members=[
                [parameter.convert() for parameter in self.parameters],
                []
            ]
        )


class JsonObjectRulePositionalParameterIntegerValue(BaseModel):
    type: Annotated[
        Literal[JsonObjectRulePositionalParameterValueType.INTEGER],
        Field(default=JsonObjectRulePositionalParameterValueType.INTEGER)
    ]

    def convert(self) -> ObjectRulePositionalParameterIntegerValue:
        return ObjectRulePositionalParameterIntegerValue()


class JsonObjectRulePositionalParameterObjectValue(JsonObjectRule):
    type: Annotated[
        Literal[JsonObjectRulePositionalParameterValueType.OBJECT],
        Field(default=JsonObjectRulePositionalParameterValueType.OBJECT)
    ]

    def convert(self) -> ObjectRulePositionalParameterObjectValue:
        return ObjectRulePositionalParameterObjectValue(
            name=self.name,
            parameters=[parameter.convert() for parameter in self.parameters]
        )


class JsonObjectRulePositionalParameterStringValue(BaseModel):
    type: Annotated[
        Literal[JsonObjectRulePositionalParameterValueType.STRING],
        Field(default=JsonObjectRulePositionalParameterValueType.STRING)
    ]

    def convert(self) -> ObjectRulePositionalParameterStringValue:
        return ObjectRulePositionalParameterStringValue()


JsonObjectRulePositionalParameterValue = Annotated[
    Union[
        JsonObjectRulePositionalParameterIntegerValue,
        JsonObjectRulePositionalParameterObjectValue,
        JsonObjectRulePositionalParameterStringValue
    ],
    Field(discriminator="type")
]


class JsonObjectRulePositionalParameter(BaseModel):
    type: Annotated[
        Literal[JsonObjectRuleParameterType.POSITIONAL],
        Field(default=JsonObjectRuleParameterType.POSITIONAL)
    ]

    name: str
    value: Annotated[
        list[JsonObjectRulePositionalParameterValue],
        Field(default=[JsonObjectRulePositionalParameterStringValue()])
    ]

    def convert(self) -> ObjectRulePositionalParameter:
        return ObjectRulePositionalParameter(
            name=self.name,
            value=[value.convert() for value in self.value]
        )


class JsonObjectRuleUnionParameter(BaseModel):
    type: Annotated[
        Literal[JsonObjectRuleParameterType.UNION],
        Field(default=JsonObjectRuleParameterType.UNION)
    ]

    members: list[list[JsonObjectRuleParameter]]

    def convert(self) -> ObjectRuleUnionParameter:
        return ObjectRuleUnionParameter(
            members=[
                [parameter.convert() for parameter in member]
                for member in self.members
            ]
        )


JsonObjectRuleParameter = Annotated[
    Union[
        JsonObjectRuleLiteralParameter,
        JsonObjectRuleOptionalParameter,
        JsonObjectRulePositionalParameter,
        JsonObjectRuleUnionParameter
    ],
    Field(discriminator="type")
]


def load(readable: str | IOBase) -> list[JsonObjectRule]:
    stream = StringIO(readable) if isinstance(readable, str) else readable
    data = json.load(stream)
    json_rules = TypeAdapter(list[JsonObjectRule]).validate_python(data)
    converted_rules = [json_rule.convert() for json_rule in json_rules]

    return converted_rules
