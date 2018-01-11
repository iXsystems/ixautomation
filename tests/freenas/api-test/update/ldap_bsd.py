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
from Functions import BSD_TEST,

try:
    from config import BRIDGEHOST, BRIDGEDOMAIN, ADPASSWORD, ADUSERNAME
    from config import LDAPBASEDN, LDAPHOSTNAME, LDAPHOSTNAME2
    from config import LDAPBASEDN2, LDAPBINDDN2, LDAPBINDPASSWORD2
except ImportError:
    exit()

DATASET = "ldap-bsd"
SMB_NAME = "TestShare"
SMB_PATH = "/mnt/tank/" + DATASET
MOUNTPOINT = "/tmp/ldap-bsd" + BRIDGEHOST
LDAP_USER = 'ldapuser'
VOL_GROUP = "qa"


class ldap_bsd_test(unittest.TestCase):

    # Clean up any leftover items from previous failed AD LDAP or SMB runs
    @classmethod
    def setUpClass(inst):
        # Clean up any leftover items from previous failed AD LDAP or SMB runs
        payload1 = {"ad_bindpw": ADPASSWORD,
                    "ad_bindname": ADUSERNAME,
                    "ad_domainname": BRIDGEDOMAIN,
                    "ad_netbiosname_a": BRIDGEHOST,
                    "ad_idmap_backend": "rid",
                    "ad_enable": "false"}
        PUT("/directoryservice/activedirectory/1/", payload1)
        payload2 = {"ldap_basedn": LDAPBASEDN,
                    "ldap_anonbind": False,
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
        cmd = 'umount -f "%s" &>/dev/null; ' % MOUNTPOINT
        cmd += 'rmdir "%s" &>/dev/null' % MOUNTPOINT
        BSD_TEST(cmd)

    # Set auxilary parameters to allow mount_smbfs to work with ldap
    def test_01_Creating_SMB_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    # Enable LDAP
    def test_02_Enabling_LDAPd(self):
        payload = {"ldap_basedn": LDAPBASEDN2,
                   "ldap_binddn": LDAPBINDDN2,
                   "ldap_bindpw": LDAPBINDPASSWORD2,
                   "ldap_netbiosname_a": BRIDGEHOST,
                   "ldap_hostname": LDAPHOSTNAME2,
                   "ldap_has_samba_schema": True,
                   "ldap_enable": True}
        assert PUT("/directoryservice/ldap/1/", payload) == 200

    # Check LDAP
    def test_03_Checking_LDAPd(self):
        assert GET_OUTPUT("/directoryservice/ldap/", "ldap_enable") is True

    def test_04_Enabling_SMB_service(self):
        payload = {"cifs_srv_description": "Test FreeNAS Server",
                   "cifs_srv_guest": "nobody",
                   "cifs_hostname_lookup": False,
                   "cifs_srv_aio_enable": False}
        assert PUT("/services/cifs/", payload) == 200

    # Now start the service
    def test_05_Starting_SMB_service(self):
        assert PUT("/services/services/cifs/", {"srv_enable": True}) == 200

    def test_06_Checking_to_see_if_SMB_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "RUNNING"

    def test_07_Changing_permissions_on_SMB_PATH(self):
        payload = {"mp_path": SMB_PATH,
                   "mp_acl": "unix",
                   "mp_mode": "777",
                   "mp_user": "root",
                   "mp_group": "wheel",
                   "mp_recursive": True}
        assert PUT("/storage/permission/", payload) == 200

    def test_08_Creating_a_SMB_share_on_SMB_PATH(self):
        payload = {"mp_path": SMB_PATH,
                   "mp_acl": "unix",
                   "mp_mode": "777",
                   "mp_user": "root",
                   "mp_group": "wheel",
                   "mp_recursive": True}
        assert POST("/sharing/cifs/", payload) == 201

    # Now check if we can mount SMB / create / rename / copy / delete / umount
    def test_09_Creating_SMB_mountpoint(self):
        assert BSD_TEST('mkdir -p "%s" && sync' % MOUNTPOINT) is True

    # The LDAPUSER user must exist in LDAP with this password
    def test_09_Store_LDAP_credentials_in_file_for_mount_smbfs(self):
        cmd = 'echo "[TESTNAS:LDAPUSER]" > ~/.nsmbrc && '
        cmd += 'echo "password=12345678" >> ~/.nsmbrc'
        assert BSD_TEST(cmd) is True

    def test_09_Mounting_SMB(self):
        cmd = 'mount_smbfs -N -I %s -W LDAP02 ' % ip
        cmd += '"//%s@testnas/%s" "%s"' % (LDAP_USER, SMB_NAME, MOUNTPOINT)
        assert BSD_TEST(cmd) is True

    def test_09_Checking_permissions_on_MOUNTPOINT(self):
        device_name = return_output('dirname "%s"' % MOUNTPOINT)
        cmd = 'ls -la "%s" | ' % device_name
        cmd += 'awk \'$4 == "%s" && $9 == "%s" \'' % (VOL_GROUP, DATASET)
        assert BSD_TEST(cmd) is True

    def test_09_Creating_SMB_file(self):
        assert BSD_TEST('touch "%s/testfile"' % MOUNTPOINT) is True

    def test_09_Moving_SMB_file(self):
        cmd = 'mv "%s/testfile" "%s/testfile2"' % (MOUNTPOINT, MOUNTPOINT)
        assert BSD_TEST(cmd) is True

    def test_09_Copying_SMB_file(self):
        cmd = 'cp "%s/testfile2" "%s/testfile"' % (MOUNTPOINT, MOUNTPOINT)
        assert BSD_TEST(cmd) is True

    def test_09_Deleting_SMB_file_1_2(self):
        assert BSD_TEST('rm "%s/testfile"' % MOUNTPOINT) is True

    def test_09_Deleting_SMB_file_2_2(self):
        assert BSD_TEST('rm "%s/testfile2"' % MOUNTPOINT) is True

    def test_09_Unmounting_SMB(self):
        assert BSD_TEST('umount -f "%s"' % MOUNTPOINT) is True

    def test_09_Verifying_SMB_share_was_unmounted(self):
        assert BSD_TEST('mount | grep -qv "%s"' % MOUNTPOINT) is True

    def test_09_Removing_SMB_mountpoint(self):
        cmd = 'test -d "%s" && rmdir "%s" || exit 0' % (MOUNTPOINT, MOUNTPOINT)
        assert BSD_TEST(cmd) is True

    def test_09_Removing_SMB_share_on_SMB_PATH(self):
        payload = {"cfs_comment": "My Test SMB Share",
                   "cifs_path": SMB_PATH,
                   "cifs_name": SMB_NAME,
                   "cifs_guestok": True,
                   "cifs_vfsobjects": "streams_xattr"}
        assert DELETE_ALL("/sharing/cifs/", payload) == 204

    # Disable LDAP
    def test_10_Disabling_LDAPd(self):
        payload = {"ldap_basedn": LDAPBASEDN2,
                   "ldap_binddn": LDAPBINDDN2,
                   "ldap_bindpw": LDAPBINDPASSWORD2,
                   "ldap_netbiosname_a": BRIDGEHOST,
                   "ldap_hostname": LDAPHOSTNAME2,
                   "ldap_has_samba_schema": True,
                   "ldap_enable": False}
        assert PUT("/directoryservice/ldap/1/", payload) == 200

    # Now stop the SMB service
    def test_11_Stopping_SMB_service(self):
        assert PUT("/services/services/cifs/", {"srv_enable": False}) == 200

    # Check LDAP
    def test_12_Verify_LDAP_is_disabledd(self):
        assert GET_OUTPUT("/directoryservice/ldap/", "ldap_enable") is False

    def test_13_Verify_SMB_service_has_shut_down(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "STOPPED"

    # Check destroying a SMB dataset
    def test_14_Destroying_SMB_dataset(self):
        assert DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204


if __name__ == "__main__":
    unittest.main(verbosity=2)
