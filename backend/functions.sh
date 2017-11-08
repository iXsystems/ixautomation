#!/usr/bin/env sh

# Set the build tag
BUILDTAG="$BUILD"
export BUILDTAG

exit_err() {
   echo "ERROR: $*"
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

bootstrap()
{
  if [ ! -d "/usr/local/share/trueos" ] ; then
    echo "Host is not running TrueOS!"
    exit 1
  fi
  if ! which git >/dev/null 2>/dev/null
  then
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
    ECho "Installing shells/bash.."
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

  which rsync >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing net/rsync"
    rc_halt "pkg-static install -y rsync"
  fi

  if [ ! -f "/usr/local/share/uefi-firmware/BHYVE_UEFI.fd" ] ; then
  echo "Installing sysutils/bhyve-firmware"
    rc_halt "pkg-static install -y bhyve-firmware"
  fi

  which python3.6 >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing lang/python36"
    rc_halt "pkg-static install -y python36"
  fi

  which py.test-3.6 >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing devel/py3-pytest"
    rc_halt "pkg-static install -y py36-pytest"
  fi

  find /usr/local/lib -name requests | grep requests >/dev/null
  if [ "$?" != "0" ]; then
    echo "Installing www/py3-requests"
    rc_halt "pkg-static install -y py36-requests"
  fi

  if [ ! -f "/usr/local/etc/sudoers.d/ixautomation" ] ; then
    cp sudoers.d/ixautomation /usr/local/etc/sudoers.d/ixautomation
  fi

}

bootstrap_webui()
{
  uname -a | grep "Linux" >/dev/null
  if [ $? -eq 0 ] ; then
    cd ~/ || exit 1
    apt-get -y install openssh-server
    apt-get -y install python-pip
    pip install --upgrade pip
    pip install selenium
    pip install unittest-xml-reporting
    apt-get -y install python-pytest
    apt-get -y install curl
    #download firefox webdriver
    git clone https://github.com/rishabh27892/webui-test-files/
    cd webui-test-files/ || exit 1
    tar -xvzf geckodriver-v0.11.1-linux64.tar.gz
    chmod +x geckodriver
    sudo cp geckodriver /usr/local/bin/
    cd ~/ || exit 1
    rm -rf webui-test-files
  fi
  if uname -a | grep "FreeBSD" >/dev/null
  then
    if [ ! -d "/usr/local/share/trueos" ] ; then
      echo "Host is not running TrueOS!"
      exit 1
    fi
    if ! which python3.6 >/dev/null 2>/dev/null
    then
      echo "Installing lang/python36"
      rc_halt "pkg-static install -y python36"
      rc_halt "ln -f /usr/local/bin/python3.6 /usr/local/bin/python"
    else
      rc_halt "ln -f /usr/local/bin/python3.6 /usr/local/bin/python"
    fi
    which pip-3.6 >/dev/null 2>/dev/null
    if [ "$?" != "0" ]; then
      echo "Installing devel/py36-pip"
      rc_halt "pkg-static install -y py36-pip"
    fi
    which py.test-3.6 >/dev/null 2>/dev/null
    if [ "$?" != "0" ]; then
      echo "Installing devel/py36-pytest"
      rc_halt "pkg-static install -y py36-pytest"
      rc_halt "ln -f /usr/local/bin/py.test-3.6 /usr/local/bin/py.test"
    fi
    which geckodriver >/dev/null 2>/dev/null
    if [ "$?" != "0" ]; then
      echo "Installing www/geckodriver"
      rc_halt "pkg-static install -y geckodriver"
    fi
    find /usr/local/lib -name selenium | grep selenium >/dev/null
    if [ "$?" != "0" ]; then
      echo "Installing selenium"
      rc_halt "pip-3.6 install selenium"
    fi
    find /usr/local/lib -name xmlrunner | grep selenium >/dev/null
    if [ "$?" != "0" ]; then
      echo "Installing selenium"
      rc_halt "pip-3.6 install unittest-xml-reporting"
    fi

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
    for i in $(mount | grep -q "on ${MASTERWRKDIR}/" | awk '{print $1}' | tail -r)
    do
      umount -f "$i"
    done

  # Should be done with unmounts
  if ! mount | grep -q "on ${MASTERWRKDIR}/"
  then
    rm -rf "${MASTERWRKDIR}" 2>/dev/null
    chflags -R noschg "${MASTERWRKDIR}" 2>/dev/null
    rm -rf "${MASTERWRKDIR}"
  fi
}

create_workdir()
{
  if [ -n "$USING_JENKINS" ] ; then return 0 ; fi

  MASTERWRKDIR=$(mktemp -d ${cwd}/build/XXXX)
  #if [ $? -ne 0 ] ; then exit_clean; fi

  cd "${MASTERWRKDIR}" || exit_clean
}

exit_clean()
{
  vm_destroy
  cleanup_workdir
  exit 0
}

exit_fail()
{
  vm_destroy
  cleanup_workdir
  exit 1
}

jenkins_vm_tests()
{
  trap 'exit_fail' INT
  GITREPO="https://www.github.com/ixsystems/ixbuild.git"
  create_workdir
  vm_setup
  vm_select_iso
  vm_install
  vm_boot
  if [ "${TEST}" = "api-tests" ]; then
    cd "${cwd}/freenas/api-test" || exit_clean
    python3.6 runtest.py --ip ${FNASTESTIP} --password testing --interface vtnet0
    cd -
  fi
  vm_destroy
  cleanup_workdir
}

jenkins_start_vm()
{
  trap 'exit_fail' INT
  GITREPO="https://www.github.com/ixsystems/ixbuild.git"
  create_workdir
  vm_setup
  vm_select_iso
  vm_install
  vm_boot
}


jenkins_vm_destroy_all()
{
  vm_stop_all
  vm_destroy_all
}

jenkins_api_tests()
{
  trap 'exit_fail' INT
  GITREPO="https://www.github.com/ixsystems/ixbuild.git"
  create_workdir
  vm_setup
  vm_select_iso
  vm_install
  vm_boot
  cd "${cwd}/freenas/api-test" || exit_clean
  python3.6 runtest.py --ip ${FNASTESTIP} --password testing --interface vtnet0
  cd -
  vm_destroy
  cleanup_workdir
}


jenkins_freenas_webui_tests()
{
  export DISPLAY=:0
  cd "${cwd}/freenas/webui-tests" || exit_clean
  python runtest.py
  cd -
}

jenkins_iocage_tests()
{
  GITREPO="https://www.github.com/iocage/iocage"
  create_workdir
  cleanup_workdir
}
