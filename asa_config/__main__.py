from pathlib import Path
from pprint import pprint

from ._parse.command_rule import parse_rules


RULE_DATA_PATH = Path(__file__).parent.parent / "data" / "command_rules.txt"


def main():
    rules = parse_rules(RULE_DATA_PATH.read_text())
    pprint(rules)


if __name__ == "__main__":
    main()
