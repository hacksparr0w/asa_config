from __future__ import annotations

from pydantic import BaseModel

from ._argument import ArgumentGroup
from ._io import Readable, get_stream


__all__ = (
    "ArgumentReadError",
    "IndentationError",

    "load"
)


class ArgumentReadError(Exception):
    pass


class IndentationError(ArgumentReadError):
    pass


class _ArgumentEntry(BaseModel):
    arguments: list[str]
    indentation_level: int


def _read_indentation(
    text: str,
    indentation_string: str | None
) -> tuple[int, int, str | None]:
    index = 0
    indentation_level = 0
    indentation_character = indentation_string[0] \
        if indentation_string else None

    whitespaces = ""

    while True:
        current_character = text[index]

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


def _group_entries(
    entries: list[_ArgumentEntry],
    current_indentation_level: int = 0
) -> list[ArgumentGroup]:
    groups = []

    if not entries:
        return groups

    current_entry = entries[0]
    next_entry = None
    children = []

    if not current_entry.indentation_level == current_indentation_level:
        raise ValueError("Indentation mismatch")

    index = 1

    def finalize():
        group = ArgumentGroup(
            root=current_entry.arguments,
            children=_group_entries(
                children,
                current_indentation_level + 1
            )
        )

        groups.append(group)

    while True:
        if index == len(entries):
            finalize()

            return groups

        next_entry = entries[index]

        if next_entry.indentation_level == current_indentation_level:
            finalize()

            children = []
            current_entry = next_entry
            index += 1
        elif next_entry.indentation_level > current_indentation_level:
            children.append(next_entry)

            index += 1
        else:
            raise ValueError("Unexpected indentation level")


def _read_entries(readable: Readable) -> list[_ArgumentEntry]:
    stream = get_stream(readable)
    entries = []

    previous_indentation_level = 0
    previous_indentation_string = None

    while True:
        text = stream.readline()

        if not text:
            break

        if text.isspace():
            continue

        current_indentation_level, index, current_indentation_string = \
            _read_indentation(text, previous_indentation_string)

        if current_indentation_level > previous_indentation_level + 1:
            raise IndentationError

        arguments = text[index:].rstrip().split(" ")

        entry = _ArgumentEntry(
            arguments=arguments,
            indentation_level=current_indentation_level
        )

        entries.append(entry)

        previous_indentation_level = current_indentation_level
        previous_indentation_string = current_indentation_string

    return entries


def load(readable: Readable) -> list[ArgumentGroup]:
    entries = _read_entries(readable)
    groups = _group_entries(entries)

    return groups
