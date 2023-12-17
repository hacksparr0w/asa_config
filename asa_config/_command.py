from ._rule import Literal, Rule, Union


def _find_candidate_rules(
    arguments: list[str],
    rules: list[Rule]
) -> list[Rule]:
    best_matches = []
    best_score = 0

    def evaluate(arguments: list[str], rule: Rule) -> int:
        score = 0

        for argument, parameter in zip(arguments, rule):
            if not isinstance(parameter, Literal):
                return score
            
            if argument != parameter.value:
                return score

            score += 1
        
        return score

    for rule in rules:
        score = evaluate(arguments, rule)

        if score > best_score:
            best_matches = [rule]
            best_score = score
        elif score == best_score:
            best_matches.append(rule)

    return best_matches


def _match_literal(
    argument: str,
    rule: Rule
) -> tuple[Rule, int] | None:
    for index, parameter in enumerate(rule):
        if isinstance(parameter, Literal) and parameter.value == argument:
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


def _has_literal(rule: Rule) -> bool:
    for parameter in rule:
        if isinstance(parameter, Literal):
            return True
        elif isinstance(parameter, Union):
            for member in parameter.members:
                if _has_literal(member):
                    return True

    return False


def _prune_optionals(
    arguments: list[str],
    rule: Rule
) -> Rule:
    result = []

    for parameter in rule:
        if not isinstance(parameter, Union):
            result.append(parameter)
            continue

        members = parameter.members

        if members[-1] != []:
            result.append(parameter)
            continue

        matches = []

        for member in members[:-1]:
            if not _has_literal(member):
                if [] not in matches:
                    matches = [[], *matches]

                matches.append(member)
                continue

            match = _match_literals(arguments, member)
            flattened_member, match_indices = match

            if match_indices:
                matches.append(flattened_member)

        if len(matches) == 1:
            result.append(matches[0])
        elif len(matches) > 1:
            result.append(Union(list(reversed(matches))))

    return result


def _discriminate_rules_by_matching_literals(
    arguments: list[str],
    rules: list[Rule]
) -> tuple[Rule, list[tuple[int, int]]]:
    best_match = None
    best_match_score = 0

    for rule in rules:
        match = _match_literals(arguments, rule)
        match_score = len(match[1])

        if match_score >= best_match_score:
            best_match = match
            best_match_score = match_score

    return best_match


def _parse(arguments: list[str], rules: list[Rule]) -> dict:
    rules = _find_candidate_rules(arguments, rules)

    if not rules:
        raise ValueError("No matching rule found")

    rule, _ = _discriminate_rules_by_matching_literals(
        arguments,
        rules
    )

    rule = _prune_optionals(arguments, rule)
    rule, match_indices = _match_literals(arguments, rule)

    print(rule)
    print(match_indices)
