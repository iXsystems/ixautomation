#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
from functions import POST, GET_USER


class group_test(unittest.TestCase):

    def test_01_Creating_group_testgroup(self):
        payload = {"bsdgrp_gid": 1200,"bsdgrp_group": "testgroup"}
        assert POST("/account/groups/", payload) == 201

if __name__ == "__main__":
    unittest.main(verbosity=2)
