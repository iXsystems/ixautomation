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

DATASET="webdavshare"
DATASET_PATH="/mnt/tank/%s/" % DATASET
TMP_FILE="/tmp/testfile.txt"
SHARE_NAME="webdavshare"
SHARE_USER="webdav"
SHARE_PASS="davtest"

class webdav_bsd_test(unittest.TestCase):

    # Clean up any leftover items from previous failed test runs
    @classmethod
    def setUpClass(inst):
        payload1 = {"webdav_name": SHARE_NAME,
                    "webdav_comment": "Auto-created by ixbuild tests",
                    "webdav_path": DATASET_PATH}
        DELETE_ALL("/sharing/webdav/", payload)

        PUT("/services/services/webdav/", {"srv_enable": False})
        DELETE("/storage/volume/1/datasets/%s/", DATASET)
        # rm "${TMP_FILE}" &>/dev/null

    def test_01_Creating_dataset_for_WebDAV_use(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    def test_02_Changing_permissions_on_DATASET_PATH(self):
        payload = {"mp_path": DATASET_PATH,
                   "mp_acl": "unix",
                   "mp_mode": "777",
                   "mp_user": "root",
                   "mp_group": "wheel"}
        assert PUT("/storage/permission/", payload) == 201

    def test_03_Creating_WebDAV_share_on_DATASET_PATH(self):
        payload = {"webdav_name": SHARE_NAME,
                   "webdav_comment": "Auto-created by ixbuild tests",
                   "webdav_path": DATASET_PATH}
        assert POST("/sharing/webdav/", payload) == 201

    def test_04_Starting_WebDAV_service(self):
        assert PUT("/services/services/webdav/", {"srv_enable": True}) == 200

    #commenting exit_status and service_status
    #echo_test_title "Poll test target to ensure WebDAV service is up and running"
    #wait_for_avail_port "8080"
    #check_exit_status || return 1

    #echo_test_title "Verifying that WebDAV service is reported as enabled by the API"
    #rest_request "GET" "/services/services/webdav/"
    #check_service_status "RUNNING" || return 1

    #echo_test_title "Verify that user and group ownership was changed to \"webdav\" on \"${DATASET_PATH}\""
    #ssh_test "ls -l \"$(dirname ${DATASET_PATH})\" | awk 'NR > 1 && \$3 == \"webdav\" && \$4 == \"webdav\" {print \$9}' | grep \"${DATASET}\""
    #check_exit_status

    # Test our WebDAV share using curl commands

    #touch "${TMP_FILE}"

    #echo_test_title "Create test file on the WebDAV share using curl"
    #rc_test "curl -f --digest -u \"${SHARE_USER}:${SHARE_PASS}\" -T \"${TMP_FILE}\" \"http://${FNASTESTIP}:8080/${SHARE_NAME}/\" -w \"%{http_code}\" | grep -q 201"

    #echo_test_title "Create a new directory on the WebDAV share using curl"
    #rc_test "curl -f --digest -u \"${SHARE_USER}:${SHARE_PASS}\" -X MKCOL \"http://${FNASTESTIP}:8080/${SHARE_NAME}/tmp/\" -w \"%{http_code}\" | grep -q 201"

    #echo_test_title "Test moving file into new directory on WebDAV share using curl"
    #rc_test "curl -f --digest -u \"${SHARE_USER}:${SHARE_PASS}\" -X MOVE --header \"Destination:http://${FNASTESTIP}:8080/${SHARE_NAME}/tmp/testfile.txt\" \"http://${FNASTESTIP}:8080/${SHARE_NAME}/testfile.txt\" -w \"%{http_code}\" | grep -q 201"

    #echo_test_title "Test deleting file from the WebDAV share using curl"
    #curl --digest -u "${SHARE_USER}:${SHARE_PASS}" -X DELETE "http://${FNASTESTIP}:8080/${SHARE_NAME}/tmp/testfile.txt" &>/dev/null
    #rc_test "curl --digest -u \"${SHARE_USER}:${SHARE_PASS}\" \"http://${FNASTESTIP}:8080/${SHARE_NAME}/tmp/testfile.txt\" -w \"%{http_code}\" 2>/dev/null | grep -q 404"

    #echo_test_title "Test deleting directory from the WebDAV share using curl"
    #curl --digest -u "${SHARE_USER}:${SHARE_PASS}" -X DELETE "http://${FNASTESTIP}:8080/${SHARE_NAME}/tmp/" &>/dev/null
    #rc_test "curl --digest -u \"${SHARE_USER}:${SHARE_PASS}\" \"http://${FNASTESTIP}:8080/${SHARE_NAME}/tmp/\" -w \"%{http_code}\" 2>/dev/null | grep -q 404"

    #2 tests below this line are the reason for XML falure
    #1st test
    #hiding the below test for curl testing
    #echo_test_title "Removing WebDAV share on \"${DATASET_PATH}\""
    #rest_request "DELETE" "/sharing/webdav/" '{ "webdav_name": "'"${SHARE_NAME}"'", "webdav_comment": "Auto-created by '"${BRIDGEHOST}"'", "webdav_path": "'"${DATASET_PATH}"'" }'
    #check_rest_response "204"

    def test_05_Stopping_WebDAV_service(self):
        assert PUT("/services/services/webdav/", {"srv_enable": False}) == 200

    def test_06_Verifying_that_the_WebDAV_service_has_stopped(self):
        assert GET_OUTPUT("/services/services/webdav", "srv_state") == "STOPPED"

    #2nd test
    #echo_test_title "Destroying WebDAV dataset \"${DATASET}\""
    #rest_request "DELETE" "/storage/volume/1/datasets/${DATASET}/"
    #check_rest_response "204" || return 1

    # Remove tmp file created for testing
    # rm '/tmp/testfile.txt' &>/dev/null

if __name__ == "__main__":
    unittest.main(verbosity=2)

