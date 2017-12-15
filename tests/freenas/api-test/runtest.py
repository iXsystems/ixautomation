#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

from subprocess import call
from sys import argv
from os import path, getcwd, makedirs
import getopt
import sys

apifolder = getcwd()
sys.path.append(apifolder)

results_xml = getcwd() + '/results/'
localHome = path.expanduser('~')
dotsshPath = localHome + '/.ssh'
keyPath = localHome + '/.ssh/test_id_rsa'

error_msg = """Usage for %s:
    --ip <###.###.###.###>     - IP of the FreeNAS
    --password <root password> - Password of the FreeNAS root user
    --interface <interface>    - The interface that FreeNAS is run one
    """ % argv[0]

# if have no argumment stop
if len(argv) == 1:
    print(error_msg)
    exit()

# look if all the argument are there.
try:
    myopts, args = getopt.getopt(argv[1:], 'ipI', ["ip=",
                                                   "password=", "interface="])
except getopt.GetoptError as e:
    print(str(e))
    print(error_msg)
    exit()

for output, arg in myopts:
    if output in ('-i', '--ip'):
        ip = arg
    elif output in ('-p', '--password'):
        passwd = arg
    elif output in ('-I', '--interface'):
        interface = arg

cfg_content = """#!/usr/bin/env python3.6

import os

user = "root"
password = "%s"
ip = "%s"
freenas_url = 'http://' + ip + '/api/v1.0'
interface = "%s"
ntpServer = "10.20.20.122"
localHome = "%s"
disk1 = "vtbd1"
disk2 = "vtbd2"
#disk1 = "da1"
#disk2 = "da2"
keyPath = "%s"
""" % (passwd, ip, interface, localHome, keyPath)

cfg_file = open("auto_config.py", 'w')
cfg_file.writelines(cfg_content)
cfg_file.close()

from functions import setup_ssh_agent, create_key, add_ssh_key

# Setup ssh agent befor starting test.
setup_ssh_agent()
if path.isdir(dotsshPath) is False:
    makedirs(dotsshPath)
if path.exists(keyPath) is False:
    create_key(keyPath)
add_ssh_key(keyPath)

f = open(keyPath + '.pub', 'r')
Key = f.readlines()[0].rstrip()

cfg_file = open("auto_config.py", 'a')
cfg_file.writelines('sshKey = "%s"\n' % Key)
cfg_file.close()

# Create test

call(["py.test-3.6", "--junitxml",
      "%snetwork_result.xml" % results_xml,
      "create/network.py"])
call(["py.test-3.6", "--junitxml",
      "%sssh_result.xml" % results_xml,
      "create/ssh.py"])
call(["py.test-3.6", "--junitxml",
      "%sstorage_result.xml" % results_xml,
      "create/storage.py"])
call(["py.test-3.6", "--junitxml",
      "%sntp_result.xml" % results_xml,
      "create/ntp.py"])
call(["py.test-3.6", "--junitxml",
      "%sad_bsd_result.xml" % results_xml,
      "create/ad_bsd.py"])
call(["py.test-3.6", "--junitxml",
      "%sad_osx_result.xml" % results_xml,
      "create/ad_osx.py"])
call(["py.test-3.6", "--junitxml",
      "%safp_osx_result.xml" % results_xml,
      "create/afp_osx.py"])
# call(["py.test-3.6", "--junitxml",
#        "%salerts_result.xml" % results_xml,
#        "create/alerts.py"])
call(["py.test-3.6", "--junitxml",
      "%sbootenv_result.xml" % results_xml,
      "create/bootenv.py"])
call(["py.test-3.6", "--junitxml",
      "%scronjob_result.xml" % results_xml,
      "create/cronjob.py"])
# call(["py.test-3.6", "--junitxml",
#       "%sdebug_result.xml" % results_xml,
#       "create/debug.py"])
call(["py.test-3.6", "--junitxml",
      "%semails_result.xml" % results_xml,
      "create/emails.py"])
call(["py.test-3.6", "--junitxml",
      "%sdomaincontroller_result.xml" % results_xml,
      "create/domaincontroller.py"])
call(["py.test-3.6", "--junitxml", "%suser_result.xml" % results_xml,
      "create/user.py"])
call(["py.test-3.6", "--junitxml",
      "%sftp_result.xml" % results_xml,
      "create/ftp.py"])
call(["py.test-3.6", "--junitxml",
      "%sgroup_result.xml" % results_xml,
      "create/group.py"])
call(["py.test-3.6", "--junitxml",
      "%siscsi_result.xml" % results_xml,
      "create/iscsi.py"])
# jails API Broken
# call(["py.test-3.6", "--junitxml",
#        "%sjails_result.xml" % results_xml,
#        "create/jails.py"])
call(["py.test-3.6", "--junitxml",
      "%sldap_bsd_result.xml" % results_xml,
      "create/ldap_bsd.py"])
call(["py.test-3.6", "--junitxml",
      "%sldap_osx_result.xml" % results_xml,
      "create/ldap_osx.py"])
call(["py.test-3.6", "--junitxml",
      "%slldp_result.xml" % results_xml,
      "create/lldp.py"])
call(["py.test-3.6", "--junitxml",
      "%snfs_result.xml" % results_xml,
      "create/nfs.py"])
call(["py.test-3.6", "--junitxml",
      "%rsync_result.xml" % results_xml,
      "create/rsync.py"])
# call(["py.test-3.6", "--junitxml",
#        "%smarttest_result.xml" % results_xml,
#        "create/smarttest.py"])
call(["py.test-3.6", "--junitxml",
      "%ssmb_bsd_result.xml" % results_xml,
      "create/smb_bsd.py"])
call(["py.test-3.6", "--junitxml",
      "%ssmb_osx_result.xml" % results_xml,
      "create/smb_osx.py"])
call(["py.test-3.6", "--junitxml",
      "%ssnmp_result.xml" % results_xml,
      "create/snmp.py"])
call(["py.test-3.6", "--junitxml",
      "%ssystem_result.xml" % results_xml,
      "create/system.py"])
call(["py.test-3.6", "--junitxml",
      "%stftp_result.xml" % results_xml,
      "create/tftp.py"])
call(["py.test-3.6", "--junitxml",
      "%sups_result.xml" % results_xml,
      "create/ups.py"])
call(["py.test-3.6", "--junitxml",
      "%swebdav_bsd_result.xml" % results_xml,
      "create/webdav_bsd.py"])
call(["py.test-3.6", "--junitxml",
      "%swebdav_osx_result.xml" % results_xml,
      "create/webdav_osx.py"])

# Update test

call(["py.test-3.6", "--junitxml",
      "%supdate_ad_bsd_result.xml" % results_xml,
      "update/ad_bsd.py"])
call(["py.test-3.6", "--junitxml",
      "%supdate/ad_osx_result.xml" % results_xml,
      "update/ad_osx.py"])
