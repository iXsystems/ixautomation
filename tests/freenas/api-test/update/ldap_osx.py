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

try:
    from config import BRIDGEHOST, BRIDGEDOMAIN, ADPASSWORD, ADUSERNAME
    from config import LDAPBASEDN, LDAPHOSTNAME, LDAPHOSTNAME2
    from config import LDAPBASEDN2, LDAPBINDDN2, LDAPBINDPASSWORD2
except ImportError:
    exit()

DATASET = "ldap-osx"
SMB_NAME = "TestShare"
SMB_PATH = "/mnt/tank/${DATASET}"
MOUNTPOINT = "/tmp/ldap-osx${BRIDGEHOST}"
LDAP_USER = "ldapuser"
LDAP_PASS = "12345678"


class ldap_osx_test(unittest.TestCase):

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

    # Set auxilary parameters to allow mount_smbfs to work with ldap
    def test_01_Creating_SMB_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    # Enable LDAP
    def test_02_Enabling_LDAP(self):
        payload = {"ldap_basedn": LDAPBASEDN2,
                   "ldap_binddn": LDAPBINDDN2,
                   "ldap_bindpw": LDAPBINDPASSWORD2,
                   "ldap_netbiosname_a": BRIDGEHOST,
                   "ldap_hostname": LDAPHOSTNAME2,
                   "ldap_has_samba_schema": True,
                   "ldap_enable": True}
        assert PUT("/directoryservice/ldap/1/", payload) == 200

    # Check LDAP
    def test_03_Checking_LDAP(self):
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

    # def test_07_Changing_permissions_on_SMB_PATH(self):
    #     payload = {"mp_path": SMB_PATH,
    #                "mp_acl": "unix",
    #                "mp_mode": "777",
    #                "mp_user": "root",
    #                "mp_group": "qa",
    #                "mp_recursive": True}
    #     assert PUT("/storage/permission/", payload) == 200

    # def test_08_Creating_a_SMB_share_on_SMB_PATH(self):
    #     payload = {"mp_path": SMB_PATH,
    #                "mp_acl": "unix",
    #                "mp_mode": "777",
    #                "mp_user": "root",
    #                "mp_group": "qa",
    #                "mp_recursive": True}
    #     assert POST("/sharing/cifs/", payload) == 201

    def test_09_Removing_SMB_share_on_SMB_PATH(self):
        payload = {"cfs_comment": "My Test SMB Share",
                   "cifs_path": SMB_PATH,
                   "cifs_name": SMB_NAME,
                   "cifs_guestok": True,
                   "cifs_vfsobjects": "streams_xattr"}
        assert DELETE_ALL("/sharing/cifs/", payload) == 204

    # Disable LDAP
    def test_10_Disabling_LDAP(self):
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
