#!/usr/bin/env python3.6

# This file is use to test functions code

from functions import BSD_TEST

try:
    from config import BRIDGEHOST
except ImportError:
    exit()

MOUNTPOINT = "/tmp/ldap-bsd" + BRIDGEHOST

cmd = 'umount -f "%s" &>/dev/null; rmdir "%s" &>/dev/null' % (MOUNTPOINT,
                                                              MOUNTPOINT)
print(BSD_TEST(cmd))
