#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
import sys, os
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import PUT, POST, GET_OUTPUT
from auto_config import ip

try:
    import config
except ImportError:
    pass
else:
    from config import  NISSERVER, NISDOMAIN

# define variables
SERVER=NISSERVER
DOMAIN=NISDOMAIN
DATASET="nis-bsd"
NIS_PATH="/mnt/tank/" + DATASET


class nis_bsd_test(unittest.TestCase):
    def test_01_Setting_NIS_domain(self):
        assert PUT("/directoryservice/nis/", {"nis_domain": NISDOMAIN}) == 200

    def test_02_Setting_NIS_server(self):
        assert PUT("/directoryservice/nis/", {"nis_servers": NISSERVER}) == 200

    def test_03_Enabling_NIS_service(self):
        assert PUT("/directoryservice/nis/", {"nis_enable": True}) == 200

    def test_04_Checking_if_NIS_service_is_enable(self):
        assert GET_OUTPUT("/directoryservice/nis/", "nis_enable") == True

    def test_05_Creating_NIS_dataset(self):
        assert POST("/storage/volume/tank/datasets/", {"name": DATASET}) == 201

    def test_06_Enabling_secure_mode(self):
        assert PUT("/directoryservice/nis/", {"nis_secure_mode": True}) == 200

    def test_07_Checking_if_secure_mode_is_enable(self):
        assert GET_OUTPUT("/directoryservice/nis/", "nis_secure_mode") == True

    def test_08_Disabling_secure_mode(self):
        assert PUT("/directoryservice/nis/", {"nis_secure_mode": False}) == 200

    def test_09_Enabling_manycast(self):
        assert PUT("/directoryservice/nis/", {"nis_manycast": True}) == 200

    def test_10_Checking_if_manycast_is_enable(self):
        assert GET_OUTPUT("/directoryservice/nis/", "nis_manycast") == True

    def test_11_Disabling_manycast(self):
        assert PUT("/directoryservice/nis/", {"nis_manycast": False}) == 200

    def test_12_Disabling_NIS_service(self):
        assert PUT("/directoryservice/nis/", {"nis_enable": False}) == 200

if __name__ == "__main__":
    unittest.main(verbosity=2)
