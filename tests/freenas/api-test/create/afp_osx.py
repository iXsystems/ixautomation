#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, POST, GET_OUTPUT, DELETE, DELETE_ALL
from auto_config import ip
try:
    from config import BRIDGEHOST
except ImportError:
    exit()

DATASET = "afp-osx"
AFP_NAME = "My AFP Share"
AFP_PATH = "/mnt/tank/" + DATASET
MOUNTPOINT = "/tmp/afp-osx" + BRIDGEHOST
VOL_GROUP = "qa"


class afp_osx_test(unittest.TestCase):

    # Clean up any leftover items from previous failed runs
    @classmethod
    def setUpClass(inst):
        PUT("/services/afp/", {"afp_srv_guest": "false"})
        payload = {"afp_name": AFP_NAME, "afp_path": AFP_PATH}
        DELETE_ALL("/sharing/afp/", payload)
        DELETE("/storage/volume/1/datasets/%s/" % DATASET)

    def test_01_Creating_AFP_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    def test_02_Enabling_AFP_service(self):
        payload = {"afp_srv_guest": "true",
                   "afp_srv_bindip": ip}
        assert PUT("/services/afp/", payload) == 200

    def test_03_Starting_AFP_service(self):
        assert PUT("/services/services/afp/", {"srv_enable": "true"}) == 200

    def test_04_Checking_to_see_if_AFP_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/afp/", "srv_state") == "RUNNING"

    def test_05_Changing_permissions_on_AFP_PATH(self):
        payload = {"mp_path": AFP_PATH,
                   "mp_acl": "unix", "mp_mode":
                   "777", "mp_user": "root",
                   "mp_group": "wheel"}
        assert PUT("/storage/permission/", payload) == 201

    def test_06_Creating_a_AFP_share_on_AFP_PATH(self):
        payload = {"afp_name": AFP_NAME,
                   "afp_path": AFP_PATH}
        assert POST("/sharing/afp/", payload) == 201

    # Test disable AFP
    def test_15_Verify_AFP_service_can_be_disabled(self):
        assert PUT("/services/afp/", {"afp_srv_guest": "false"}) == 200

    # Test delete AFP dataset
    def test_16_Verify_AFP_dataset_can_be_destroyed(self):
        assert DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204

if __name__ == "__main__":
    unittest.main(verbosity=2)
