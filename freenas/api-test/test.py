#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
from auto_config import freenas_url, password, user, ip
import json
import requests

try:
    import config
except ImportError:
    pass
else:
    from config import BRIDGEHOST, BRIDGEDOMAIN, ADPASSWORD, ADUSERNAME
    from config import LDAPBASEDN, LDAPBINDDN, LDAPHOSTNAME, LDAPBINDPASSWORD
authentification = (user, password)
header = {'Content-Type': 'application/json', 'Vary': 'accept'}
DATASET="ad-bsd"
SMB_NAME="TestShare"
SMB_PATH="/mnt/tank/" + DATASET
MOUNTPOINT="/tmp/ad-bsd" + BRIDGEHOST
VOL_GROUP="qa"

payload = {"ad_enable": "true"}
testpath = "/directoryservice/activedirectory/2/"
putit = requests.put(freenas_url + testpath, headers=header,
                     auth=authentification, data=json.dumps(payload))

assert putit.status_code == 200



payload1 = {"ad_bindpw": ADPASSWORD,
            "ad_bindname": ADUSERNAME,
            "ad_domainname": BRIDGEDOMAIN,
            "ad_netbiosname": BRIDGEHOST,
            "ad_idmap_backend": "rid",
            "ad_enable": "false"}

payload = {"ad_enable": "true"}

