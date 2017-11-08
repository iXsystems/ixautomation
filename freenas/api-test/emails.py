#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

import unittest
from functions import PUT


class email_test(unittest.TestCase):

    def test_01_Configuring_email_settings(self):
        payload = {"em_fromemail": "william.spam@ixsystems.com",
                   "em_outgoingserver": "mail.ixsystems.com",
                   "em_pass": "changeme",
                   "em_port": 25,
                   "em_security": "plain",
                   "em_smtp": "true",
                   "em_user": "william.spam@ixsystems.com"}
        assert PUT("/system/email/",payload) == 200


if __name__ == "__main__":
    unittest.main(verbosity=2)
