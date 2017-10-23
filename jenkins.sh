#!/usr/bin/env sh

# Only run as superuser
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Command to fiter $2 output to determine which test folder and config to source

SYSTYPE="${2}"

# Source our functions

cwd="$(realpath "$0" | xargs dirname)"
. "${cwd}/backend/functions-vm.sh"

if [ -f "${cwd}/${SYSTYPE}/${SYSTYPE}.cfg" ] ; then
  echo "##########################################"
. "${cwd}/${SYSTYPE}/${SYSTYPE}.cfg"
fi

PROGDIR="$(realpath "$0" | xargs dirname)"
export PROGDIR

# Change directory
cd "${PROGDIR}" || exit

# Set the variables
TYPE="${1}"

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
freenas-tests                - Runs FreeNAS VM API tests against built release
freenas-api-tests         - Runs FreeNAS VM Python API tests against built release
freenas-webui-tests          - Runs FreeNAS webui tests using webdriver

-- iocage Commands --
iocage-tests                 - Run CI from iocage git (Requires pool name)

-- TrueOS Commands --
trueos-tests                 - Runs TrueOS VM tests

-- FreeBSD Commands --
freebsd-tests                - Runs FreeBSD VM test

EOF

}

if [ -z "$1" ] ; then
  display_usage
  exit 1
fi

# Source our functions
cwd="$(realpath "$0" | xargs dirname)"
. "${cwd}/backend/functions.sh"

######################################################

case $TYPE in
        install-dependencies) install_dependencies ;;
  install-dependencies-webui) install_dependencies_webui ;;
               freenas-tests) jenkins_freenas_tests ;;
        freenas-api-tests) jenkins_freenas_api_tests;;
         freenas-webui-tests) jenkins_freenas_webui_tests ;;
                iocage-tests) jenkins_iocage_tests ;;
                trueos-tests) jenkins_trueos_tests ;;
               freebsd-tests) jenkins_freebsd_tests ;;
                    vm-tests) jenkins_vm_tests ;;
                           *) echo "Invalid command: $1"
                              display_usage
                              exit 1
                              ;;
esac
