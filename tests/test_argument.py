from io import StringIO
from textwrap import dedent

import pytest

from asa_config._argument import CommandArguments, read


@pytest.mark.parametrize(
    "config,expected",
    [
        (
            dedent(
                """
                interface GigabitEthernet1
                 description a bc d
                 ip address
                """
            ),
            [
                CommandArguments(
                    arguments=["interface", "GigabitEthernet1"],
                    subarguments=[
                        CommandArguments(
                            arguments=["description", "a", "bc", "d"],
                            subarguments=[]
                        ),
                        CommandArguments(
                            arguments=["ip", "address"],
                            subarguments=[]
                        )
                    ]
                )
            ],
        ),
        (
            dedent(
                """
                object network HST_1
                 host 158.87.185.149
                 description VLAN1026_GSNI-FFM-SDE-IR-10
                  access-list HST_1_access_in extended permit ip any any
                object network HST_2
                 host 158.87.185.148
                """
            ),
            [
                CommandArguments(
                    arguments=["object", "network", "HST_1"],
                    subarguments=[
                        CommandArguments(
                            arguments=["host", "158.87.185.149"],
                            subarguments=[]
                        ),
                        CommandArguments(
                            arguments=[
                                "description",
                                "VLAN1026_GSNI-FFM-SDE-IR-10"
                            ],
                            subarguments=[
                                CommandArguments(
                                    arguments=[
                                        "access-list",
                                        "HST_1_access_in",
                                        "extended",
                                        "permit",
                                        "ip",
                                        "any",
                                        "any"
                                    ],
                                    subarguments=[]
                                )
                            ]
                        )
                    ]
                ),
                CommandArguments(
                    arguments=["object", "network", "HST_2"],
                    subarguments=[
                        CommandArguments(
                            arguments=["host", "158.87.185.148"],
                            subarguments=[]
                        )
                    ]
                )
            ]
        )
    ]
)
def test_read(
    config: str,
    expected: list[CommandArguments]
) -> None:
    stream = StringIO(config)
    chunks = read(stream)

    assert chunks == expected
