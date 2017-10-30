#!/usr/bin/env sh

# Only run as superuser
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Command to fiter $2 output to determine which test folder and config to source

SYSTYPE="${2}"

if [ -f "${cwd}/${SYSTYPE}/${SYSTYPE}.cfg" ] ; then
  echo "##########################################"
. "${cwd}/${SYSTYPE}/${SYSTYPE}.cfg"
fi

PROGDIR="$(realpath "$0" | xargs dirname)"
export PROGDIR

# Set the variables for jenkins.sh
TYPE="${1}"

# Set the variables for vm-bhyve
export VM_BHYVE="${PROGDIR}/utils/vm-bhyve/vm-bhyve"
export LIB="${PROGDIR}/utils/vm-bhyve/lib"
export vm_dir="${PROGDIR}/vms"

# Are we using jenkins?
if [ -n "$WORKSPACE" ] ; then
  export USING_JENKINS="YES"
fi

display_usage() {

   cat << EOF
Available Commands:

-- iXautomation Commands --
install-dependencies         - Install all the packages need for iXautomation
install-dependencies-webui   - Install all the packages need for iXautomation webui

-- FreeNAS Commands --
freenas-api-tests         - Runs FreeNAS VM Python API tests against built release
freenas-webui-tests          - Runs FreeNAS webui tests using webdriver

-- iocage Commands --
iocage-tests                 - Run CI from iocage git (Requires pool name)

-- VM Commands --
vm-test                      - Runs a SYSTYPE in a VM using vm-bhyve (freebsd, freenas, or trueos)

EOF

}

if [ -z "$1" ] ; then
  display_usage
  exit 1
fi

# Source our functions
cwd="$(realpath "$0" | xargs dirname)"
. backend/functions.sh
. backend/functions-vm.sh

# Set the variables for vm-bhyve
export VM_BHYVE="${PROGDIR}/utils/vm-bhyve/vm-bhyve"
export LIB="${PROGDIR}/utils/vm-bhyve/lib"
export vm_dir="${PROGDIR}/vms"

######################################################

case $TYPE in
        install-dependencies) install_dependencies ;;
  install-dependencies-webui) install_dependencies_webui ;;
        freenas-api-tests) jenkins_freenas_api_tests;;
         freenas-webui-tests) jenkins_freenas_webui_tests ;;
                iocage-tests) jenkins_iocage_tests ;;
                trueos-tests) jenkins_trueos_tests ;;
               freebsd-tests) jenkins_freebsd_tests ;;
                    vm-tests) jenkins_vm_tests ;;
              vm-destroy-all) jenkins_vm_destroy_all ;;
                           *) echo "Invalid command: $1"
                              display_usage
                              exit 1
                              ;;
esac
