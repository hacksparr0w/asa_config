from asa_config._object import match
from asa_config.json_rule import load_all

from devtools import pprint


def main():
    rules = load_all()
    result = match(
        ["access-list", "MY_ACL", "extended", "permit", "TCP", "object-group", "GRP_IBMSOBOX", "object-group", "GRP_NET1691403080", "eq", "888", "log"],
        rules
    )

    pprint(result)


if __name__ == "__main__":
    main()
