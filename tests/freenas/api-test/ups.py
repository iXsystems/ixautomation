#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
from functions import PUT

class tftp_test(unittest.TestCase):

    def test_01_Enabling_UPS_Service(self):
        assert PUT("/services/services/ups/" {"srv_enable": True}) == 200

    def test_02_Enabling_Remote_Monitor(self):
        assert PUT("/services/services/ups/", {"ups_rmonitor": True}) == 200

    def test_03_Disabling_Remote_Monitor_option(self):
        assert PUT("/services/services/ups/", {"ups_rmonitor": false}) == 200

    def test_04_Enabling_email_status_update_option(self):
        assert PUT("/services/services/ups/", {"ups_emailnotify": True}) == 200

    def test_05_Disabling_email_status_update_option(self):
        assert PUT("/services/services/ups/", {"ups_emailnotify": False}) == 200

    def test_06_running_UPS_in_Master_Mode(self):
        assert PUT("/services/services/ups/", {"ups_mode": "master"}) == 200

    def test_07_Running_UPS_in_Slave_Mode(self):
        assert PUT("/services/services/ups/", {"ups_mode": "slave"}) == 200

    def test_08_Setting_UPS_shutdown_mode_Battery(self):
        assert PUT("/services/services/ups/", {"ups_shutdown": "batt"}) == 200

    def test_09_Setting_UPS_shutdown_mode_Low_Battery(self):
        assert PUT("/services/services/ups/", {"ups_shutdown": "lowbatt"}) == 200

    def test_10_Disabling_UPS_Service(self):
        assert PUT("/services/services/ups/", {"srv_enable": False}) == 200

    def test_11_Setting_Identifier(self):
        assert PUT("/services/services/ups/", {"ups_identifier": "ups"}) == 200


if __name__ == "__main__":
    unittest.main(verbosity=2)
