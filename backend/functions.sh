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

install_dependencies()
{
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
    echo '%jenkins ALL = NOPASSWD: /ixautomation/jenkins.sh' >> /usr/local/etc/sudoers.d/ixautomation
    echo 'Defaults      env_keep += "SSH_AUTH_SOCK HOME"' >> /usr/local/etc/sudoers.d/ixautomation
  fi

}

install_dependencies_webui()
{
  uname -a | grep "Linux" >/dev/null
  if [ $? -eq 0 ] ; then
    cd ~/ || exit 1
    apt-get -y install openssh-server
    apt-get -y install python-pip
    pip install --upgrade pip
    pip install selenium
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
  if [ ! -d "/tmp/build" ] ; then
     mkdir /tmp/build
  fi
  cd /tmp/build || exit_clean

  MASTERWRKDIR=`mktemp -d /tmp/build/XXXX`

  # Vanilla Checkout
  cocmd="git clone --depth=1 ${GITREPO} ${MASTERWRKDIR}"
  echo "Cloning with: $cocmd"
  $cocmd
  if [ $? -ne 0 ] ; then exit_clean; fi

  cd "${MASTERWRKDIR}" || exit_clean
}

exit_clean()
{
  bhyve_stop
  cleanup_workdir
  exit 0 
}

exit_fail()
{
  bhyve_stop
  cleanup_workdir
  exit 1
}

jenkins_freenas_tests()
{
  trap 'exit_fail' INT
  GITREPO="https://www.github.com/ixsystems/ixbuild.git"
  create_workdir
  bhyve_select_iso
  bhyve_install_iso
  bhyve_boot
  bhyve_stop
  cleanup_workdir
}

jenkins_freenas_api_tests()
{
  trap 'exit_clean' INT
  GITREPO="https://www.github.com/ixsystems/ixbuild.git"
  create_workdir
  bhyve_select_iso
  bhyve_install_iso
  bhyve_boot
  cd "${MASTERWRKDIR}/freenas/api-test" || exit_clean
  python runtest.py -ip ${FNASTESTIP} -password abcd1234 -interface vtnet0
  cd -
}


jenkins_freenas_webui_tests()
{
  export DISPLAY=:0
  if [ -d "/home/webui/ixbuild" ] ; then
    cd /home/webui/ixbuild || exit 1
    git pull
    cd - || exit 1
  else
    if [ ! -d "/home/webui" ] ; then
      mkdir /home/webui
    fi
    git clone -b master https://www.github.com/ixsystems/ixbuild.git /home/webui/ixbuild
  fi
  cd /home/webui/ixbuild/freenas/webui-tests || exit 1
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
  create_workdir
  bhyve_select_iso
  bhyve_install_iso
  #bhyve_boot
  exit_clean
}

jenkins_freebsd_tests()
{
  trap 'exit_clean' INT
  create_workdir
  bhyve_select_iso
  bhyve_install_iso
  #bhyve_boot
  exit_clean
}
