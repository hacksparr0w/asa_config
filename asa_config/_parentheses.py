from dataclasses import dataclass


__all__ = (
    "Group",
    "Literal",
    "Parameter",
    "Parentheses",

    "read"
)


_PARENTHESES = (
    ("[", "]"),
    ("{", "}"),
    ("<", ">")
)


Parentheses = tuple[str, str]


@dataclass
class Literal:
    value: str


@dataclass
class Group:
    parentheses: Parentheses
    children: list["Parameter"]


Parameter = Literal | Group


def read(
    content: str,
    start_index: int = 0,
    current_parentheses: Parentheses | None = None
) -> tuple[list[Parameter], int]:
    result = []
    buffer = ""
    current_index = start_index

    def finalize_literal() -> None:
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

        if character == " ":
            finalize_literal()
        else:
            matched = False

            for parentheses_candidate in _PARENTHESES:
                opening_parenthesis, closing_parenthesis = (
                    parentheses_candidate
                )

                if character == opening_parenthesis:
                    finalize_literal()

                    children, current_index = read(
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

                    finalize_literal()

                    return result, current_index

            if not matched:
                buffer += character
 
        current_index += 1

    if current_parentheses is not None:
        raise ValueError

    finalize_literal()

    return result, current_index - 1
