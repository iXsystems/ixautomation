#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

import unittest
from functions import PUT, GET_OUTPUT, is_agent_setup, if_key_listed
from auto_config import sshKey


class ssh_test(unittest.TestCase):

    def test_1_Configuring_ssh_settings(self):
        payload = {"ssh_rootlogin": 'true'}
        assert PUT("/services/ssh/", payload) == 200

    def test_2_Enabling_ssh_service(self):
        payload = {"srv_enable": 'true'}
        assert PUT("/services/services/ssh/", payload) == 200

    def test_3_Checking_ssh_enabled(self):
        assert GET_OUTPUT("/services/services/ssh/",'srv_state') == "RUNNING"

    def test_4_Ensure_ssh_agent_is_setup(self):
        assert is_agent_setup() == True

    def test_5_Ensure_ssh_key_is_up(self):
        assert if_key_listed() == True

    def test_6_Add_ssh_ky_to_root(self):
        payload = {"bsdusr_sshpubkey": sshKey}
        assert PUT("/account/users/1/", payload) == 200


if __name__ == "__main__":
    unittest.main(verbosity=2)
