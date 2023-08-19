from dataclasses import dataclass, replace
from typing import Iterator

from . import command_rule, command_syntax


class ParseError(Exception):
    pass


class Token:
    LINE = "\n"
    SPACE = " "


@dataclass
class Command:
    keywords: list[str]
    arguments: dict[str, str | "Command"]
    subcommands: list["Command"]


@dataclass
class ReadArgument:
    value: str


@dataclass
class ReadIndentation:
    level: int


class ReadCommandSeparator:
    pass


class ReadContentEnd:
    pass


ReadResult = (
    ReadArgument
    | ReadIndentation
    | ReadCommandSeparator
    | ReadContentEnd
)


@dataclass
class ReaderState:
    content: str
    index: int = 0
    buffer: str = ""
    expect_indentation: bool = False


def reader(
    start_state: ReaderState
) -> Iterator[tuple[ReadResult, ReaderState]]:
    current_state = start_state

    while current_state.index < len(current_state.content):
        character = current_state.content[current_state.index]

        if character == Token.LINE:
            if not current_state.expect_command_separator:
                current_state = replace(current_state, buffer="")

    if current_state.buffer:
        yield ReadArgument(current_state.buffer), current_state
        current_state = replace(current_state, buffer="")

    yield ReadContentEnd(), current_state


def parse_next(
    rules: list[command_rule.Rule],
    content: str,
    start_index: int = 0
) -> tuple[Command, int]:



def parse(content: str) -> Command:
    pass
