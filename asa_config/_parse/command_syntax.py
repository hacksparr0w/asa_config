from typing import Iterator

from ..utility import find
from . import command_rule


Matchable = command_rule.Literal | command_rule.Positional
Syntax = list[Matchable]


def split(
    union: command_rule.Union
) -> tuple[list[command_rule.Parameter], list[command_rule.Parameter]]:
    if len(union.members) == 2:
        return tuple(union.members)

    return [command_rule.Union(union.members[1:])], union.members[0]


def lift(outer_union: command_rule.Union) -> command_rule.Union:
    def find_indices():
        for member_index, member in enumerate(outer_union.members):
            for parameter_index, parameter in enumerate(member):
                if isinstance(parameter, command_rule.Union):
                    return member_index, parameter_index

        return None

    indices = find_indices()

    if not indices:
        return outer_union

    member_index, parameter_index = indices
    inner_union = outer_union.members[member_index][parameter_index]
    a, b = split(inner_union)
    member = outer_union.members[member_index]
    members = (
        outer_union.members[:member_index]
        + [member[:parameter_index] + a + member[parameter_index + 1:]]
        + [member[:parameter_index] + b + member[parameter_index + 1:]]
        + outer_union.members[member_index + 1:]
    )

    return command_rule.Union(members)


def flatten(union: command_rule.Union) -> command_rule.Union:
    result = union

    while True:
        step = lift(result)

        if step is result:
            return result

        result = step


def generate(
    rule: command_rule.Rule
) -> Iterator[Syntax]:
    if len(rule) == 0:
        yield []
        return

    found = find(lambda x: isinstance(x, command_rule.Union), rule)

    if not found:
        yield [rule]
        return

    index, union = found
    union = flatten(union)

    for member in union.members:
        for rest in generate(rule[index + 1:]):
            yield rule[:index] + member + rest
