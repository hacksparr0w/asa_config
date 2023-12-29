from __future__ import annotations

from io import StringIO, TextIOBase

from pydantic import BaseModel


class ObjectArgumentReadError(Exception):
    pass


class IndentationError(ObjectArgumentReadError):
    pass


class ObjectArguments(BaseModel):
    arguments: list[str]
    subarguments: list[ObjectArguments]


class _ObjectArgumentChunk(BaseModel):
    arguments: list[str]
    indentation_level: int


def _read_indentation(
    line: str,
    indentation_string: str | None
) -> tuple[int, int, str | None]:
    index = 0
    indentation_level = 0
    indentation_character = indentation_string[0] \
        if indentation_string else None

    whitespaces = ""

    while True:
        current_character = line[index]

        if current_character not in (" ", "\t"):
            break

        if indentation_character is None:
            indentation_character = current_character
        else:
            if current_character != indentation_character:
                raise IndentationError

        whitespaces += current_character
        index += 1

    if not whitespaces:
        return 0, index, None

    if indentation_string is None:
        return 1, index, whitespaces

    indentation_level = len(whitespaces) // len(indentation_string)
    remainder = len(whitespaces) % len(indentation_string)

    if remainder != 0:
        raise IndentationError

    return indentation_level, index, indentation_string


def _group_chunks(
    chunks: list[_ObjectArgumentChunk],
    current_indentation_level: int = 0
) -> list[ObjectArguments]:
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
        arguments = ObjectArguments(
            arguments=current_chunk.arguments,
            subarguments=_group_chunks(
                subchunks,
                current_indentation_level + 1
            )
        )

        result.append(arguments)

    while True:
        if index == len(chunks):
            finalize()

            return result

        next_chunk = chunks[index]

        if next_chunk.indentation_level == current_indentation_level:
            finalize()

            subchunks = []
            current_chunk = next_chunk
            index += 1

            continue
        elif next_chunk.indentation_level > current_indentation_level:
            subchunks.append(next_chunk)

            index += 1

            continue
        else:
            raise ValueError("Unexpected indentation level")


def read(readable: TextIOBase | str) -> list[ObjectArguments]:
    stream = StringIO(readable) if isinstance(readable, str) else readable
    chunks = []

    previous_indentation_level = 0
    previous_indentation_string = None

    while True:
        line = stream.readline()

        if not line:
            break

        if line.isspace():
            continue

        current_indentation_level, index, current_indentation_string = \
            _read_indentation(line, previous_indentation_string)

        if current_indentation_level > previous_indentation_level + 1:
            raise IndentationError

        arguments = line[index:].rstrip().split(" ")

        chunk = _ObjectArgumentChunk(
            arguments=arguments,
            indentation_level=current_indentation_level
        )

        chunks.append(chunk)

        previous_indentation_level = current_indentation_level
        previous_indentation_string = current_indentation_string

    return _group_chunks(chunks)
