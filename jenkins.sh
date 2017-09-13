#!/usr/bin/env sh

# Only run as superuser
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

export PROGDIR="`realpath $0 | xargs dirname`"

# Change directory
cd "${PROGDIR}"

# Set the variables
TYPE="${1}"

# Are we using jenkins?
if [ -n "$WORKSPACE" ] ; then
  export USING_JENKINS="YES"
fi

display_usage() {

   cat << EOF
Available Commands:

-- FreeNAS Commands --
freenas-tests            - Runs FreeNAS VM API tests against built release

-- iocage Commands --
iocage-tests             - Run CI from iocage git (Requires pool name)
EOF

}

if [ -z "$1" ] ; then
  display_usage
  exit 1
fi

# Source our functions
cwd="`realpath $0 | xargs dirname`"
. ${cwd}/backend/functions.sh

######################################################

case $TYPE in
            iocage-tests) jenkins_iocage_tests ;;
           freenas-tests) jenkins_freenas_tests ;;
                       *) echo "Invalid command: $1"
                          display_usage
                          exit 1
                          ;;
esac
