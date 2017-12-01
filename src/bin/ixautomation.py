#!/usr/bin/env python3.6

import os
import sys
import getpass
import getopt
sys.path.append("/usr/local/lib/ixautomation")
# Source our functions
from functions import jenkins_vm_tests



loginUser = os.getlogin()
curentUser = getpass.getuser()

if curentUser != "root":
    print("This script must be run as root")
    sys.exit(1)

UsageMSG = """Usage for %s:
Available Commands:

** iXautomation Commands **
--bootstrap               - Install all the packages need for iXautomation
--bootstrap-webui         - Install all the packages need for iXautomation webui

** FreeNAS Commands **
--freenas-webui-tests     - Runs FreeNAS webui tests using webdriver

** iocage Commands **
--iocage-tests            - Run CI from iocage git (Requires pool name)

** API test Commands **
--api-tests               - Runs Python API tests (freenas or trueos)

** VM Commands **
--tests-vm <system>       - Runs a (freenas, or trueos) in a VM using vm-bhyve
--start-vm <system>       - Start a VM with (freenas, or trueos)
--destroy-all-vm          - Destroy all vm created
""" % sys.argv[0]

# if have no argumment stop
if len(sys.argv) == 1:
    print(UsageMSG)
    exit()

# list of argument that chould be use.
listofoption = ["testsv-vm", "api-tests", "start-vm", "destroy-all-vm"]

# look if all the argument are there.
try:
    myopts, args = getopt.getopt(sys.argv[1:], 'ipI', listofoption)
except getopt.GetoptError as e:
    print(str(e))
    print(UsageMSG)
    exit()

for output, arg in myopts:
    if output in ('-i', '--ip'):
        ip = arg
    elif output in ('-p', '--password'):
        passwd = arg
    elif output in ('-I', '--interface'):
        interface = arg

######################################################

# case $TYPE in
#                    bootstrap) bootstrap()
#              bootstrap-webui) bootstrap_webui() ;;
#                    api-tests) jenkins_api_tests();;
#          freenas-webui-tests) jenkins_freenas_webui_tests ;;
#                 iocage-tests) jenkins_iocage_tests ;;
#                     vm-tests) jenkins_vm_tests ;;
#                     start-vm) jenkins_start_vm ;;
#               vm-destroy-all) jenkins_vm_destroy_all ;;
#                            *) echo "Invalid command: $1"
#                               display_usage
#                               exit 1
#                               ;;
# esac
