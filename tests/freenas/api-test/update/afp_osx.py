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
from functions import OSX_TEST, return_output
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

    # Clean up any leftover items from previous failed AD LDAP or SMB runs
    @classmethod
    def setUpClass(inst):
        PUT("/services/afp/", {"afp_srv_guest": False})
        payload = {"afp_name": AFP_NAME, "afp_path": AFP_PATH}
        DELETE_ALL("/sharing/afp/", payload)
        DELETE("/storage/volume/1/datasets/%s/" % DATASET)
        cmd = 'umount -f "%s"; rmdir "%s"; exit 0;' % (MOUNTPOINT, MOUNTPOINT)
        OSX_TEST(cmd)

    def test_01_Creating_AFP_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    def test_02_Updating_AFP_service(self):
        payload = {"afp_srv_connections_limit": "100"}
        assert PUT("/services/afp/", payload) == 200

    def test_03_Enabling_AFP_service(self):
        payload = {"afp_srv_guest": True, "afp_srv_bindip": ip}
        assert PUT("/services/afp/", payload) == 200

    # Now start the service
    def test_04_Starting_AFP_service(self):
        assert PUT("/services/services/afp/", {"srv_enable": True}) == 200

    def test_05_Checking_to_see_if_AFP_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/afp/", "srv_state") == "RUNNING"

    def test_06_Changing_permissions_on_AFP_PATH(self):
        payload = {"mp_path": AFP_PATH,
                   "mp_acl": "unix",
                   "mp_mode": "777",
                   "mp_user": "root",
                   "mp_group": "wheel"}
        assert PUT("/storage/permission/", payload) == 201

    def test_07_Creating_a_AFP_share_on_AFP_PATH(self):
        payload = {"afp_name": AFP_NAME, "afp_path": AFP_PATH}
        assert POST("/sharing/afp/", payload) == 201

    # Mount share on OSX system and create a test file
    def test_08_Create_mount_point_for_AFP_on_OSX_system(self):
        assert OSX_TEST('mkdir -p "%s"' % MOUNTPOINT) is True

    def test_09_Mount_AFP_share_on_OSX_system(self):
        cmd = 'mount -t afp "afp://%s/%s" "%S"' % (ip, AFP_NAME, MOUNTPOINT)
        assert OSX_TEST(cmd) is True

    # def test_10_Checking_permissions_on_MOUNTPOINT(self):
    #     device_name = return_output('dirname "%s"') % MOUNTPOINT
    #     cmd = 'ls -la "%s" | ' % device_name
    #     cmd += 'awk \'\$4 == "%s" && \$9 == "%s" \' ' % (VOL_GROUP, DATASET)
    #     assert OSX_TEST(cmd) is True

    def test_11_Create_file_on_AFP_share_via_OSX_to_test_permissions(self):
        assert OSX_TEST('touch "%s/testfile.txt"' % MOUNTPOINT) is True

    # Move test file to a new location on the AFP share
    def test_12_Moving_AFP_test_file_into_a_new_directory(self):
        cmd = 'mkdir -p "%s/tmp" && ' % MOUNTPOINT
        cmd += 'mv "%s/testfile.txt" ' % MOUNTPOINT
        cmd += '"%s/tmp/testfile.txt"' % MOUNTPOINT
        assert OSX_TEST(cmd) is True

    # Delete test file and test directory from AFP share
    def test_13_Deleting_test_file_and_directory_from_AFP_share(self):
        cmd = 'rm -f "%s/tmp/testfile.txt" && ' % MOUNTPOINT
        cmd += 'rmdir "%s/tmp"' % MOUNTPOINT
        assert OSX_TEST(cmd) is True

    def test_14_Verifying_test_file_directory_were_successfully_removed(self):
        cmd = 'find -- "%s/" -prune -type d -empty | grep -q .' % MOUNTPOINT
        assert OSX_TEST(cmd) is True

    # Clean up mounted AFP share
    def test_15_Unmount_AFP_share(self):
        assert OSX_TEST('umount -f "%s"' % MOUNTPOINT) is True

    # Test disable AFP
    def test_16_Verify_AFP_service_can_be_disabled(self):
        assert PUT("/services/afp/", {"afp_srv_guest": False}) == 200

    # Test delete AFP dataset
    def test_17_Verify_AFP_dataset_can_be_destroyed(self):
        assert DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204

if __name__ == "__main__":
    unittest.main(verbosity=2)
