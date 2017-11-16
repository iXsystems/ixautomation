#!/usr/bin/env python3.6

import os

user = "root"
password = "abcd1234"
ip = "10.20.21.215"
freenas_url = 'http://' + ip + '/api/v1.0'
interface = "em0"
ntpServer = "10.20.20.122"
localHome = "/home/ericbsd"
#disk1 = "vtbd1"
#disk2 = "vtbd2"
disk1 = "da1"
disk2 = "da2"
keyPath = "/home/ericbsd/.ssh/test_id_rsa"
sshKey = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCllFZEdVFpU9H6RwbU5yP/STj5pak7C65fS62cQwNrVEQPV316/6wr82dHYqK7cr4hgTxCAIdLgIlJlQx4LpIjraF46M4vcLz7itrpCwJZ3St4/g4tihP1pWOnWNAS0Zw0eSfXE3X4htGWfnLiae0H+dPVhG2zvb2eGuXYB6g03lHMuyVuty35U+L5I9Th/LnIUPW7/t0m2lTtgSd4IfDL0y5eBZ24iklW5aSsAc/D6sqRppS1tgOwPjiEupshgqPoZPsMcXH8h2WoOB77Dx877Wkvwwb8klH666MlSTNIw8AcKDWQfO6Mh1ptj7s4WMVf0sYHcp5BzgTuT1oRDDbh ericbsd@ericbsd.tn.ixsystems.com"
