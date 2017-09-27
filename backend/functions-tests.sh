#!/usr/bin/env bash

# $1 = Command to run
ssh_test()
{
  export TESTSTDOUT="/tmp/.sshCmdTestStdOut"
  export TESTSTDERR="/tmp/.sshCmdTestStdErr"
  touch $TESTSTDOUT
  touch $TESTSTDERR

  sshserver=${ip}
  if [ -z "$sshserver" ] ; then
    sshserver=$FNASTESTIP
  fi

  if [ -z "$sshserver" ] ; then
    echo "SSH server IP address required for ssh_test()."
    return 1
  fi

  # Test fuser value
  if [ -z "${fuser}" ] ; then
    echo "SSH server username required for ssh_test()."
    return 1
  fi

  ssh -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      -o VerifyHostKeyDNS=no \
      -i ~/.ssh/test_id_rsa \
      root@${sshserver} ${1} >$TESTSTDOUT 2>$TESTSTDERR

  return $?
}

# Export test functions for other tests outside of ixautomation (requires bash)
export -f ssh_test
