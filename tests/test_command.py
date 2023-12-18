import pytest

from asa_config._command import _prune_unions
from asa_config._rule import Literal, Positional, Union


@pytest.mark.parametrize(
    "arguments, rule, expected",
    (
        (
            [
                "access-list",
                "MY_ACL",
                "extended",
                "permit",
                "TCP",
                "object-group",
                "GRP_IBMSOBOX",
                "object-group",
                "GRP_NET1691403080",
                "eq",
                "888",
                "log"
            ],
            [
                Literal(value="access-list"),
                Positional(name="access_list_name"),
                Union(
                    members=[
                        [
                            Literal(value="line"),
                            Positional(name="line_number")
                        ],
                        []
                    ]
                ),
                Literal(value="extended"),
                Union(
                    members=[
                        [Literal(value="deny")],
                        [Literal(value="permit")]
                    ]
                ),
                Union(
                    members=[
                        [Literal(value="tcp")],
                        [Literal(value="udp")],
                        [Literal(value="sctp")]
                    ]
                ),
                Union(members=[[Positional(name="user_argument")], []]),
                Union(
                    members=[
                        [Positional(name="security_group_argument")],
                        []
                    ]
                ),
                Positional(name="source_address_argument"),
                Union(
                    members=[
                        [Positional(name="source_port_argument")],
                        []
                    ]
                ),
                Union(
                    members=[
                        [Positional(name="security_group_argument")],
                        []
                    ]
                ),
                Positional(name="dest_address_argument"),
                Union(
                    members=[[Positional(name="dest_port_argument")], []]
                ),
                Union(
                    members=[
                        [
                            Literal(value="log"),
                            Union(
                                members=[
                                    [
                                        Union(
                                            members=[
                                                [Positional(name="level")],
                                                []
                                            ]
                                        ),
                                        Union(
                                            members=[
                                                [
                                                    Literal(value="interval"),
                                                    Positional(name="secs")
                                                ],
                                                []
                                            ]
                                        )
                                    ],
                                    [Literal(value="disable")],
                                    [Literal(value="default")],
                                    []
                                ]
                            )
                        ],
                        []
                    ]
                ),
                Union(
                    members=[
                        [
                            Literal(value="time-range"),
                            Positional(name="time_range_name")
                        ],
                        []
                    ]
                ),
                Union(members=[[Literal(value="inactive")], []])
            ],
            [
                Literal(value="access-list"),
                Positional(name="access_list_name"),
                Literal(value="extended"),
                Literal(value="permit"),
                Literal(value="tcp"),
                Union(members=[[Positional(name="user_argument")], []]),
                Union(
                    members=[
                        [Positional(name="security_group_argument")],
                        []
                    ]
                ),
                Positional(name="source_address_argument"),
                Union(
                    members=[
                        [Positional(name="source_port_argument")],
                        []
                    ]
                ),
                Union(
                    members=[
                        [Positional(name="security_group_argument")],
                        []
                    ]
                ),
                Positional(name="dest_address_argument"),
                Union(
                    members=[[Positional(name="dest_port_argument")], []]
                ),
                Literal(value="log")
            ]
        ),
    )
)
def test_prune_unions(arguments, rule, expected) -> None:
    result = _prune_unions(arguments, rule)

    print(result)

    assert result == expected
