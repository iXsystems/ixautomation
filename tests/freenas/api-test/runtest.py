#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

from subprocess import call
from sys import argv
from os import path, getcwd, makedirs
import getopt

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

call(["py.test-3.6", "--junitxml", "%snetwork_result.xml" % results_xml, "network.py"])
call(["py.test-3.6", "--junitxml", "%sssh_result.xml" % results_xml, "ssh.py"])
call(["py.test-3.6", "--junitxml", "%sstorage_result.xml" % results_xml, "storage.py"])
call(["py.test-3.6", "--junitxml", "%sntp_result.xml" % results_xml, "ntp.py"])
call(["py.test-3.6", "--junitxml", "%sad_bsd_result.xml" % results_xml, "ad_bsd.py"])
call(["py.test-3.6", "--junitxml", "%sad_osx_result.xml" % results_xml, "ad_osx.py"])
call(["py.test-3.6", "--junitxml", "%safp_osx_result.xml" % results_xml, "afp_osx.py"])
#call(["py.test-3.6", "--junitxml", "%salerts_result.xml" % results_xml, "alerts.py"])
call(["py.test-3.6", "--junitxml", "%sbootenv_result.xml" % results_xml, "bootenv.py"])
call(["py.test-3.6", "--junitxml", "%scronjob_result.xml" % results_xml, "cronjob.py"])
#call(["py.test-3.6", "--junitxml", "%sdebug_result.xml" % results_xml, "debug.py"])
call(["py.test-3.6", "--junitxml", "%semails_result.xml" % results_xml, "emails.py"])
call(["py.test-3.6", "--junitxml", "%sdomaincontroller_result.xml" % results_xml, "domaincontroller.py"])
call(["py.test-3.6", "--junitxml", "%suser_result.xml" % results_xml, "user.py"])
call(["py.test-3.6", "--junitxml", "%sftp_result.xml" % results_xml, "ftp.py"])
call(["py.test-3.6", "--junitxml", "%sgroup_result.xml" % results_xml, "group.py"])
call(["py.test-3.6", "--junitxml", "%siscsi_result.xml" % results_xml, "iscsi.py"])
# jails API Broken
#call(["py.test-3.6", "--junitxml", "%sjails_result.xml" % results_xml, "jails.py"])
call(["py.test-3.6", "--junitxml", "%sldap_bsd_result.xml" % results_xml, "ldap_bsd.py"])
call(["py.test-3.6", "--junitxml", "%sldap_osx_result.xml" % results_xml, "ldap_osx.py"])
call(["py.test-3.6", "--junitxml", "%slldp_result.xml" % results_xml, "lldp.py"])
call(["py.test-3.6", "--junitxml", "%snfs_result.xml" % results_xml, "nfs.py"])
call(["py.test-3.6", "--junitxml", "%rsync_result.xml" % results_xml, "rsync.py"])
#call(["py.test-3.6", "--junitxml", "%smarttest_result.xml" % results_xml, "smarttest.py"])
call(["py.test-3.6", "--junitxml", "%ssmb_bsd_result.xml" % results_xml, "smb_bsd.py"])
call(["py.test-3.6", "--junitxml", "%ssmb_osx_result.xml" % results_xml, "smb_osx.py"])
call(["py.test-3.6", "--junitxml", "%ssnmp_result.xml" % results_xml, "snmp.py"])
call(["py.test-3.6", "--junitxml", "%ssystem_result.xml" % results_xml, "system.py"])
call(["py.test-3.6", "--junitxml", "%stftp_result.xml" % results_xml, "tftp.py"])
call(["py.test-3.6", "--junitxml", "%sups_result.xml" % results_xml, "ups.py"])

