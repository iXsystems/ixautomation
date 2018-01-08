#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, POST, GET_OUTPUT, BSD_TEST
from auto_config import ip

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
        BSD_TEST("iscsictl -R -t TARGET_NAME" % TARGET_NAME)
        BSD_TEST('umount -f "%s" &>/dev/null' % MOUNTPOINT)
        BSD_TEST('rmdir "%s" &>/dev/null' % MOUNTPOINT)

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
    # Now connect to iSCSI target
    def test_10_Connecting_to_iSCSI_target(self):
        cmd = 'iscsictl -A -p %s:3620 -t %s' % (ip, TARGET_NAME)
        assert BSD_TEST(cmd) is True

    def test_11_Waiting_for_iscsi_connection_before_grabbing_device_name(self):
        # local loop_cnt = 0
        # while [ $loop_cnt -le 12 ] ; do
        assert BSD_TEST("iscsictl -L") is True
        #    iscsi_state=$(cat /tmp/.bsdCmdTestStdOut | awk '$2 == "'${BRIDGEIP}':3620" {print $3}')
        #    iscsi_dev=$(cat /tmp/.bsdCmdTestStdOut | awk '$2 == "'${BRIDGEIP}':3620" {print $4}')

        # if [ -n "${iscsi_state}" -a "${iscsi_state}" == "Connected:" ]:
        #    if [ -n "${iscsi_dev}" ] ; then
        #        DEVICE_NAME=$iscsi_dev
        #        echo -n " using \"${DEVICE_NAME}\""
        #        echo_ok && break
        #    else:
        #        echo -n "... connected with no device"
        #    loop_cnt=$(expr $loop_cnt + 1)
        #    [ $loop_cnt -gt 12 ] && echo_fail && return 1
        #    echo -n "."
        #    sleep 3
        # done

    def test_12_Format_the_target_volume(self):
        assert BSD_TEST('newfs "/dev/%s"' % DEVICE_NAME) is True

    def test_13_Creating_iSCSI_mountpoint(self):
        assert BSD_TEST('mkdir -p "%s"' % MOUNTPOINT) is True

    def test_14_Mount_the_target_volume(self):
        cmd = 'mount "/dev/%s" "%s"' % (DEVICE_NAME, MOUNTPOINT)
        assert BSD_TEST(cmd) is True

    def test_15_Creating_file(self):
        cmd = 'touch "%s/testfile"' % MOUNTPOINT
        # The line under doesn't make sence
        # "umount '${MOUNTPOINT}'; rmdir '${MOUNTPOINT}'"
        assert BSD_TEST(cmd) is True

    def test_16_Moving_file(self):
        cmd = 'mv "%s/testfile" "%s/testfile2"' % (MOUNTPOINT, MOUNTPOINT)
        assert BSD_TEST(cmd) is True

    def test_17_Copying_file(self):
        cmd = 'cp "%s/testfile2" "%s/testfile"' % (MOUNTPOINT, MOUNTPOINT)
        assert BSD_TEST(cmd) is True

    def test_18_Deleting_file(self):
        assert BSD_TEST('rm "%s/testfile2"' % MOUNTPOINT) is True

    def test_19_Unmounting_iSCSI_volume(self):
        assert BSD_TEST('umount "%s"' % MOUNTPOINT) is True

    def test_20_Removing_iSCSI_volume_mountpoint(self):
        assert BSD_TEST('rmdir "%s"' % MOUNTPOINT) is True

    def test_21_Disconnect_all_targets(self):
        assert BSD_TEST('iscsictl -R -t %s' % TARGET_NAME) is True

    # Disable the iSCSI service
    def test_22_Disable_iSCSI_service(self):
        payload = {"srv_enable": "false"}
        assert PUT("/services/services/iscsitarget/", payload) == 200

    def test_23_Verify_the_iSCSI_service_is_disabled(self):
        assert GET_OUTPUT("/services/services/iscsitarget/",
                          "srv_state") == "STOPPED"

if __name__ == "__main__":
    unittest.main(verbosity=2)
