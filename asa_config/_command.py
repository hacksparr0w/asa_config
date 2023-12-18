from __future__ import annotations

from ._rule import Literal, Parameter, Positional, Rule, Union

from dataclasses import dataclass


class MatchError(Exception):
    pass


class RuleNotFoundError(MatchError):
    pass


class ArgumentError(MatchError):
    pass


class TooManyArgumentsError(ArgumentError):
    pass


class TooFewArgumentsError(ArgumentError):
    pass


@dataclass
class MatchResult:
    rule: Rule
    literals: list[str]
    positionals: dict[str, str | MatchResult]


def _find_candidate_rules(
    arguments: list[str],
    rules: list[Rule]
) -> list[Rule]:    
    def evaluate(rule: Rule) -> int:
        score = 0

        for argument, parameter in zip(arguments, rule):
            if not isinstance(parameter, Literal):
                return score
            
            if argument != parameter.value:
                return score

            score += 1

        return score

    best_matches = []
    best_score = 0

    for rule in rules:
        score = evaluate(rule)

        if score > best_score:
            best_matches = [rule]
            best_score = score
        elif score == best_score:
            best_matches.append(rule)

    return best_matches


def _is_optional(parameter: Parameter) -> bool:
    if not isinstance(parameter, Union):
        return False

    members = parameter.members

    if len(members) != 2:
        return False

    if members[1] != []:
        return False

    for inner in members[0]:
        if not isinstance(inner, Literal | Positional):
            return False

    return True


def _is_flat(rule: Rule) -> bool:
    for parameter in rule:
        if isinstance(parameter, Union) and not _is_optional(parameter):
            return False

    return True


def _match_literal(
    argument: str,
    rule: Rule
) -> tuple[Rule, int] | None:
    for index, parameter in enumerate(rule):
        if isinstance(parameter, Literal):
            if Literal.matches(argument, parameter):
                return rule, index
        elif isinstance(parameter, Union):
            for member in parameter.members:
                match = _match_literal(argument, member)

                if not match:
                    continue

                flattened_rule = [*rule[:index], *match[0], *rule[index + 1:]]
                shifted_index = index + match[1]

                return flattened_rule, shifted_index

    return None


def _match_literals(
    arguments: list[str],
    rule: Rule
) -> tuple[Rule, list[tuple[int, int]]]:
    match_indices = []

    for argument_index, argument in enumerate(arguments):
        match = _match_literal(argument, rule)

        if not match:
            continue

        rule, rule_index = match

        match_indices.append((argument_index, rule_index))

    return rule, match_indices


def _prune_union(
    arguments: list[str],
    union: Union
) -> Rule:
    def _contains_literal(rule: Rule) -> bool:
        for parameter in rule:
            if isinstance(parameter, Literal):
                return True

            if isinstance(parameter, Union):
                if any(map(_contains_literal, parameter.members)):
                    return True

        return False

    members = union.members
    is_optional = members[-1] == []

    matches = []

    if is_optional:
        members = members[:-1]
        matches.append([])

    for member in members:
        if not _contains_literal(member):
            matches.append(member)
            continue

        rule, match_indices = _match_literals(arguments, member)

        if match_indices:
            rule = _prune_unions(arguments, rule)
            matches = [rule]
            break

    assert len(matches) > 0

    if len(matches) == 1:
        return matches[0]

    return [Union(members=list(reversed(matches)))]


def _prune_unions(
    arguments: list[str],
    rule: Rule
) -> Rule:
    result = []

    for parameter in rule:
        if not isinstance(parameter, Union):
            result.append(parameter)
            continue

        result.extend(_prune_union(arguments, parameter))

    return result


def _discriminate_candidate_rule(
    arguments: list[str],
    rule: list[Rule]
) -> bool:
    for parameter in rule:
        if isinstance(parameter, Literal):
            matches = map(
                lambda argument: Literal.matches(argument, parameter),
                arguments
            )

            if not any(matches):
                return False

    return True


def _transform_argument_group(
    argument_group: list[str],
    rules: list[Rule]
) -> list[MatchResult | str]:
    argument_buffer = []
    remaining_arguments = [*argument_group]
    transformed_arguments = []

    while remaining_arguments:
        try:
            match = _match(remaining_arguments, rules)

            transformed_arguments.append(match)

            if argument_buffer:
                remaining_arguments.extend(argument_buffer)
                argument_buffer = []
        except RuleNotFoundError:
            transformed_arguments.append(argument_group[0])
            remaining_arguments.pop(0)
        except TooManyArgumentsError:
            argument = remaining_arguments.pop()
            argument_buffer = [argument, *argument_buffer]

    return transformed_arguments


def _transform_arguments(
    original_arguments: list[str],
    literal_match_indices: list[tuple[int, int]],
    rules: list[Rule]
) -> list[MatchResult | str]:
    def is_literal_index(current_argument_index: int) -> bool:
        for other_argument_index, _ in literal_match_indices:
            if current_argument_index == other_argument_index:
                return True

        return False

    transformed_arguments = []
    current_argument_group = []

    for current_argument_index in range(len(original_arguments)):
        is_last_index = current_argument_index == len(original_arguments) - 1
        argument = original_arguments[current_argument_index]

        if is_literal_index(current_argument_index):
            transformed_arguments.append(argument)
        else:
            current_argument_group.append(argument)

            if is_last_index or is_literal_index(current_argument_index + 1):
                transformed_argument_group = _transform_argument_group(
                    current_argument_group,
                    rules
                )

                transformed_arguments.extend(transformed_argument_group)
                current_argument_group = []

    return transformed_arguments


def _match_positionals(
    arguments: list[MatchResult | str],
    rule: Rule,
    literal_match_indices: list[tuple[int, int]]
) -> MatchResult:
    def get_remaining_required_positionals(current_index: int = 0) -> int:
        total = 0

        for other_index, parameter in enumerate(rule):
            if other_index < current_index:
                continue

            if isinstance(parameter, Positional):
                total += 1

        return total

    if len(rule) < len(arguments):
        raise TooManyArgumentsError

    literals = []
    positionals = {}

    current_argument_index = 0
    current_parameter_index = 0

    available_positionals = len(arguments) - len(literal_match_indices)

    if available_positionals < get_remaining_required_positionals():
        raise TooFewArgumentsError

    while True:
        current_parameter = rule[current_parameter_index]
        current_argument = arguments[current_argument_index]

        if isinstance(current_parameter, Literal):
            assert Literal.matches(current_argument, current_parameter)

            literals.append(current_argument)

            current_parameter_index += 1
            current_argument_index += 1
        elif _is_optional(current_parameter):
            if available_positionals > \
                get_remaining_required_positionals(current_parameter_index):

                name = current_parameter.members[0][0].name
                positionals[name] = current_argument

                current_argument_index += 1

            current_parameter_index += 1
        else:
            positionals[current_parameter.name] = current_argument
            current_parameter_index += 1
            current_argument_index += 1

        if current_parameter_index == len(rule):
            assert current_argument_index == len(arguments)

            break

    return MatchResult(rule, literals, positionals)


def _match(arguments: list[str], rules: list[Rule]) -> MatchResult:
    rules = _find_candidate_rules(arguments, rules)

    if not rules:
        raise RuleNotFoundError

    rules = list(
        filter(
            lambda rule: _discriminate_candidate_rule(arguments, rule),
            rules
        )
    )

    if not rules:
        raise RuleNotFoundError

    print("before prune:")
    print(rules[1])

    rules = list(map(lambda rule: _prune_unions(arguments, rule), rules))

    print("after prune:")
    print(rules[1])

    matches = list(map(lambda rule: _match_literals(arguments, rule), rules))

    for index, (rule, literal_match_indices) in enumerate(matches):
        assert _is_flat(rule)

        is_last_index = index == len(matches) - 1

        transformed_arguments = _transform_arguments(
            arguments,
            literal_match_indices,
            rules
        )

        try:
            return _match_positionals(
                transformed_arguments,
                rule,
                literal_match_indices
            )
        except ArgumentError:
            if is_last_index:
                raise
