#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, GET_OUTPUT, BSD_TEST
from auto_config import ip
try:
    from config import BRIDGEHOST
except ImportError:
    exit()

MOUNTPOINT = "/tmp/iscsi" + BRIDGEHOST
DEVICE_NAME_PATH = "/tmp/freenasiscsi"
TARGET_NAME = "iqn.1994-09.freenasqa:target0"


class iscsi_test(unittest.TestCase):

    # Clean up any leftover items from previous failed AD LDAP or SMB runs
    @classmethod
    def setUpClass(inst):
        PUT("/services/services/iscsitarget/", {"srv_enable": False})
        BSD_TEST("iscsictl -R -t ${TARGET_NAME}")
        BSD_TEST("umount -f \"${MOUNTPOINT}\" &>/dev/null")
        BSD_TEST("rmdir \"${MOUNTPOINT}\" &>/dev/null")

    # Enable the iSCSI service
    def test_01_Enable_iSCSI_service(self):
        payload = {"srv_enable": True}
        assert PUT("/services/services/iscsitarget/", payload) == 200

    def test_02_Verify_the_iSCSI_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/iscsitarget/",
                          "srv_state") == "RUNNING"

    # Now connect to iSCSI target
    def test_03_Connecting_to_iSCSI_target(self):
        # loop_cnt = 0
        # while [ $loop_cnt -le 6 ] ; do
        BSD_TEST('iscsictl -A -p %s:3620 -t %s' % (ip, TARGET_NAME)) is True
        #     if [ $? -eq 0 ] ; then
        #         echo_ok
        #         break
        #     loop_cnt=$(expr $loop_cnt + 1)
        #     [ $loop_cnt -gt 6 ] && echo_fail && return 1
        #     sleep 3

    def test_04_Waiting_for_iscsi_connection_before_grabbing_device_name(self):
        # loop_cnt = 0
        # while [ $loop_cnt -le 12 ] ; do
        BSD_TEST('iscsictl -L') is True
        #     iscsi_state=$(cat /tmp/.bsdCmdTestStdOut | awk '$2 == "'${BRIDGEIP}':3620" {print $3}')
        #     iscsi_dev=$(cat /tmp/.bsdCmdTestStdOut | awk '$2 == "'${BRIDGEIP}':3620" {print $4}')

        #     if [ -n "${iscsi_state}" -a "${iscsi_state}" == "Connected:" ] ; then
        #         if [ -n "${iscsi_dev}" ] ; then
        #             DEVICE_NAME=$iscsi_dev
        #             echo -n " using \"${DEVICE_NAME}\""
        #             echo_ok && break
        #         else
        #             echo -n "... connected with no device"


        #     loop_cnt=$(expr $loop_cnt + 1)
        #     [ $loop_cnt -gt 12 ] && echo_fail && return 1
        #     echo -n "."
        #     sleep 3

    # Now check if we can mount target create, rename, copy, delete, umount
    def test_05_Creating_iSCSI_mountpoint(self):
        BSD_TEST('mkdir -p "%s"' % MOUNTPOINT) is True

    def test_06_Mount_the_target_volume(self):
        BSD_TEST('mount "/dev/%s" "%s"' % (DEVICE_NAME, MOUNTPOINT)) is True

    def test_07_Creating_45MB_file_to_verify_vzol_size_increase(self):
        BSD_TEST('dd if=/dev/zero of=/tmp/45Mfile.img bs=1M count=45') is True

    def test_08_Moving_45MB_file_to_verify_vzol_size_increase(self):
        BSD_TEST('mv /tmp/45Mfile.img "/testfile1"' % MOUNTPOINT) is True

    def test_09_Deleting_file(self):
        BSD_TEST('rm "%s/testfile1"' % MOUNTPOINT) is True

    def test_10_Unmounting_iSCSI_volume(self):
        BSD_TEST('umount -f "%s"' % MOUNTPOINT) is True

    def test_11_Removing_iSCSI_volume_mountpoint(self):
        BSD_TEST('rmdir "%s"' % MOUNTPOINT) is True

    def test_12_Disconnect_iSCSI_target(self):
        BSD_TEST('iscsictl -R -t %s' % TARGET_NAME) is True

    # Disable the iSCSI service
    def test_13_Disable_iSCSI_service(self):
        payload = {"srv_enable": False}
        assert PUT("/services/services/iscsitarget/", payload) == 200

    def test_14_Verify_the_iSCSI_service_is_Sdisabled(self):
        assert GET_OUTPUT("/services/services/iscsitarget/",
                          "srv_state") == "STOPPED"

if __name__ == "__main__":
    unittest.main(verbosity=2)
