from textwrap import dedent

import pytest

from asa_config._object_argument import ObjectArguments, read


@pytest.mark.parametrize(
    "input, expected",
    [
        ("", []),
        ("\n  \n\t \n\n", []),
        (
            "access-list MY_ACL remark CH:aaa;DA:20230807;IM:aaa;RE:aaa;",
            [
                ObjectArguments(
                    arguments=[
                        "access-list",
                        "MY_ACL",
                        "remark",
                        "CH:aaa;DA:20230807;IM:aaa;RE:aaa;",
                    ],
                    subarguments=[]
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
                ObjectArguments(
                    arguments=[
                        "object",
                        "network",
                        "HST_158.87.185.149"
                    ],
                    subarguments=[
                        ObjectArguments(
                            arguments=[
                                "host",
                                "158.87.185.149"
                            ],
                            subarguments=[]
                        ),
                        ObjectArguments(
                            arguments=[
                                "description",
                                "VLAN1026_GSNI-FFM-SDE-IR-10"
                            ],
                            subarguments=[]
                        )
                    ]
                )
            ]
        )
    ]
)
def test_read(input, expected):
    result = read(input)

    assert result == expected
