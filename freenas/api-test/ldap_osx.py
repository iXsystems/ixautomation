#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD
# Location for tests into REST API of FreeNAS

import unittest
from functions import PUT, POST, GET_OUTPUT, DELETE, DELETE_ALL, return_output
from functions import BSD_TEST
from auto_config import ip

try:
    import config
except ImportError:
    pass
else:
    from config import BRIDGEHOST, BRIDGEDOMAIN, ADPASSWORD, ADUSERNAME
    from config import LDAPBASEDN, LDAPBINDDN, LDAPHOSTNAME, LDAPBINDPASSWORD

DATASET = "ldap-osx"
SMB_NAME = "TestShare"
SMB_PATH = "/mnt/tank/" + DATASET
MOUNTPOINT = "/tmp/ldap-osx" + BRIDGEHOST
VOL_GROUP = "qa"

class ldap_bsd_test(unittest.TestCase):
# Clean up any leftover items from previous failed AD LDAP or SMB runs
  osx_test "umount -f '${MOUNTPOINT}'; rmdir '${MOUNTPOINT}'; exit 0"
  rest_request "PUT" "/directoryservice/activedirectory/1/" '{ "ad_bindpw": "'${ADPASSWORD}'", "ad_bindname": "'${ADUSERNAME}'", "ad_domainname": "'${BRIDGEDOMAIN}'", "ad_netbiosname_a": "'${BRIDGEHOST}'", "ad_idmap_backend": "rid", "ad_enable":"false" }'
  rest_request "PUT" "/directoryservice/ldap/1/" '{ "ldap_basedn": "'${LDAPBASEDN}'", "ldap_anonbind": true, "ldap_netbiosname_a": "'${BRIDGEHOST}'", "ldap_hostname": "'${LDAPHOSTNAME}'", "ldap_has_samba_schema": true, "ldap_enable": false }'
  rest_request "PUT" "/services/services/cifs/" '{ "srv_enable": false }'
  rest_request "DELETE" "/sharing/cifs/" '{ "cfs_comment": "My Test SMB Share", "cifs_path": "'"${SMB_PATH}"'", "cifs_name": "'"${SMB_NAME}"'", "cifs_guestok": true, "cifs_vfsobjects": "streams_xattr" }'
  rest_request "DELETE" "/storage/volume/1/datasets/${DATASET}/"

  # Set auxilary parameters to allow mount_smbfs to work with ldap
  echo_test_title "Creating SMB dataset"
  rest_request "POST" "/storage/volume/${IXBUILD_ROOT_ZVOL}/datasets/" '{ "name": "'"${DATASET}"'" }'
  check_rest_response "201 Created"

  # Enable LDAP
  echo_test_title "Enabling LDAP with anonymous bind.."
  rest_request "PUT" "/directoryservice/ldap/1/" '{ "ldap_basedn": "'${LDAPBASEDN}'", "ldap_anonbind": true, "ldap_netbiosname_a": "'${BRIDGEHOST}'", "ldap_hostname": "'${LDAPHOSTNAME}'", "ldap_has_samba_schema": true, "ldap_enable": true }'
  check_rest_response "200 OK"

  # Check LDAP
  echo_test_title "Checking LDAP.."
  rest_request GET "/directoryservice/ldap/"
  check_property_value "return this.ldap_enable" "true"

  echo_test_title "Enabling SMB service"
  rest_request "PUT" "/services/cifs/" '{ "cifs_srv_description": "Test FreeNAS Server", "cifs_srv_guest": "nobody", "cifs_hostname_lookup": false, "cifs_srv_aio_enable": false }'
  check_rest_response "200 OK"

  # Now start the service
  echo_test_title "Starting SMB service"
  rest_request "PUT" "/services/services/cifs/" '{ "srv_enable": true }'
  check_rest_response "200 OK"

  echo_test_title "Verifying that SMB service has started"
  wait_for_avail_port "445"
  check_exit_status || return 1

  echo_test_title "Checking to see if SMB service is enabled"
  rest_request "GET" "/services/services/cifs/"
  check_service_status "RUNNING"

  echo_test_title "Changing permissions on ${SMB_PATH}"
  rest_request "PUT" "/storage/permission/" '{ "mp_path": "'"${SMB_PATH}"'", "mp_acl": "unix", "mp_mode": "777", "mp_user": "root", "mp_group": "qa", "mp_recursive": true }'
  check_rest_response "201 Created"

  echo_test_title "Creating a SMB share on ${SMB_PATH}"
  rest_request "POST" "/sharing/cifs/" '{ "cfs_comment": "My Test SMB Share", "cifs_path": "'"${SMB_PATH}"'", "cifs_name": "'"${SMB_NAME}"'", "cifs_guestok": true, "cifs_vfsobjects": "streams_xattr" }'
  check_rest_response "201 Created" || return 1

  local vol_name=$(dirname "${SMB_PATH}")
  echo_test_title "Checking permissions on ${SMB_NAME}"
  ssh_test "ls -la '${vol_name}' | awk '\$4 == \"${VOL_GROUP}\" && \$9 == \"${DATASET}\" ' "
  check_exit_status || return 1   

  if [ -n "${OSX_HOST}" -a -n "${BRIDGEIP}" ]; then
    # Mount share on OSX system and create a test file
    echo_test_title "Create mount-point for SMB on OSX system"
    osx_test "mkdir -p '${MOUNTPOINT}'"
    check_exit_status || return 1

    echo_test_title "Mount SMB share on OSX system"
    osx_test "mount -t smbfs 'smb://ldapuser:12345678@${BRIDGEIP}/${SMB_NAME}' ${MOUNTPOINT}"
    check_exit_status || return 1

    echo_test_title "Verify SMB share mounted on OSX system"
    wait_for_osx_mnt "${MOUNTPOINT}"
    check_exit_status || return 1

    local device_name=`dirname "${MOUNTPOINT}"`
    echo_test_title "Checking permissions on ${MOUNTPOINT}"
    osx_test "time ls -la '${device_name}' | awk '\$4 == \"${VOL_GROUP}\" && \$9 == \"${DATASET}\" ' "
    check_exit_status || return 1

    echo_test_title "Create file on SMB share via OSX to test permissions"
    osx_test "touch '${MOUNTPOINT}/testfile.txt'"
    check_exit_status || return 1

    # Move test file to a new location on the SMB share
    echo_test_title "Moving SMB test file into a new directory"
    osx_test "mkdir -p '${MOUNTPOINT}/tmp' && mv '${MOUNTPOINT}/testfile.txt' '${MOUNTPOINT}/tmp/testfile.txt'"
    check_exit_status || return 1

    # Delete test file and test directory from SMB share
    echo_test_title "Deleting test file and directory from SMB share"
    osx_test "rm -f '${MOUNTPOINT}/tmp/testfile.txt' && rmdir '${MOUNTPOINT}/tmp'"
    check_exit_status || return 1

    echo_test_title "Verifying that test file and directory were successfully removed"
    osx_test "find -- '${MOUNTPOINT}/' -prune -type d -empty | grep -q ."
    check_exit_status || return 1

    # Clean up mounted SMB share
    echo_test_title "Unmount SMB share"
    osx_test "umount -f '${MOUNTPOINT}'"
    check_exit_status || return 1
  fi

  # Disable LDAP
  echo_test_title "Disabling LDAP with anonymous bind.."
  rest_request "PUT" "/directoryservice/ldap/1/" '{ "ldap_basedn": "'${LDAPBASEDN}'", "ldap_anonbind": true, "ldap_netbiosname_a": "'${BRIDGEHOST}'", "ldap_hostname": "'${LDAPHOSTNAME}'", "ldap_has_samba_schema": true, "ldap_enable": false }'
  check_rest_response "200 OK"

  # Now stop the SMB service
  echo_test_title "Stopping SMB service"
  rest_request "PUT" "/services/services/cifs/" '{ "srv_enable": false }'
  check_rest_response "200 OK"

  # Check LDAP
  echo_test_title "Verify LDAP is disabled.."
  rest_request GET "/directoryservice/ldap/"
  check_property_value "return this.ldap_enable" "false"

  echo_test_title "Verify SMB service is disabled"
  rest_request "GET" "/services/services/cifs/"
  check_service_status "STOPPED"

  # Check destroying a SMB dataset
  echo_test_title "Destroying SMB dataset"
  rest_request "DELETE" "/storage/volume/1/datasets/${DATASET}/"
  check_rest_response "204" || return 1


if __name__ == "__main__":
    unittest.main(verbosity=2)
