#!/usr/bin/env sh

# Set the build tag
BUILDTAG="$BUILD"
export BUILDTAG

exit_err() {
   echo "ERROR: $@"
   exit 1
}

# Run-command, halt if command exits with non-0
rc_halt()
{
  local CMD="$1"
  if [ -z "${CMD}" ]; then
    exit_err "Error: missing argument in rc_halt()"
  fi

  echo "Running command: $CMD"
  ${CMD}
  if [ $? -ne 0 ]; then
    exit_err "Error ${STATUS}: ${CMD}"
  fi
};

install_dependencies()
{
  which git >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing git.."
    rc_halt "pkg-static install -y git"
  fi

  which curl >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing ftp/curl.."
    rc_halt "pkg-static install -y curl"
  fi

  which bash >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing shells/bash.."
    rc_halt "pkg-static install -y bash"
  fi

  which expect >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing shells/expect..."
    rc_halt "pkg-static install -y expect"
  fi

  which js24 >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing lang/spidermonkey24.."
    rc_halt "pkg-static install -y spidermonkey24"
  fi

  which wget >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing wget.."
    rc_halt "pkg-static install -y wget"
  fi

  which sshpass >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing security/sshpass"
    rc_halt "pkg-static install -y sshpass"
  fi

  which rsync >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing net/rsync"
    rc_halt "pkg-static install -y rsync"
  fi

  if [ ! -f "/usr/local/share/uefi-firmware/BHYVE_UEFI.fd" ] ; then
  echo "Installing sysutils/bhyve-firmware"
    rc_halt "pkg-static install -y bhyve-firmware"
  fi

  if [ ! -f "/usr/local/etc/sudoers.d/ixautomation" ] ; then
    touch /usr/local/etc/sudoers.d/ixautomation
    echo 'Defaults      env_keep += "SSH_AUTH_SOCK"' > /usr/local/etc/sudoers.d/ixautomation
  fi

}

cleanup_workdir()
{
  if [ -n "$USING_JENKINS" ] ; then return 0 ; fi
  if [ -z "$MASTERWRKDIR" ] ; then return 0 ; fi
  if [ ! -d "$MASTERWRKDIR" ] ; then return 0 ; fi
  if [ "$MASTERWRKDIR" = "/" ] ; then return 0 ; fi

  # If running on host, lets cleanup
    # Cleanup any leftover mounts
    for i in `mount | grep -q "on ${MASTERWRKDIR}/" | awk '{print $1}' | tail -r`
    do
      umount -f $i
    done

  # Should be done with unmounts
  mount | grep -q "on ${MASTERWRKDIR}/"
  if [ $? -ne 0 ] ; then
    rm -rf ${MASTERWRKDIR} 2>/dev/null
    chflags -R noschg ${MASTERWRKDIR} 2>/dev/null
    rm -rf ${MASTERWRKDIR}
  fi
}

create_workdir()
{
  if [ -n "$USING_JENKINS" ] ; then return 0 ; fi
  if [ ! -d "/tmp/build" ] ; then
     mkdir /tmp/build
  fi
  cd /tmp/build

  MASTERWRKDIR=`mktemp -d /tmp/build/XXXX`

  # Vanilla Checkout
  cocmd="git clone --depth=1 ${GITREPO} ${MASTERWRKDIR}"
  echo "Cloning with: $cocmd"
  $cocmd
  if [ $? -ne 0 ] ; then exit_clean; fi

  cd ${MASTERWRKDIR}
  if [ $? -ne 0 ] ; then exit_clean; fi
}

exit_clean()
{
  bhyve_stop
  cleanup_workdir
  exit 1
}

start_ssh_agent()
{
  # look is rsa key exist
  ls -al ~/.ssh | grep -q -e 'test_id_rsa.pub'
  if [ $? -eq 1 ]; then
    ssh-keygen -t rsa -f ~/.ssh/test_id_rsa -q -N ""
  fi
  # look if ssh_agent is runnig
  ssh-add -L | grep -q -e "Error connecting to agent" -e "Could not open a connection to your authentication agent."
  if [ $? -eq 0 ]; then
    ssh-agent csh
  fi
  # If the agent has no identities add rsa
  ssh-add -L | grep -q -e "The agent has no identities."
  if [ $? -eq 0 ]; then
    ssh-add .ssh/test_id_rsa
  fi
  ssh-add -L | grep -q -e "Error connecting to agent" -e "Could not open a connection to your authentication agent." -e "The agent has no identities."
  if [ $? -eq 0 ]; then
    echo "Starting ssh agent failed"
    exit_clean
  fi
}

jenkins_freenas_tests()
{
  trap 'exit_clean' INT
  export TESTSYSTEM="FreeNAS"
  GITREPO="-b feature-bhyve https://www.github.com/ixsystems/ixbuild.git"
  create_workdir
  bhyve_select_iso
  bhyve_install_iso
  start_ssh_agent
  bhyve_boot
  if [ -z $FNASTESTIP ] ; then exit_clean ; fi
  # Since we are runnig in bhyve populat VMBACKEND for starage test
  export VMBACKEND="bhyve"
  export BRIDGEIP="${FNASTESTIP}"
  cd ${MASTERWRKDIR}/freenas/scripts
  if [ $? -ne 0 ] ; then exit_clean ; fi
  echo ""
  sleep 10
  pkill -F /tmp/vmcu.pid >/dev/null 2>/dev/null
  echo ""
  echo "Output from REST API calls:"
  echo "-----------------------------------------"
  echo "Running API v1.0 test group create 1/3"
  touch /tmp/$VM-tests-create.log 2>/dev/null
  tail -f /tmp/$VM-tests-create.log 2>/dev/null &
  tpid=$!
  ./9.10-create-tests.sh ip=$FNASTESTIP 2>&1 | tee >/tmp/$VM-tests-create.log
  kill -9 $tpid
  echo ""
  echo "Running API v1.0 test group update 2/3"
  touch /tmp/$VM-tests-update.log 2>/dev/null
  tail -f /tmp/$VM-tests-update.log 2>/dev/null &
  tpid=$!
  ./9.10-update-tests.sh ip=$FNASTESTIP 2>&1 | tee >/tmp/$VM-tests-update.log
  kill -9 $tpid
  echo ""
  echo "Running API v1.0 test group delete 3/3"
  touch /tmp/$VM-tests-delete.log 2>/dev/null
  tail -f /tmp/$VM-tests-delete.log 2>/dev/null &
  tpid=$!
  ./9.10-delete-tests.sh ip=$FNASTESTIP 2>&1 | tee >/tmp/$VM-tests-delete.log
  kill -9 $tpid
  echo ""
  sleep 10
  exit_clean
}

jenkins_freenas_webui_tests()
{
  export DISPLAY=:0
  if [ -d "/home/webui/ixbuild" ] ; then
    git pull
  else
    git clone -b master https://www.github.com/ixsystems/ixbuild.git /home/webui/ixbuild
  fi
  cd ~/ixbuild/freenas/webui-tests/
  python runtest.py
}

jenkins_iocage_tests()
{
  GITREPO="https://www.github.com/iocage/iocage"
  create_workdir
  cleanup_workdir
}

jenkins_trueos_tests()
{
  trap 'exit_clean' INT
  export TESTSYSTEM="TrueOS"
  GITREPO="-b feature-bhyve https://www.github.com/ixsystems/ixbuild.git"
  create_workdir
  bhyve_select_iso
  bhyve_install_iso
  start_ssh_agent
  #bhyve_boot
  #if [ -z $FNASTESTIP ] ; then exit_clean ; fi
  exit_clean
}

jenkins_trueview_webui_tests()
{
  echo "To be added later"
}

jenkins_sysadm_cli_tests()
{
  echo "To be added later"
}

