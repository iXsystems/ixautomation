#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, POST, GET_OUTPUT, DELETE_ALL, DELETE

try:
    from config import BRIDGEHOST, BRIDGEDOMAIN, ADPASSWORD, ADUSERNAME
    from config import LDAPBASEDN, LDAPHOSTNAME
except ImportError:
    exit()


DATASET = "ldap-bsd"
SMB_NAME = "TestShare"
SMB_PATH = "/mnt/tank/" + DATASET
MOUNTPOINT = "/tmp/ldap-bsd" + BRIDGEHOST
VOL_GROUP = "qa"


class ldap_bsd_test(unittest.TestCase):

    def Clean_up_any_leftover_items(self):
        payload = {"ad_bindpw": ADPASSWORD,
                   "ad_bjindname": ADUSERNAME,
                   "ad_domainname": BRIDGEDOMAIN,
                   "ad_netbiosname_a": BRIDGEHOST,
                   "ad_idmap_backend": "rid",
                   "ad_enable": "false"}
        PUT("/directoryservice/activedirectory/1/", payload)
        payload1 = {"ldap_basedn": LDAPBASEDN,
                    "ldap_anonbind": "true",
                    "ldap_netbiosname_a": BRIDGEHOST,
                    "ldap_hostname": LDAPHOSTNAME,
                    "ldap_has_samba_schema": "true",
                    "ldap_enable": "false"}
        PUT("/directoryservice/ldap/1/", payload1)
        payload2 = {"cfs_comment": "My Test SMB Share",
                    "cifs_path": SMB_PATH,
                    "cifs_name": SMB_NAME,
                    "cifs_guestok": "true",
                    "cifs_vfsobjects": "streams_xattr"}
        DELETE_ALL("/sharing/cifs/", payload2)
        DELETE("/storage/volume/1/datasets/%s/" % DATASET)

    # Set auxilary parameters to allow mount_smbfs to work with ldap
    def test_02_Setting_auxilary_parameters_for_mount_smbfs(self):
        options = "lanman auth = yes\nntlm auth = yes \nraw NTLMv2 auth = yes"
        payload = {"cifs_srv_smb_options": options}
        assert PUT("/services/cifs/", payload) == 200

    def test_03_Creating_SMB_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    # Enable LDAP
    def test_04_Enabling_LDAP_with_anonymous_bind(self):
        payload = {"ldap_basedn": LDAPBASEDN,
                   "ldap_anonbind": "true",
                   "ldap_netbiosname_a": BRIDGEHOST,
                   "ldap_hostname": LDAPHOSTNAME,
                   "ldap_has_samba_schema": "true",
                   "ldap_enable": "true"}
        assert PUT("/directoryservice/ldap/1/", payload) == 200

    # Check LDAP
    def test_05_Checking_LDAP(self):
        assert GET_OUTPUT("/directoryservice/ldap/", "ldap_enable") is True

    def test_06_Enabling_SMB_service(self):
        payload = {"cifs_srv_description": "Test FreeNAS Server",
                   "cifs_srv_guest": "nobody",
                   "cifs_hostname_lookup": False,
                   "cifs_srv_aio_enable": False}
        assert PUT("/services/cifs/", payload) == 200

    # Now start the service
    def test_07_Starting_SMB_service(self):
        assert PUT("/services/services/cifs/", {"srv_enable": True}) == 200

    def test_08_Checking_to_see_if_SMB_service_is_enabled(self):
        GET_OUTPUT("/services/services/cifs/", "srv_state")

    # def test_09_Changing_permissions_on_SMB_PATH(self):
    #    payload = { "mp_path": SMB_PATH,
    #                "mp_acl": "unix",
    #                "mp_mode": "777",
    #                "mp_user": "root",
    #                "mp_group": "qa",
    #                "mp_recursive": True }
    #    assert PUT("/storage/permission/", payload) == 201

    def test_10_Creating_a_SMB_share_on_SMB_PATH(self):
        payload = {"cfs_comment": "My Test SMB Share",
                   "cifs_path": SMB_PATH,
                   "cifs_name": SMB_NAME,
                   "cifs_guestok": True,
                   "cifs_vfsobjects": "streams_xattr"}
        assert POST("/sharing/cifs/", payload) == 201

    def test_11_Checking_to_see_if_SMB_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "RUNNING"

    # BSD test to be done when when BSD_TEST is functional

    def test_24_Removing_SMB_share_on_SMB_PATH(self):
        payload = {"cfs_comment": "My Test SMB Share",
                   "cifs_path": SMB_PATH,
                   "cifs_name": SMB_NAME,
                   "cifs_guestok": "true",
                   "cifs_vfsobjects": "streams_xattr"}
        DELETE_ALL("/sharing/cifs/", payload) == 204

    # Disable LDAP
    def test_25_Disabling_LDAP_with_anonymous_bind(self):
        payload = {"ldap_basedn": LDAPBASEDN,
                   "ldap_anonbind": True,
                   "ldap_netbiosname_a": "'${BRIDGEHOST}'",
                   "ldap_hostname": "'${LDAPHOSTNAME}'",
                   "ldap_has_samba_schema": True,
                   "ldap_enable": False}
        assert PUT("/directoryservice/ldap/1/", payload) == 200

    # Now stop the SMB service
    def test_26_Stopping_SMB_service(self):
        PUT("/services/services/cifs/", {"srv_enable": False}) == 200

    # Check LDAP
    def test_27_Verify_LDAP_is_disabled(self):
        GET_OUTPUT("/directoryservice/ldap/", "ldap_enable") is False

    def test_28_Verify_SMB_service_is_disabled(self):
        GET_OUTPUT("/services/services/cifs/", "srv_state") == "STOPPED"

    # Check destroying a SMB dataset
    def test_29_Destroying_SMB_dataset(self):
        DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204


if __name__ == "__main__":
    unittest.main(verbosity=2)
