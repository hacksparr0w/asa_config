from __future__ import annotations

from io import IOBase, StringIO
from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated, Literal, Union

import jsonref

from pydantic import BaseModel, Field

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

    "load",
    "load_all",
    "load_file"
)


_DEFAULT_JSON_RULE_DIRECTORY = Path(__file__).parent.parent \
    / "asa_config_rules"


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


def load(
    readable: IOBase | str,
    base_uri: str | None = None
) -> ObjectRule:
    stream = StringIO(readable) if isinstance(readable, str) else readable
    data = jsonref.load(stream, base_uri=base_uri, merge_props=True)
    rule = JsonObjectRule.model_validate(data).convert()

    return rule


def load_file(file: Path) -> ObjectRule:
    with file.open("r", encoding="utf-8") as stream:
        return load(stream, base_uri=file.as_uri())


def load_all(
    directory: Path = _DEFAULT_JSON_RULE_DIRECTORY
) -> list[ObjectRule]:
    if not directory.is_dir() or not directory.exists():
        raise ValueError(f"'{directory}' is not an existing directory")

    files = directory.glob("**/*.json")
    rules = []

    for file in files:
        if file.name.startswith("_"):
            continue

        rule = load_file(file)
        rules.append(rule)

    return rules
