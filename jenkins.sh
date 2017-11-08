#!/usr/bin/env sh

# Only run as superuser
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Set the current working directory and program directory
cwd="$(realpath "$0" | xargs dirname)"
export cwd
PROGDIR="$(realpath "$0" | xargs dirname)"
export PROGDIR

# Define our arguments
TYPE="${1}"
SYSTYPE="${2}"
TEST="${3}"
if [ -f "${cwd}/${SYSTYPE}/${SYSTYPE}.cfg" ] ; then
  echo "##########################################"
. "${cwd}/${SYSTYPE}/${SYSTYPE}.cfg"
fi

# Are we using jenkins?
if [ -n "$WORKSPACE" ] ; then
  export USING_JENKINS="YES"
fi

display_usage() {

   cat << EOF
Available Commands:

-- iXautomation Commands --
bootstrap         	     - Install all the packages need for iXautomation
bootstrap-webui              - Install all the packages need for iXautomation webui

-- FreeNAS Commands --
freenas-webui-tests          - Runs FreeNAS webui tests using webdriver

-- iocage Commands --
iocage-tests                 - Run CI from iocage git (Requires pool name)

-- API test Commands --
api-tests                    - Runs FreeNAS VM Python API tests against built release (freenas or trueos)

-- VM Commands --
vm-tests                     - Runs a SYSTYPE in a VM using vm-bhyve (freenas, or trueos)
start-vm                     - Start a VM with SYSTYPE (freenas, or trueos)

EOF

}

if [ -z "$1" ] ; then
  display_usage
  exit 1
fi

# Source our functions
. backend/functions.sh
. backend/functions-vm.sh

# Set the variables for vm-bhyve
export VM_BHYVE="${PROGDIR}/utils/vm-bhyve/vm-bhyve"
export LIB="${PROGDIR}/utils/vm-bhyve/lib"
export vm_dir="${PROGDIR}/vms"

######################################################

case $TYPE in
                   bootstrap) bootstrap ;;
  	     bootstrap-webui) bootstrap_webui ;;
                   api-tests) jenkins_api_tests;;
         freenas-webui-tests) jenkins_freenas_webui_tests ;;
                iocage-tests) jenkins_iocage_tests ;;
                    vm-tests) jenkins_vm_tests ;;
                    start-vm) jenkins_start_vm ;;
              vm-destroy-all) jenkins_vm_destroy_all ;;
                           *) echo "Invalid command: $1"
                              display_usage
                              exit 1
                              ;;
esac

