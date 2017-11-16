#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
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

DATASET="ad-bsd"
SMB_NAME="TestShare"
SMB_PATH="/mnt/tank/" + DATASET
MOUNTPOINT="/tmp/ad-bsd" + BRIDGEHOST
VOL_GROUP="qa"

class ad_bsd_test(unittest.TestCase):
    def test_01_Clean_up_any_leftover_items(self):
        payload1 = {"ad_bindpw": ADPASSWORD,
                    "ad_bindname": ADUSERNAME,
                    "ad_domainname": BRIDGEDOMAIN,
                    "ad_netbiosname_a": BRIDGEHOST,
                    "ad_idmap_backend": "rid",
                    "ad_enable": False }
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
        BSD_TEST("umount -f " + MOUNTPOINT) == True
        BSD_TEST("rmdir " + MOUNTPOINT) == True

    # Set auxilary parameters to allow mount_smbfs to work with Active Directory
    def test_02_Creating_SMB_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    def test_03_Enabling_Active_Directory(self):
        payload = { "ad_bindpw": ADPASSWORD,
                    "ad_bindname": ADUSERNAME,
                    "ad_domainname": BRIDGEDOMAIN,
                    "ad_netbiosname_a": BRIDGEHOST,
                    "ad_idmap_backend": "rid",
                    "ad_enable": "true" }
        assert PUT("/directoryservice/activedirectory/1/", payload) == 200

    def test_04_Checking_Active_Directory(self):
        assert GET_OUTPUT("/directoryservice/activedirectory/", "ad_enable") == True

    def test_05_Checking_to_see_if_SMB_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "RUNNING"


    def test_06_Enabling_SMB_service(self):
        payload = { "cifs_srv_description": "Test FreeNAS Server",
                    "cifs_srv_guest": "nobody",
                    "cifs_hostname_lookup": "false",
                    "cifs_srv_aio_enable": "false" }
        assert PUT("/services/cifs/", payload) == 200

    # Now start the service
    def test_07_Starting_SMB_service(self):
        assert PUT("/services/services/cifs/", {"srv_enable": "true"}) == 200

    def test_08_Creating_SMB_mountpoint(self):
        assert BSD_TEST( "mkdir -p '%s' && sync" % MOUNTPOINT) == True

    def test_09_Changing_permissions_on_SMB_PATH(self):
        payload = { "mp_path": SMB_PATH,
                    "mp_acl": "unix",
                    "mp_mode": "777", "mp_user":
                    "root", "mp_group": "AD01\\QA",
                    "mp_recursive": "true" }
        assert PUT("/storage/permission/", payload) == 201

    def test_10_Creating_a_SMB_share_on_SMB_PATH(self):
        payload = { "cfs_comment": "My Test SMB Share",
                    "cifs_path": SMB_PATH,
                    "cifs_name": SMB_NAME,
                    "cifs_guestok": "true",
                    "cifs_vfsobjects": "streams_xattr" }
        assert POST("/sharing/cifs/", payload) == 201


    # The ADUSER user must exist in AD with this password
    def test_11_Store_AD_credentials_in_a_file_for_mount_smbfs(self):
        cmd = "echo \"[TESTNAS:ADUSER]\" > ~/.nsmbrc && echo password=12345678 >> ~/.nsmbrc"
        assert BSD_TEST(cmd) == True

    def test_12_Mounting_SMB(self):
        cmd = "mount_smbfs -N -I %s -W AD01 \"//aduser@testnas/%s\" \"%s\"" % (ip, SMB_NAME, MOUNTPOINT)
        assert BSD_TEST(cmd) == True

    #def test_13_Verify_that_SMB_share_has_finished_mounting(self):
    #wait_for_bsd_mnt "${MOUNTPOINT}"
    #check_exit_status || return 1

    #def test_14_Checking_permissions_on_MOUNTPOINT(self):
    #    device_name = return_output("dirname " + MOUNTPOINT)
    #    cmd = "ls -la '%s' | awk '\$4 == \"%s\" && \$9 == \"%s\" ' " % (device_name, VOL_GROUP, DATASET)
    #    assert BSD_TEST(cmd) == True

    #echo_test_title "Creating SMB file"
    #bsd_test "touch '${MOUNTPOINT}/testfile'"

    #echo_test_title "Moving SMB file"
    #bsd_test "mv '${MOUNTPOINT}/testfile' '${MOUNTPOINT}/testfile2'"

    #echo_test_title "Copying SMB file"
    #bsd_test "cp '${MOUNTPOINT}/testfile2' '${MOUNTPOINT}/testfile'"

    #echo_test_title "Deleting SMB file 1/2"
    #bsd_test "rm '${MOUNTPOINT}/testfile'"

    #echo_test_title "Deleting SMB file 2/2"
    #bsd_test "rm \"${MOUNTPOINT}/testfile2\""

    #echo_test_title "Unmounting SMB"
    #bsd_test "umount \"${MOUNTPOINT}\""

    #echo_test_title "Removing SMB mountpoint"
    #bsd_test "test -d \"${MOUNTPOINT}\" && rmdir \"${MOUNTPOINT}\" || exit 0"

    #echo_test_title "Removing SMB share on ${SMB_PATH}"
    #rest_request "DELETE" "/sharing/cifs/" '{ "cfs_comment": "My Test SMB Share", "cifs_path": "'"${SMB_PATH}"'", "cifs_name": "'"${SMB_NAME}"'", "cifs_guestok": true, "cifs_vfsobjects": "streams_xattr" }'

    # Disable Active Directory Directory
    def test_23_Disabling_Active_Directory(test):
        payload = { "ad_bindpw": ADPASSWORD,
                "ad_bindname": ADUSERNAME,
                "ad_domainname": BRIDGEDOMAIN,
                "ad_netbiosname_a": BRIDGEHOST,
                "ad_idmap_backend": "rid",
                "ad_enable": "false" }
        assert PUT("/directoryservice/activedirectory/1/", payload) == 200

    # Check Active Directory
    def test_24_Verify_Active_Directory_is_disabled(self):
        assert GET_OUTPUT("/directoryservice/activedirectory/", "ad_enable") == False

    def test_25_Verify_SMB_service_is_disabled(self):
        assert GET_OUTPUT("/services/services/cifs/", "srv_state") == "STOPPED"

    # Check destroying a SMB dataset
    def test_26_Destroying_SMB_dataset(self):
        assert DELETE("/storage/volume/1/datasets/%s/" % DATASET) == 204


if __name__ == "__main__":
    unittest.main(verbosity=2)
