from dataclasses import dataclass


class CommandParseError(Exception):
    pass


class CommandSyntaxError(CommandParseError):
    pass


class Token:
    COMMAND_SEPARATOR = "\n"
    WORD_SEPARATOR = " "
    INDENTATION = " "


@dataclass
class Command:
    keywords: list[str]
    arguments: dict[str, str | "Command"]
    subcommands: list["Command"]
