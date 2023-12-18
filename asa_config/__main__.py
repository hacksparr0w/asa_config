from ._command import _match
from ._rule import DEFAULT_RULES


def main():
    result = _match(
        ["access-list", "MY_ACL", "extended", "permit", "TCP", "object-group", "GRP_IBMSOBOX", "object-group", "GRP_NET1691403080", "eq", "888", "log"],
        DEFAULT_RULES
    )

    print(result)


if __name__ == "__main__":
    main()
