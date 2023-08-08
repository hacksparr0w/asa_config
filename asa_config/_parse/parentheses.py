from dataclasses import dataclass


Parentheses = tuple[str, str]


PARENTHESES = [
    ("[", "]"),
    ("{", "}"),
    ("<", ">")
]


class Token:
    SPACE = " "


@dataclass
class Literal:
    value: str


@dataclass
class Group:
    parentheses: tuple[str, str]
    children: list["Parameter"]


Parameter = Literal | Group


def parse(
    content: str,
    start_index: int = 0,
    current_parentheses: Parentheses | None = None
) -> tuple[list[Parameter], int]:
    result = []
    buffer = ""
    current_index = start_index

    def complete_literal() -> None:
        nonlocal buffer

        if len(buffer) > 0:
            result.append(Literal(buffer))
            buffer = ""

    if current_parentheses is not None:
        opening_parenthesis, _ = current_parentheses

        if content[current_index] != opening_parenthesis:
            raise ValueError

        current_index += 1

    while current_index < len(content):
        character = content[current_index]

        if character == Token.SPACE:
            complete_literal()
        else:
            matched = False

            for parentheses_candidate in PARENTHESES:
                opening_parenthesis, closing_parenthesis = (
                    parentheses_candidate
                )

                if character == opening_parenthesis:
                    complete_literal()

                    children, current_index = parse(
                        content,
                        current_index,
                        parentheses_candidate
                    )

                    result.append(Group(parentheses_candidate, children))

                    matched = True
                elif character == closing_parenthesis:
                    if current_parentheses is None:
                        raise ValueError

                    if current_parentheses != parentheses_candidate:
                        raise ValueError

                    complete_literal()

                    return result, current_index

            if not matched:
                buffer += character
 
        current_index += 1

    if current_parentheses is not None:
        raise ValueError

    complete_literal()

    return result, current_index - 1
