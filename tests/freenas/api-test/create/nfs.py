#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, POST, GET_OUTPUT
from auto_config import ip
try:
    from config import BRIDGEHOST
except ImportError:
    exit()

NFS_PATH = "/mnt/tank/share"
MOUNTPOINT = "/tmp/nfs" + BRIDGEHOST


class nfs_test(unittest.TestCase):

    # Enable NFS server
    def test_01_Creating_the_NFS_server(self):
        paylaod = {"nfs_srv_bindip": ip,
                   "nfs_srv_mountd_port": 618,
                   "nfs_srv_allow_nonroot": False,
                   "nfs_srv_servers": 10,
                   "nfs_srv_udp": False,
                   "nfs_srv_rpcstatd_port": 871,
                   "nfs_srv_rpclockd_port": 32803,
                   "nfs_srv_v4": False,
                   "nfs_srv_v4_krb": False,
                   "id": 1}
        assert PUT("/services/nfs/", paylaod) == 200

    # Check creating a NFS share
    def test_02_Creating_a_NFS_share_on_NFS_PATH(self):
        paylaod = {"nfs_comment": "My Test Share",
                   "nfs_paths": [NFS_PATH],
                   "nfs_security": "sys"}
        assert POST("/sharing/nfs/", paylaod) == 201

    # Now start the service
    def test_03_Starting_NFS_service(self):
        assert PUT("/services/services/nfs/", {"srv_enable": True}) == 200

    def test_06_Checking_to_see_if_NFS_service_is_enabled(self):
        assert GET_OUTPUT("/services/services/nfs/", "srv_state") == "RUNNING"


if __name__ == "__main__":
    unittest.main(verbosity=2)
