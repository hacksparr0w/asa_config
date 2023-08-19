from pathlib import Path

from ._parse.command_rule import parse_rules
from ._parse.command_syntax import generate


RULE_DATA_PATH = Path(__file__).parent.parent / "data" / "command_rules.txt"


def main():
    rules = parse_rules(RULE_DATA_PATH.read_text())
    rule = rules[5]

    i = 0
    for syntax in generate(rule):
        i += 1

    print(i)

if __name__ == "__main__":
    main()
