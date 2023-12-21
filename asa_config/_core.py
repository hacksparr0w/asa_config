from pathlib import Path

from ._json_rule import load


__all__ = (
    "DEFAULT_RULES",
)


_DEFAULT_RULE_FILE = (
    Path(__file__).parent.parent / "data" / "default_rules.json"
)

DEFAULT_RULES = load(_DEFAULT_RULE_FILE.read_text())
