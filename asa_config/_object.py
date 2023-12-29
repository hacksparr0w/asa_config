from __future__ import annotations

from collections import OrderedDict
from typing import Any

from pydantic import BaseModel


__all__ = (
    "Object",
    "ObjectGroup"
)


class Object(BaseModel):
    name: str
    properties: OrderedDict[str, Any]


class ObjectGroup(BaseModel):
    root: Object
    children: list[ObjectGroup]
