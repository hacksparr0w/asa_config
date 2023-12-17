from __future__ import annotations

from dataclasses import dataclass
from io import TextIOBase

from ._error import FormatError


__all__ = (
    "CommandArguments",
    "IndentationError",

    "read"
)


class IndentationError(FormatError):
    pass


@dataclass
class _CommandArgumentChunk:
    indentation_level: int
    arguments: list[str]


_CommandArgumentChunkReadResult = tuple[_CommandArgumentChunk, bool]


@dataclass
class CommandArguments:
    arguments: list[str]
    subarguments: list[CommandArguments]


def _read_command_argument_chunk(
    stream: TextIOBase,
    previous_indentation_level: int
) -> _CommandArgumentChunkReadResult:
    while True:
        line = stream.readline()

        if not line:
            return (None, True)

        line = line[:-1]

        if not line:
            previous_indentation_level = 0
            continue

        arguments = line.split(" ")
        index = 0
        indentation_level = 0

        while arguments[index] == "":
            index += 1
            indentation_level += 1

        arguments = arguments[index:]
        arguments = [
            argument for argument in arguments if not argument.isspace()
        ]

        if not arguments:
            previous_indentation_level = 0
            continue

        if indentation_level > previous_indentation_level + 1:
            raise IndentationError

        return (_CommandArgumentChunk(indentation_level, arguments), False)


def _read_command_argument_chunks(
    stream: TextIOBase
) -> list[_CommandArgumentChunk]:
    previous_indentation_level = 0
    chunks = []

    while True:
        chunk, eof = _read_command_argument_chunk(
            stream,
            previous_indentation_level
        )

        if eof:
            break

        previous_indentation_level = chunk.indentation_level
        chunks.append(chunk)

    return chunks


def _group_command_argument_chunks(
    chunks: list[_CommandArgumentChunk],
    current_indentation_level: int
) -> list[CommandArguments]:
    result = []

    if not chunks:
        return result

    current_chunk = chunks[0]
    next_chunk = None
    subchunks = []

    if not current_chunk.indentation_level == current_indentation_level:
        raise ValueError("Indentation mismatch")

    index = 1

    def finalize():
        arguments = CommandArguments(
            current_chunk.arguments,
            _group_command_argument_chunks(
                subchunks,
                current_indentation_level + 1
            )
        )

        result.append(arguments)

    while True:
        if index == len(chunks):
            finalize()

            break

        next_chunk = chunks[index]

        if next_chunk.indentation_level == current_indentation_level:
            finalize()

            subchunks = []
            current_chunk = next_chunk
            index += 1

            continue

        if next_chunk.indentation_level > current_indentation_level:
            subchunks.append(next_chunk)

            index += 1

            continue

    return result


def read(stream: TextIOBase) -> list[CommandArguments]:
    chunks = _read_command_argument_chunks(stream)
    arguments = _group_command_argument_chunks(chunks, 0)

    return arguments
