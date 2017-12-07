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

DATASET = "webdavshare"
DATASET_PATH = "/mnt/tank/%s/" % DATASET
SHARE_NAME = "webdavshare"
SHARE_USER = "webdav"
SHARE_PASS = "davtest"
MOUNTPOINT = "/tmp/webdav-osx" + BRIDGEHOST


class webdav_bsd_test(unittest.TestCase):

    # Clean up any leftover items from previous failed test runs
    @classmethod
    def setUpClass(inst):
        payload = {"webdav_name": SHARE_NAME,
                   "webdav_comment": "Auto-created by " + BRIDGEHOST,
                   "webdav_path": DATASET_PATH}
        DELETE("/sharing/webdav/", payload)
        PUT("/services/services/webdav/", {"srv_enable": False})
        DELETE("/storage/volume/1/datasets/%s/" % DATASET)

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
                   "webdav_comment": "Auto-created by " + BRIDGEHOST,
                   "webdav_path": DATASET_PATH}
        assert POST("/sharing/webdav/", payload) == 201

    def test_04_Starting_WebDAV_service(self):
        assert PUT("/services/services/webdav/", {"srv_enable": True}) == 200

    def test05_Stopping_WebDAV_service(self):
        assert PUT("/services/services/webdav/", {"srv_enable": False}) == 200

    def test_06_Verifying_that_the_WebDAV_service_has_stopped(self):
        assert GET("/services/services/webdav", "srv_state") == "STOPPED"


if __name__ == "__main__":
    unittest.main(verbosity=2)
