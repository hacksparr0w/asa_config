from dataclasses import dataclass

from . import parentheses


@dataclass
class Literal:
    value: str


@dataclass
class Positional:
    name: str


@dataclass
class Union:
    members: list[list["Parameter"]]


Parameter = (
    Literal
    | Positional
    | Union
)


Rule = list[Parameter]


class Token:
    LITERAL_PARENTHESES = ("<", ">")
    OPTIONAL_UNION_PARENTHESES = ("[", "]")
    UNION_DELIMITER = "|"
    UNION_PARENTHESES = ("{", "}")


def conver_positional_literal(literal: parentheses.Literal) -> Positional:
    return Positional(literal.value)


def convert_literal_group(group: parentheses.Group) -> Literal:
    assert len(group.children) == 1

    first_child = group.children[0]

    assert isinstance(first_child, parentheses.Literal)
    
    return Literal(first_child.value)


def convert_union_group(group: parentheses.Group, optional: bool) -> Union:
    members = []
    member = []

    for child in group.children:
        if isinstance(child, parentheses.Literal):
                if child.value == Token.UNION_DELIMITER:
                    if len(member) == 0:
                        raise ValueError

                    members.append(member)
                    member = []
                    continue

        converted = convert(child)
        member.append(converted)

    if len(member) == 0:
        raise ValueError

    if len(members) == 0 and not optional:
        raise ValueError

    members.append(member)

    if optional:
        members.append([])

    return Union(members)


def convert(parameter: parentheses.Parameter) -> Parameter:
    if isinstance(parameter, parentheses.Literal):
        return conver_positional_literal(parameter)

    assert isinstance(parameter, parentheses.Group)

    if parameter.parentheses == Token.LITERAL_PARENTHESES:
        return convert_literal_group(parameter)

    if parameter.parentheses == Token.UNION_PARENTHESES:
        return convert_union_group(parameter, False)

    assert parameter.parentheses == Token.OPTIONAL_UNION_PARENTHESES

    return convert_union_group(parameter, True)


def parse_rule(content: str) -> Rule:
    return [convert(p) for p in parentheses.parse(content)[0]]


def parse_rules(content: str) -> list[Rule]:
    rules = []

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        rules.append(parse_rule(line))

    return rules
