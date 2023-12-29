from textwrap import dedent

import asa_config
import asa_config.json_rule


from devtools import pprint


def main():
    rules = asa_config.json_rule.load_all()
    result = asa_config.load(
        dedent(
            """
            object network HST_158.87.185.149
             host 158.87.185.149
             description VLAN1026_GSNI-FFM-SDE-IR-10
            object network HST_158.87.185.148
             host 158.87.185.148
             description defrvep01ir10wm
            object network HST_158.87.185.145
             host 158.87.185.145
             description defrvep02ir10wm
            object network HST_158.98.145.29
             host 158.98.145.29
             description kdepwdc01
            object network HST_158.98.145.39
             host 158.98.145.39
             description kdepwdc02
            object-group network GRP_NET1691403080
             network-object object HST_158.87.185.148
             network-object object HST_158.87.185.149
             network-object object HST_158.87.185.145
            object-group network GRP_NET1691403081
             network-object object HST_158.98.145.29
             network-object object HST_158.98.145.39

            access-list MY_ACL remark CH:aaa;DA:20230807;IM:aaa;RE:aaa;
            access-list MY_ACL remark DE:aaa
            access-list MY_ACL extended permit TCP object-group GRP_NET1691403080 object-group GRP_NET1691403081 object-group GRP_SVCTCP1652862712 log
            access-list MY_ACL extended permit UDP object-group GRP_NET1691403080 object-group GRP_NET1691403081 object-group GRP_SVCUDP1652862713 log
            access-list MY_ACL extended permit TCP object-group GRP_NET1691403080 object-group GRP_NET1691403081 object-group GRP_SVCTCP1652862715 log
            access-list MY_ACL extended permit UDP object-group GRP_NET1691403080 object-group GRP_NET1691403081 object-group GRP_SVCUDP1652862712 log
            access-list MY_ACL extended permit TCP object-group GRP_NET1691403081 object-group GRP_NET1691403080 object-group GRP_SVCTCP1652862712 log
            access-list MY_ACL extended permit UDP object-group GRP_NET1691403081 object-group GRP_NET1691403080 object-group GRP_SVCUDP1652862713 log
            access-list MY_ACL extended permit TCP object-group GRP_NET1691403081 object-group GRP_NET1691403080 object-group GRP_SVCTCP1652862715 log
            access-list MY_ACL extended permit UDP object-group GRP_NET1691403081 object-group GRP_NET1691403080 object-group GRP_SVCUDP1652862712 log
            access-list MY_ACL extended permit UDP object-group GRP_NET1691403080 object-group GRP_IBMSOBOX eq 888 log
            access-list MY_ACL extended permit TCP object-group GRP_NET1691403080 object-group GRP_IBMSOBOX eq 888 log
            access-list MY_ACL extended permit UDP object-group GRP_IBMSOBOX object-group GRP_NET1691403080 eq 888 log
            access-list MY_ACL extended permit TCP object-group GRP_IBMSOBOX object-group GRP_NET1691403080 eq 888 log
            """
        ),
        rules
    )

    pprint(result)


if __name__ == "__main__":
    main()
