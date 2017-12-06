#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
from functions import PUT, POST, GET_OUTPUT, DELETE, DELETE_ALL, OSX_TEST
from auto_config import ip
try:
    import config
except ImportError:
    pass
else:
    from config import BRIDGEHOST, BRIDGEDOMAIN, ADPASSWORD, ADUSERNAME
    from config import LDAPBASEDN, LDAPBINDDN, LDAPBINDPASSWORD, LDAPHOSTNAME

DATASET = "smb-osx"
SMB_NAME = "TestShare"
SMB_PATH = "/mnt/tank/" + DATASET
MOUNTPOINT = "/tmp/smb-osx" + BRIDGEHOST
VOL_GROUP="qa"

class smb_osx_test(unittest.TestCase):

    # Clean up any leftover items from previous failed AD LDAP or SMB runs
    @classmethod
    def setUpClass(inst):
        payload1 = {"ad_bindpw": ADPASSWORD,
                    "ad_bindname": ADUSERNAME,
                    "ad_domainname": BRIDGEDOMAIN,
                    "ad_netbiosname_a": BRIDGEHOST,
                    "ad_idmap_backend": "rid",
                    "ad_enable": False}
        PUT("/directoryservice/activedirectory/1/", payload1)
        payload2 = {"ldap_basedn": LDAPBASEDN,
                    "ldap_binddn": LDAPBINDDN,
                    "ldap_bindpw": LDAPBINDPASSWORD,
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
        DELETE("/sharing/cifs/", payload3)
        DELETE("/storage/volume/1/datasets/%s/" % DATASET)

    def test_01_Creating_SMB_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    def test_02_Starting_SMB_service(self):
         assert PUT("/services/services/cifs/", {"srv_enable": True}) == 200

    def test_03_Changing_permissions_on_SMB_PATH(self):
        payload = {"mp_path": SMB_PATH,
                   "mp_acl": "unix",
                   "mp_mode": "777",
                   "mp_user": "root",
                   "mp_group": "wheel"}
        assert PUT("/storage/permission/", payload) == 201

    def test_04_Creating_a_SMB_share_on_SMB_PATH(self):
        payload = {"cfs_comment": "My Test SMB Share",
                   "cifs_path": SMB_PATH,
                   "cifs_name": SMB_NAME,
                   "cifs_guestok": True,
                   "cifs_vfsobjects": "streams_xattr"}
        assert POST("/sharing/cifs/", payload) == 201

    def test_05_Checking_to_see_if_SMB_service_is_running(self):
        assert GET("/services/services/cifs/", "srv_state") == "RUNNING"

    # OSX_TEST here when ready

    def test_06_Removing_SMB_share_on_SMB_PATH(self):
        payload = {"cfs_comment": "My Test SMB Share",
                   "cifs_path": SMB_PATH,
                   "cifs_name": SMB_NAME,
                   "cifs_guestok": True,
                   "cifs_vfsobjects": "streams_xattr"}
        assert DELETE("/sharing/cifs/", payload) == 204

    # Now stop the service
    def test_07_Stopping_SMB_service(self):
        assert PUT("/services/services/cifs/", {"srv_enable": False}) == 200

    def test_08_Verify_SMB_service_is_disabled(self):
        assert GET("/services/services/cifs/", "srv_state") == "STOPPED"

    # Check destroying a SMB dataset
    def test_09_Destroying_SMB_dataset(self):
        assert DELETE("/storage/volume/1/datasets/%s/" + DATASET) == 204


if __name__ == "__main__":
    unittest.main(verbosity=2)
