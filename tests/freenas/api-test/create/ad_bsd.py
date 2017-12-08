#!/usr/bin/env python3.6
# Author: Eric Turgeon.
# License: BSD
# Location for tests into REST API of FreeNAS


import unittest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, POST, GET_OUTPUT, DELETE, DELETE_ALL
from functions import BSD_TEST


try:
    from config import BRIDGEHOST, BRIDGEDOMAIN, ADPASSWORD, ADUSERNAME
    from config import LDAPBASEDN, LDAPBINDDN, LDAPHOSTNAME, LDAPBINDPASSWORD
except ImportError:
    exit

DATASET = "ad-bsd"
SMB_NAME = "TestShare"
SMB_PATH = "/mnt/tank/" + DATASET
MOUNTPOINT = "/tmp/ad-bsd" + BRIDGEHOST
VOL_GROUP = "qa"


class ad_bsd_test(unittest.TestCase):

    def test_01_clean_up_any_leftover_items(self):
        payload1 = {"ad_bindpw": ADPASSWORD,
                    "ad_bindname": ADUSERNAME,
                    "ad_domainname": BRIDGEDOMAIN,
                    "ad_netbiosname_a": BRIDGEHOST,
                    "ad_idmap_backend": "rid",
                    "ad_enable": False}
        PUT("/directoryservice/activedirectory/1/", payload1) == 200
        payload2 = {"ldap_basedn": LDAPBASEDN,
                    "ldap_binddn": LDAPBINDDN,
                    "ldap_bindpw": LDAPBINDPASSWORD,
                    "ldap_netbiosname_a": BRIDGEHOST,
                    "ldap_hostname": LDAPHOSTNAME,
                    "ldap_has_samba_schema": "true",
                    "ldap_enable": "false"}
        PUT("/directoryservice/ldap/1/", payload2) == 200
        PUT("/services/services/cifs/", {"srv_enable": "false"}) == 200
        payload3 = {"cfs_comment": "My Test SMB Share",
                    "cifs_path": SMB_PATH,
                    "cifs_name": SMB_NAME,
                    "cifs_guestok": "true",
                    "cifs_vfsobjects": "streams_xattr"}
        DELETE_ALL("/sharing/cifs/", payload3) == 204
        DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204
        # BSD_TEST("umount -f " + MOUNTPOINT)
        # BSD_TEST("rmdir " + MOUNTPOINT)

    def test_02_creating_smb_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    def test_03_enabling_active_directory(self):
        payload = {"ad_bindpw": ADPASSWORD,
                   "ad_bindname": ADUSERNAME,
                   "ad_domainname": BRIDGEDOMAIN,
                   "ad_netbiosname_a": BRIDGEHOST,
                   "ad_idmap_backend": "rid",
                   "ad_enable": True}
        assert PUT("/directoryservice/activedirectory/1/", payload) == 200

    def test_04_checking_active_directory(self):
        assert GET_OUTPUT("/directoryservice/activedirectory/",
                          "ad_enable") is True

    def test_05_checking_to_see_if_smb_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "RUNNING"

    def test_06_enabling_smb_service(self):
        payload = {"cifs_srv_description": "Test FreeNAS Server",
                   "cifs_srv_guest": "nobody",
                   "cifs_hostname_lookup": False,
                   "cifs_srv_aio_enable": False}
        assert PUT("/services/cifs/", payload) == 200

    # Now start the service
    def test_07_Starting_SMB_service(self):
        assert PUT("/services/services/cifs/", {"srv_enable": "true"}) == 200

    def test_08_creating_smb_mountpoint(self):
        assert BSD_TEST("mkdir -p '%s' && sync" % MOUNTPOINT) is True

    # def test_09_Changing_permissions_on_SMB_PATH(self):
    #    payload = { "mp_path": SMB_PATH,
    #                "mp_acl": "unix",
    #                "mp_mode": "777",
    #                "mp_user": "root",
    #                "mp_group": r"AD01\QA",
    #                "mp_recursive": True }
    #    assert PUT("/storage/permission/", payload) == 201

    def test_10_Creating_a_SMB_share_on_SMB_PATH(self):
        payload = {"cfs_comment": "My Test SMB Share",
                   "cifs_path": SMB_PATH,
                   "cifs_name": SMB_NAME,
                   "cifs_guestok": "true",
                   "cifs_vfsobjects": "streams_xattr"}
        assert POST("/sharing/cifs/", payload) == 201

    # Disable Active Directory Directory
    def test_23_disabling_active_directory(self):
        payload = {"ad_bindpw": ADPASSWORD,
                   "ad_bindname": ADUSERNAME,
                   "ad_domainname": BRIDGEDOMAIN,
                   "ad_netbiosname_a": BRIDGEHOST,
                   "ad_idmap_backend": "rid",
                   "ad_enable": "false"}
        assert PUT("/directoryservice/activedirectory/1/", payload) == 200

    # Check Active Directory
    def test_24_Verify_Active_Directory_is_disabled(self):
        assert GET_OUTPUT("/directoryservice/activedirectory/",
                          "ad_enable") is False

    def test_25_Verify_SMB_service_is_disabled(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "STOPPED"

    # Check destroying a SMB dataset
    def test_26_Destroying_SMB_dataset(self):
        assert DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204


if __name__ == "__main__":
    unittest.main(verbosity=2)
