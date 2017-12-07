#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
from functions import SSH_TEST
from auto_config import ip
alert_msg = "Testing system alerts with failure."
alert_status = "FAIL"
alert_file = "/tmp/self-test-alert"
class ad_bsd_test(unittest.TestCase):
    def test_01_Create_an_alert_on_the_remote_system(self):
        cmd = "echo '[%s] %s' >> %s" % (alert_status, alert_msg, alert_file)
        assert SSH_TEST(cmd) == True


if __name__ == "__main__":
    unittest.main(verbosity=2)
