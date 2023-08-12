from pathlib import Path
from textwrap import dedent

from ._parse.rule import parse_rules


RULE_DATA_PATH = Path(__file__).parent.parent / "data" / "command_rules.txt"


def main():
    rules = parse_rules(RULE_DATA_PATH.read_text())


if __name__ == "__main__":
    main()
