#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
from functions import PUT, POST, GET_OUTPUT, DELETE, DELETE_ALL, OSX_TEST

try:
    import config
except ImportError:
    pass
else:
    from config import BRIDGEHOST





class smarttest_test(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        inst.disk_identifiers = GET_OUTPUT("/storage/disk", "disk_identifier")
        print(inst.disk_identifiers)

    def test_01_Create_a_new_SMARTTest(self):
        payload = {"smarttest_disks": disk_ident_1,
                   "smarttest_type": "L",
                   "smarttest_hour": "*",
                   "smarttest_daymonth": "*",
                   "smarttest_month": "*",
                   "smarttest_dayweek": "*"}
        assert POST("/tasks/smarttest/", payload) == 201
    check_rest_response "201" || return 1

    def test_02_Check_that_API_reports_new_SMARTTest(self):
        assert GET_OUTPUT("/tasks/smarttest/", "smarttest_disks") == disk_ident_1


if __name__ == "__main__":
    unittest.main(verbosity=2)
