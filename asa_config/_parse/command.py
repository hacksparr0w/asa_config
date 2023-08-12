from . import command_rule


class Token:
    COMMAND_SEPARATOR = "\n"
    WORD_SEPARATOR = " "
    INDENTATION = " "


class Command:
    keywords: list[str]
    arguments: dict[str, str | "Command"]
    subcommands: list["Command"]


def parse_next(
    rules: list[command_rule.Rule],
    content: str,
    start_index: int = 0,
    indentation_level: int = 0
) -> tuple[Command, int]:
    keywords = []
    arguments = {}
    subcommands = []

    buffer = ""
    index = start_index
    indentation_counter = 0

    while True:
        if content[index] == Token.INDENTATION:
            indentation_counter += 1
        else:
            raise ValueError

        index += 1

    while True:


def parse(rules: list[command_rule.Rule], content: str) -> list[Command]:
    pass
