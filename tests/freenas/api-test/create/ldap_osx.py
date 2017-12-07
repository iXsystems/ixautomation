#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys, os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, POST, GET_OUTPUT, DELETE, DELETE_ALL, return_output
from functions import BSD_TEST
from auto_config import ip

try:
    import config
except ImportError:
    pass
else:
    from config import BRIDGEHOST, BRIDGEDOMAIN, ADPASSWORD, ADUSERNAME
    from config import LDAPBASEDN, LDAPBINDDN, LDAPHOSTNAME, LDAPBINDPASSWORD

DATASET = "ldap-osx"
SMB_NAME = "TestShare"
SMB_PATH = "/mnt/tank/" + DATASET
MOUNTPOINT = "/tmp/ldap-osx" + BRIDGEHOST
VOL_GROUP = "qa"

class ldap_osx_test(unittest.TestCase):
    # Clean up any leftover items from previous failed AD LDAP or SMB runs
    def test_01_Clean_up_any_leftover_items(self):
        #osx_test "umount -f '${MOUNTPOINT}'; rmdir '${MOUNTPOINT}'; exit 0"
        payload1 = {"ad_bindpw": ADPASSWORD,
                   "ad_bindname": ADUSERNAME,
                   "ad_domainname": BRIDGEDOMAIN,
                   "ad_netbiosname_a": BRIDGEHOST,
                   "ad_idmap_backend": "rid",
                   "ad_enable":False}
        PUT("/directoryservice/activedirectory/1/", payload1)
        payload2 = {"ldap_basedn": LDAPBASEDN,
                    "ldap_anonbind": True,
                    "ldap_netbiosname_a": BRIDGEHOST,
                    "ldap_hostname": LDAPHOSTNAME,
                    "ldap_has_samba_schema": True,
                    "ldap_enable": False}
        PUT("/directoryservice/ldap/1/", payload2)
        PUT("/services/services/cifs/", {"srv_enable": False})
        payload3 = {"cfs_comment": "My Test SMB Share",
                    "cifs_path": SMB_PATH,
                    "cifs_name": SMB_NAME,
                    "cifs_guestok": True,
                    "cifs_vfsobjects": "streams_xattr"}
        DELETE_ALL("/sharing/cifs/", payload3)
        DELETE("/storage/volume/1/datasets/%s/" % DATASET)

    # Set auxilary parameters to allow mount_smbfs to work with ldap
    def test_02_Creating_SMB_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    # Enable LDAP
    def test_03_Enabling_LDAP_with_anonymous_bind(self):
        payload = {"ldap_basedn": LDAPBASEDN,
                   "ldap_anonbind": True,
                   "ldap_netbiosname_a": BRIDGEHOST,
                   "ldap_hostname": LDAPHOSTNAME,
                   "ldap_has_samba_schema": True,
                   "ldap_enable": True}
        assert PUT("/directoryservice/ldap/1/", payload) == 200

    # Check LDAP
    def test_04_Checking_LDAP(self):
        assert GET_OUTPUT("/directoryservice/ldap/", "ldap_enable") == True

    def test_05_Enabling_SMB_service(self):
        payload = {"cifs_srv_description": "Test FreeNAS Server",
                   "cifs_srv_guest": "nobody",
                   "cifs_hostname_lookup": False,
                   "cifs_srv_aio_enable": False }
        assert PUT("/services/cifs/",payload) == 200

    # Now start the service
    def test_06_Starting_SMB_service(self):
        assert PUT("/services/services/cifs/", {"srv_enable": True}) == 200

    #echo_test_title "Verifying that SMB service has started"
    #wait_for_avail_port "445"
    #check_exit_status || return 1

    def test_07_Checking_to_see_if_SMB_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "RUNNING"

   # def test_08_Changing_permissions_on_SMB_PATH(self):
   #     payload = {"mp_path": SMB_PATH,
   #                "mp_acl": "unix",
   #                "mp_mode": "777",
   #                "mp_user": "root",
   #                "mp_group": "qa",
   #                "mp_recursive": True}
   #     assert PUT("/storage/permission/", payload) == 201

    def test_09_Creating_a_SMB_share_on_SMB_PATH(self):
        payload = {"cfs_comment": "My Test SMB Share",
                   "cifs_path": SMB_PATH,
                   "cifs_name": SMB_NAME,
                   "cifs_guestok": True,
                   "cifs_vfsobjects": "streams_xattr"}
        assert POST("/sharing/cifs/", payload) == 201


    #local vol_name=$(dirname "${SMB_PATH}")
    #echo_test_title "Checking permissions on ${SMB_NAME}"
    #ssh_test "ls -la '${vol_name}' | awk '\$4 == \"${VOL_GROUP}\" && \$9 == \"${DATASET}\" ' "

    #if [ -n "${OSX_HOST}" -a -n "${BRIDGEIP}" ]; then
    # Mount share on OSX system and create a test file
    #echo_test_title "Create mount-point for SMB on OSX system"
    #osx_test "mkdir -p '${MOUNTPOINT}'"

    #echo_test_title "Mount SMB share on OSX system"
    #osx_test "mount -t smbfs 'smb://ldapuser:12345678@${BRIDGEIP}/${SMB_NAME}' ${MOUNTPOINT}"

    #echo_test_title "Verify SMB share mounted on OSX system"
    #wait_for_osx_mnt "${MOUNTPOINT}"

    #local device_name=`dirname "${MOUNTPOINT}"`
    #echo_test_title "Checking permissions on ${MOUNTPOINT}"
    #osx_test "time ls -la '${device_name}' | awk '\$4 == \"${VOL_GROUP}\" && \$9 == \"${DATASET}\" ' "

    #echo_test_title "Create file on SMB share via OSX to test permissions"
    #osx_test "touch '${MOUNTPOINT}/testfile.txt'"

    # Move test file to a new location on the SMB share
    #echo_test_title "Moving SMB test file into a new directory"
    #osx_test "mkdir -p '${MOUNTPOINT}/tmp' && mv '${MOUNTPOINT}/testfile.txt' '${MOUNTPOINT}/tmp/testfile.txt'"

    # Delete test file and test directory from SMB share
    #echo_test_title "Deleting test file and directory from SMB share"
    #osx_test "rm -f '${MOUNTPOINT}/tmp/testfile.txt' && rmdir '${MOUNTPOINT}/tmp'"

    #echo_test_title "Verifying that test file and directory were successfully removed"
    #osx_test "find -- '${MOUNTPOINT}/' -prune -type d -empty | grep -q ."

    # Clean up mounted SMB share
    #echo_test_title "Unmount SMB share"
    #osx_test "umount -f '${MOUNTPOINT}'"

    # Disable LDAP
    def test_10_Disabling_LDAP_with_anonymous_bind(self):
        payload = {"ldap_basedn": LDAPBASEDN,
                   "ldap_anonbind": True,
                   "ldap_netbiosname_a": BRIDGEHOST,
                   "ldap_hostname": LDAPHOSTNAME,
                   "ldap_has_samba_schema": True,
                   "ldap_enable": False }
        assert PUT("/directoryservice/ldap/1/", payload) == 200

    # Now stop the SMB service
    def test_11_Stopping_SMB_service(self):
        assert PUT("/services/services/cifs/", {"srv_enable": False}) == 200

    # Check LDAP
    def test_12_Verify_LDAP_is_disabled(self):
        assert GET_OUTPUT("/directoryservice/ldap/", "ldap_enable") == False

    def test_13_Verify_SMB_service_is_disabled(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "STOPPED"

    # Check destroying a SMB dataset
    def test_14_Destroying_SMB_dataset(self):
        assert DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204


if __name__ == "__main__":
    unittest.main(verbosity=2)
