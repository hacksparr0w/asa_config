from ._core import DEFAULT_RULES
from ._rule import match

from devtools import pprint


def main():
    # print(DEFAULT_RULES)
    result = match(
        ["access-list", "MY_ACL", "extended", "permit", "TCP", "object-group", "GRP_IBMSOBOX", "object-group", "GRP_NET1691403080", "eq", "888", "log"],
        DEFAULT_RULES
    )

    pprint(result)


if __name__ == "__main__":
    main()
