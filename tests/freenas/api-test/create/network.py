#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

from auto_config import interface
from functions import POST, PUT
import unittest
from config import BRIDGEDOMAIN, BRIDGEHOST, BRIDGEDNS, BRIDGEGW

class network(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        pass

    def test_01_configure_interface_dhcp(self):
        payload = {"int_dhcp": "true",
                   "int_name": "ext",
                   "int_interface": interface
                  }
        assert POST("/network/interface/", payload) == 201

    def test_02_Setting_default_route_and_DNS(self):
        payload = {"gc_domain": BRIDGEDOMAIN,
                   "gc_hostname": BRIDGEHOST,
                   "gc_ipv4gateway": BRIDGEGW,
                   "gc_nameserver1": BRIDGEDNS}
        assert PUT("/network/globalconfiguration/", payload) == 200


    @classmethod
    def tearDownClass(inst):
        pass

if __name__ == "__main__":
    unittest.main(verbosity=2)
