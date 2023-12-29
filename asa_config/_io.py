from io import StringIO, TextIOBase
from typing import Union


__all__ = (
    "Readable",
    "get_stream"
)


Readable = Union[TextIOBase, str]


def get_stream(readable: Readable) -> TextIOBase:
    if isinstance(readable, str):
        return StringIO(readable)

    return readable
