#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
from functions import PUT, POST, GET_OUTPUT, DELETE, DELETE_ALL
try:
    import config
except NameError:
    pass
else:
    from config import BRIDGEIP, BRIDGEHOST


DATASET = "afp-osx"
AFP_NAME = "My AFP Share"
AFP_PATH = "/mnt/tank/" + DATASET
MOUNTPOINT = "/tmp/afp-osx" + BRIDGEHOST
VOL_GROUP = "qa"

class ad_bsd_test(unittest.TestCase):

    # Clean up any leftover items from previous failed runs
    def test_01_Clean_up_any_leftover_items(self):
        PUT("/services/afp/", {"afp_srv_guest": "false"})
        DELETE_ALL("/sharing/afp/", {"afp_name": AFP_NAME, "afp_path": AFP_PATH})
        DELETE("/storage/volume/1/datasets/%s/" % DATASET)

    def test_02_Creating_AFP_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    def test_03_Enabling_AFP_service(self):
        try:
            BRIDGEIP
        except NameError:
            payload = {"afp_srv_guest": "true" }
        else:
            payload = {"afp_srv_guest": "true",
                       "afp_srv_bindip": BRIDGEIP}
        assert PUT("/services/afp/", payload) == 200

    def test_04_Starting_AFP_service(self):
        assert PUT("/services/services/afp/", {"srv_enable": "true"}) == 200

    def test_05_Checking_to_see_if_AFP_service_is_enabled(self):
        assert GET("/services/services/afp/", "srv_state") == "RUNNING"

    def test_06_Changing_permissions_on_AFP_PATH(self):
        payload = { "mp_path": "'${AFP_PATH}'",
                    "mp_acl": "unix", "mp_mode":
                    "777", "mp_user": "root",
                    "mp_group": "wheel" }
        assert PUT("/storage/permission/", payload) == 201

    def test_07_Creating_a_AFP_share_on_AFP_PATH(self):
        payload = {"afp_name": AFP_NAME,
                   "afp_path": AFP_PATH}
        assert POST("/sharing/afp/", payload) == 201

    # Verify mountability and permissions of AFP share
    #if [ -n "${OSX_HOST}" -a -n "${BRIDGEIP}" ]; then
    #echo_test_title "Poll VM to ensure AFP service is up and running"
    #wait_for_avail_port "548"
    #check_exit_status || return 1

    #echo_test_title "Check to see if AFP can be accessed from OS X"
    #wait_for_afp_from_osx
    #check_exit_status || return 1

    # Mount share on OSX system and create a test file
    #echo_test_title "Create mount-point for AFP on OSX system"
    #osx_test "mkdir -p '${MOUNTPOINT}'"
    #check_exit_status || return 1

    #echo_test_title "Mount AFP share on OSX system"
    #osx_test "mount -t afp 'afp://${BRIDGEIP}/${AFP_NAME}' '${MOUNTPOINT}'"
    #check_exit_status || return 1

    #local device_name=`dirname "${MOUNTPOINT}"`
    #echo_test_title "Checking permissions on ${MOUNTPOINT}"
    #osx_test "ls -la '${device_name}' | awk '\$4 == \"${VOL_GROUP}\" && \$9 == \"${DATASET}\" ' "
    #check_exit_status || return 1

    #echo_test_title "Create file on AFP share via OSX to test permissions"
    #osx_test "touch '${MOUNTPOINT}/testfile.txt'"
    #check_exit_status || return 1

    # Move test file to a new location on the AFP share
    #echo_test_title "Moving AFP test file into a new directory"
    #osx_test "mkdir -p '${MOUNTPOINT}/tmp' && mv '${MOUNTPOINT}/testfile.txt' '${MOUNTPOINT}/tmp/testfile.txt'"
    #check_exit_status || return 1

    # Delete test file and test directory from AFP share
    #echo_test_title "Deleting test file and directory from AFP share"
    #osx_test "rm -f '${MOUNTPOINT}/tmp/testfile.txt' && rmdir '${MOUNTPOINT}/tmp'"
    #check_exit_status || return 1

    #echo_test_title "Verifying that test file and directory were successfully removed"
    #osx_test "find -- '${MOUNTPOINT}/' -prune -type d -empty | grep -q ."
    #check_exit_status || return 1

    ## Clean up mounted AFP share
    #echo_test_title "Unmount AFP share"
    #osx_test "umount -f '${MOUNTPOINT}'"
    #check_exit_status || return 1
    #fi

    # Test disable AFP
    def test_08_Verify_AFP_service_can_be_disabled(self):
        assert PUT("/services/afp/", {"afp_srv_guest": "false"}) == 200

    # Test delete AFP dataset
    def test_09_Verify_AFP_dataset_can_be_destroyed(self):
     assert DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204


if __name__ == "__main__":
    unittest.main(verbosity=2)
