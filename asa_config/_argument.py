from __future__ import annotations

from pydantic import BaseModel


__all__ = (
    "ArgumentGroup",
)


class ArgumentGroup(BaseModel):
    root: list[str]
    children: list[ArgumentGroup]
