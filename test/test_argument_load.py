from textwrap import dedent

import pytest

from asa_config._argument import ArgumentGroup
from asa_config._argument_load import load


@pytest.mark.parametrize(
    "input, expected",
    [
        ("", []),
        ("\n  \n\t \n\n", []),
        (
            "access-list MY_ACL remark CH:aaa;DA:20230807;IM:aaa;RE:aaa;",
            [
                ArgumentGroup(
                    root=[
                        "access-list",
                        "MY_ACL",
                        "remark",
                        "CH:aaa;DA:20230807;IM:aaa;RE:aaa;",
                    ],
                    children=[]
                )
            ]
        ),
        (
            dedent(
                """
                object network HST_158.87.185.149
                    host 158.87.185.149
                    description VLAN1026_GSNI-FFM-SDE-IR-10
                """
            ),
            [
                ArgumentGroup(
                    root=[
                        "object",
                        "network",
                        "HST_158.87.185.149"
                    ],
                    children=[
                        ArgumentGroup(
                            root=[
                                "host",
                                "158.87.185.149"
                            ],
                            children=[]
                        ),
                        ArgumentGroup(
                            root=[
                                "description",
                                "VLAN1026_GSNI-FFM-SDE-IR-10"
                            ],
                            children=[]
                        )
                    ]
                )
            ]
        )
    ]
)
def test_load(input, expected):
    result = load(input)

    assert result == expected
