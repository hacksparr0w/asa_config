from __future__ import annotations

from enum import StrEnum, auto
from io import IOBase, StringIO
from pathlib import Path
from typing import Annotated, Union, Literal

import jsonref

from pydantic import BaseModel, Field

from ._object import (
    IntegerRule,
    LiteralRule,
    ObjectRule,
    ObjectRuleProperty,
    OptionalRule,
    StringRule,
    TupleRule,
    UnionRule
)


_DEFAULT_JSON_OBJECT_RULE_DIRECTORY = Path(__file__).parent.parent \
    / "object_rules"

_JSON_RULE_TYPE_ALIAS = "$type"


class JsonRuleType(StrEnum):
    INTEGER = auto()
    LITERAL = auto()
    OBJECT = auto()
    OPTIONAL = auto()
    STRING = auto()
    TUPLE = auto()
    UNION = auto()


class JsonIntegerRule(BaseModel):
    type: Annotated[
        Literal[JsonRuleType.INTEGER],
        Field(
            alias=_JSON_RULE_TYPE_ALIAS,
            default=JsonRuleType.INTEGER
        )
    ]

    def convert(self) -> ObjectRule:
        return IntegerRule()


class JsonLiteralRule(BaseModel):
    type: Annotated[
        Literal[JsonRuleType.LITERAL],
        Field(
            alias=_JSON_RULE_TYPE_ALIAS,
            default=JsonRuleType.LITERAL
        )
    ]

    value: str

    def convert(self) -> ObjectRule:
        return LiteralRule(value=self.value)


class JsonObjectRuleProperty(BaseModel):
    name: str
    value: JsonRule

    def convert(self) -> ObjectRuleProperty:
        return ObjectRuleProperty(
            name=self.name,
            value=self.value.convert()
        )


class JsonObjectRule(BaseModel):
    type: Annotated[
        Literal[JsonRuleType.OBJECT],
        Field(
            alias=_JSON_RULE_TYPE_ALIAS,
            default=JsonRuleType.OBJECT
        )
    ]

    name: str
    properties: list[JsonObjectRuleProperty]
    subobjects: list[JsonObjectRule] = []

    def convert(self) -> ObjectRule:
        return ObjectRule(
            name=self.name,
            properties=[prop.convert() for prop in self.properties],
            subobjects=[rule.convert() for rule in self.subobjects]
        )


class JsonOptionalRule(BaseModel):
    type: Annotated[
        Literal[JsonRuleType.OPTIONAL],
        Field(
            alias=_JSON_RULE_TYPE_ALIAS,
            default=JsonRuleType.OPTIONAL
        )
    ]

    value: JsonRule

    def convert(self) -> ObjectRule:
        return OptionalRule(self.value.convert())


class JsonStringRule(BaseModel):
    type: Annotated[
        Literal[JsonRuleType.STRING],
        Field(
            alias=_JSON_RULE_TYPE_ALIAS,
            default=JsonRuleType.STRING
        )
    ]

    def convert(self) -> ObjectRule:
        return StringRule()


class JsonTupleRule(BaseModel):
    type: Annotated[
        Literal[JsonRuleType.TUPLE],
        Field(
            alias=_JSON_RULE_TYPE_ALIAS,
            default=JsonRuleType.TUPLE
        )
    ]

    values: list[JsonRule]

    def convert(self) -> ObjectRule:
        return TupleRule(values=[rule.convert() for rule in self.values])


class JsonUnionRule(BaseModel):
    type: Annotated[
        Literal[JsonRuleType.UNION],
        Field(
            alias=_JSON_RULE_TYPE_ALIAS,
            default=JsonRuleType.UNION
        )
    ]

    values: list[JsonRule]

    def convert(self) -> ObjectRule:
        return UnionRule(values=[rule.convert() for rule in self.values])


JsonRule = Annotated[
    Union[
        JsonIntegerRule,
        JsonLiteralRule,
        JsonObjectRule,
        JsonOptionalRule,
        JsonStringRule,
        JsonTupleRule,
        JsonUnionRule
    ],
    Field(discriminator="type")
]


def load(
    readable: IOBase | str,
    base_uri: str | None = None
) -> ObjectRule:
    stream = StringIO(readable) if isinstance(readable, str) else readable
    data = jsonref.load(stream, base_uri=base_uri)
    rule = JsonObjectRule.model_validate(data).convert()

    return rule


def load_file(file: Path) -> ObjectRule:
    with file.open("r", encoding="utf-8") as stream:
        return load(stream, base_uri=file.as_uri())


def load_all(
    directory: Path = _DEFAULT_JSON_OBJECT_RULE_DIRECTORY
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
