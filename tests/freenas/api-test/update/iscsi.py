#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, GET_OUTPUT

try:
    from config import BRIDGEHOST
except ImportError:
    exit()

MOUNTPOINT = "/tmp/iscsi" + BRIDGEHOST
DEVICE_NAME_PATH = "/tmp/freenasiscsi"
TARGET_NAME = "iqn.1994-09.freenasqa:target0"


class ad_bsd_test(unittest.TestCase):

    # Clean up any leftover items from previous failed AD LDAP or SMB runs
    @classmethod
    def setUpClass(inst):
        PUT("/services/services/iscsitarget/", {"srv_enable": False})

    # Enable the iSCSI service
    def test_01_Enable_iSCSI_service(self):
        payload = {"srv_enable": True}
        assert PUT("/services/services/iscsitarget/", payload) == 200

    def test_01_Verify_the_iSCSI_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/iscsitarget/",
                          "srv_state") == "RUNNING"

    # Disable the iSCSI service
    def test_01_Disable_iSCSI_service(self):
        payload = {"srv_enable": False}
        assert PUT("/services/services/iscsitarget/", payload) == 200

    def test_01_Verify_the_iSCSI_service_is_Sdisabled(self):
        assert GET_OUTPUT("/services/services/iscsitarget/",
                          "srv_state") == "STOPPED"

if __name__ == "__main__":
    unittest.main(verbosity=2)
