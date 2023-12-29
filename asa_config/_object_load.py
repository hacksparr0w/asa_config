from ._argument_load import load as load_argument_groups
from ._io import Readable
from ._object import ObjectGroup
from ._rule import ObjectRule, match_object_group


__all__ = (
    "load",
)


def load(readable: Readable, rules: list[ObjectRule]) -> list[ObjectGroup]:
    argument_groups = load_argument_groups(readable)
    object_groups = [
        match_object_group(group, rules) for group in argument_groups
    ]

    return object_groups
