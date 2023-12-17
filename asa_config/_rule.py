from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import _parentheses


__all__ = (
    "DEFAULT_RULES",

    "Literal",
    "Parameter",
    "Positional",
    "Union",

    "read"
)


_DEFAULT_RULE_FILE = Path(__file__).parent.parent / "data" / "rules.txt"


@dataclass
class Literal:
    value: str


@dataclass
class Positional:
    name: str


@dataclass
class Union:
    members: list[Rule]


Parameter = (
    Literal
    | Positional
    | Union
)


Rule = list[Parameter]


class _Token:
    LITERAL_PARENTHESES = ("<", ">")
    OPTIONAL_UNION_PARENTHESES = ("[", "]")
    UNION_DELIMITER = "|"
    UNION_PARENTHESES = ("{", "}")


def _convert_literal(literal: _parentheses.Literal) -> Positional:
    return Positional(literal.value)


def _convert_literal_group(group: _parentheses.Group) -> Literal:
    assert len(group.children) == 1

    first_child = group.children[0]

    assert isinstance(first_child, _parentheses.Literal)
    
    return Literal(first_child.value)


def _convert_union_group(
    group: _parentheses.Group,
    optional: bool
) -> Union:
    members = []
    member = []

    for child in group.children:
        if isinstance(child, _parentheses.Literal):
                if child.value == _Token.UNION_DELIMITER:
                    if len(member) == 0:
                        raise ValueError

                    members.append(member)
                    member = []
                    continue

        converted = _convert(child)
        member.append(converted)

    if len(member) == 0:
        raise ValueError

    if len(members) == 0 and not optional:
        raise ValueError

    members.append(member)

    if optional:
        members.append([])

    return Union(members)


def _convert(parameter: _parentheses.Parameter) -> Parameter:
    if isinstance(parameter, _parentheses.Literal):
        return _convert_literal(parameter)

    assert isinstance(parameter, _parentheses.Group)

    if parameter.parentheses == _Token.LITERAL_PARENTHESES:
        return _convert_literal_group(parameter)

    if parameter.parentheses == _Token.UNION_PARENTHESES:
        return _convert_union_group(parameter, False)

    assert parameter.parentheses == _Token.OPTIONAL_UNION_PARENTHESES

    return _convert_union_group(parameter, True)


def _read_rule(content: str) -> Rule:
    return [_convert(p) for p in _parentheses.read(content)[0]]


def read(content: str) -> list[Rule]:
    rules = []

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        rules.append(_read_rule(line))

    return rules


DEFAULT_RULES = read(_DEFAULT_RULE_FILE.read_text())
