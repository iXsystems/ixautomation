#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, POST, GET_OUTPUT

try:
    from config import BRIDGEHOST
except ImportError:
    exit()

MOUNTPOINT = "/tmp/iscsi" + BRIDGEHOST
DEVICE_NAME = "/tmp/freenasiscsi"
TARGET_NAME = "iqn.1994-09.freenasqa:target0"


class iscsi_test(unittest.TestCase):

    def test_01_Clean_up_any_leftover_items(self):
        payload = {"srv_enable": "false"}
        assert PUT("/services/services/iscsitarget/", payload) == 200
        # When BSD_TEST is functional will need to add the code to clean test

    # Add iSCSI initator
    def Test_02_Add_iSCSI_initiator(self):
        payload = {"id": 1,
                   "iscsi_target_initiator_auth_network": "ALL",
                   "iscsi_target_initiator_comment": "",
                   "iscsi_target_initiator_initiators": "ALL",
                   "iscsi_target_initiator_tag": 1}
        assert POST("/services/iscsi/authorizedinitiator/", payload) == 201

    def test_03_Add_ISCSI_portal(self):
        payload = {"iscsi_target_portal_ips": ["0.0.0.0:3620"]}
        assert POST("/services/iscsi/portal/", payload) == 201

    # Add iSCSI target
    def test_04_Add_ISCSI_target(self):
        payload = {"iscsi_target_name": TARGET_NAME}
        assert POST("/services/iscsi/target/", payload) == 201

    # Add Target to groups
    # def test_05_Add_target_to_groups(self):
    #    payload = {"iscsi_target": "1",
    #               "iscsi_target_authgroup": None,
    #               "iscsi_target_portalgroup": 1,
    #               "iscsi_target_initiatorgroup": "1",
    #               "iscsi_target_authtype": "None",
    #               "iscsi_target_initialdigest": "Auto"}

    #    assert POST("/services/iscsi/targetgroup/", payload) == 201

    # Add iSCSI extent
    def test_06_Add_ISCSI_extent(self):
        payload = {"iscsi_target_extent_type": "File",
                   "iscsi_target_extent_name": "extent",
                   "iscsi_target_extent_filesize": "50MB",
                   "iscsi_target_extent_rpm": "SSD",
                   "iscsi_target_extent_path": "/mnt/tank/dataset03/iscsi"}
        assert POST("/services/iscsi/extent/", payload) == 201

    # Associate iSCSI target
    def test_07_Associate_ISCSI_target(self):
        payload = {"id": 1,
                   "iscsi_extent": 1,
                   "iscsi_lunid": None,
                   "iscsi_target": 1}
        assert POST("/services/iscsi/targettoextent/", payload) == 201

    # Enable the iSCSI service
    def test_08_Enable_iSCSI_service(self):
        payload = {"srv_enable": "true"}
        assert PUT("/services/services/iscsitarget/", payload) == 200

    def test_09_Verify_the_iSCSI_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/iscsitarget/",
                          "srv_state") == "RUNNING"

    # when BSD_TEST is functional test using it will need to be added

    # Disable the iSCSI service
    def test_10_Disable_iSCSI_service(self):
        payload = {"srv_enable": "false"}
        assert PUT("/services/services/iscsitarget/", payload) == 200

    def test_11_Verify_the_iSCSI_service_is_disabled(self):
        assert GET_OUTPUT("/services/services/iscsitarget/",
                          "srv_state") == "STOPPED"

if __name__ == "__main__":
    unittest.main(verbosity=2)
