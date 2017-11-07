#!/usr/bin/env sh

vm_setup()
{
  if [ ! -d "/usr/local/share/trueos" ] ; then
    echo "Host is not running TrueOS!"
    exit 1
  fi
  if [ ! -f "/usr/local/etc/init.d/ixautomation" ] ; then
    cp ${cwd}/init.d/ixautomation /usr/local/etc/init.d/ixautomation
  fi
  if [ ! -f "/etc/runlevels/default/ixautomation" ] ; then
    rc-update add ixautomation
  fi
  if [ ! -f "/libexec/rc/init.d/started/ixautomation" ] ; then
    service ixautomation start
  fi
  if [ ! -f "/libexec/rc/init.d/started/ixautomation" ] ; then
    exit 1
  fi
  $VM_BHYVE init
}

vm_select_iso()
{
  export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
  if [ -z "$SYSTYPE" ]; then
    echo "Please specify SYSTYPE as freenas, trueos, etc"
    exit 1
  fi
  if [ -n "$USING_JENKINS" ] ; then return 0 ; fi
  [ -z "${IXBUILD_ROOT_ZVOL}" ] && export IXBUILD_ROOT_ZVOL="tank"

  # If we aren't running as part of the build process, list ISOs in the $ISODIR
  if [ -z "$SFTPHOST" -o -z "$SFTPUSER" ] ; then

  # Default to prompting for ISOs from ./ixbuild/freenas/iso/*
  if [ -n "$USING_JENKINS" ] ; then
    local ISODIR="${WORKSPACE/artifacts/iso}"
  else
    local ISODIR="${PROGDIR}/vms/.iso/"
  fi

  # [ ! -d "${ISODIR}" ] && "Directory not found: ${ISODIR}" && exit_clean
  if [ ! -d "${ISODIR}" ] ; then
    echo "Please create ${ISODIR} directory first"
    exit_clean
  fi

  # List ISOs in ${ISODIR} and allow the user to select the target
  iso_cnt=`cd ${ISODIR} && ls -l ${SYSNAME}*.iso 2>/dev/null | wc -l | sed 's| ||g'`

  # Download the latest FreeNas ISO if no ISO found in $ISODIR
  if [ $iso_cnt -lt 1 ] ; then
    echo -n "No local ISO found would you like to fetch the latest ${SYSNAME} ISO? (y/n): "
    read download_confirmed
    if test -n "${download_confirmed}" && test "${download_confirmed}" = "y" ; then
      cd ${ISODIR}
      echo "Fetching $iso_name..."
      fetch $iso_url
      USER=$(sh -c 'echo ${SUDO_USER}')
      #.if.$USER.is.empty.we.are.not.running.with.sudo.get.the.real.username
      if [ -z "$USER" ] ; then
        USER=$(id -nu)
      fi
      chown $USER ${SYSNAME}*.iso
      cd -
    else
      echo "Please put a ${SYSNAME} ISO in \"${ISODIR}\""
      exit_clean
    fi
  fi

  # Repopulate the list of ISOs in ${ISODIR} and allow the user to select the target
  iso_cnt=`cd ${ISODIR} && ls -l ${SYSNAME}*.iso 2>/dev/null | wc -l | sed 's| ||g'`

  # Our to-be-determined file name of the ISO to test; must be inside $ISODIR
  local iso_name=""

  # If there's only one ISO in the $ISODIR, assume it's for testing.
  if [ $iso_cnt -eq 1 ] ; then
    # Snatch the first (only) ISO listed in the directory
    iso_name="$(cd "${ISODIR}" && ls -l ${SYSNAME}*.iso | awk 'NR == 1 {print $9}')"
  else
    # Otherwise, loop until we get a valid user selection
    while :
    do
    echo "Please select which ISO to test (1-$iso_cnt):"

    # Listing ISOs in the ./freenas/iso/ directory, numbering the results for selection
    ls -l "${ISODIR}"${SYSNAME}*.iso | awk 'BEGIN{cnt=1} {print "    ("cnt") "$9; cnt+=1}'
    echo -n "Enter your selection and press [ENTER]: "

    # Prompt user to determine which ISO to use
    read iso_selection

    # Only accept integer chars for our ISO selection
    iso_selection=${iso_selection##*[!0-9]*}

    # If an invalid selection, notify the user, pause briefly and then re-prompt for a selection
      if [ -z $iso_selection ] || [ $iso_selection -lt 1 ] || [ $iso_selection -gt $iso_cnt ] 2>/dev/null; then
        echo -n "Invalid selection.." && sleep 1 && echo -n "." && sleep 1 && echo "."
        elif [ -n "`echo $iso_selection | sed 's| ||g'`" ] ; then

        # Confirm our user's ISO selection with another prompt
        iso_name="$(cd "${ISODIR}" && ls -l ${SYSNAME}*.iso | awk 'FNR == '$iso_selection' {print $9}')"
        printf "You have selected \"${iso_name}\", is this correct? (y/n): "
        read iso_confirmed

          if test -n "${iso_confirmed}" && test "${iso_confirmed}" = "y" ; then
          break
          fi
        fi
      done
    fi
  fi

  # Copy selected ISO to temporary location for VM
  if [ -n "$USING_JENKINS" ] ; then
    $VM_BHYVE iso ${ISODIR}/${iso_name}
  fi
  $VM_BHYVE create -t ${SYSTYPE} ${VM}
  $VM_BHYVE install ${VM} ${iso_name}
}

vm_start()
{
export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
${VM_BHYVE} start ${VM}
sleep 5
}

vm_stop()
{
export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
yes | ${VM_BHYVE} stop ${VM}
sleep 10
}

vm_install()
{
  export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
  # Get console device for newly created VM
  sleep 1
  local VM_OUTPUT="/tmp/${VM}console.log"

  # Run our expect/tcl script to automate the installation dialog
  ${PROGDIR}/${SYSTYPE}/bhyve-installer.exp "$VM_BHYVE" "${VM}" "${VM_OUTPUT}"
  echo -e \\033c # Reset/clear to get native term dimensions
  echo "Success: Shutting down the installation VM.."
  vm_stop
}

vm_boot()
{
  vm_start
  export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
  # Get console device for newly created VM
  sleep 1
  local COM_LISTEN=`cat ${vm_dir}/${VM}/console | cut -d/ -f3`
  local VM_OUTPUT="/tmp/${VM}console.log"
  ${PROGDIR}/${SYSTYPE}/bhyve-bootup.exp "${VM_BHYVE}" "${VM}" "${VM_OUTPUT}"

  echo -e \\033c # Reset/clear to get native term dimensions

  if grep -q "Starting nginx." ${VM_OUTPUT} || grep -q "Plugin loaded: SSHPlugin" ${VM_OUTPUT} ; then
    export FNASTESTIP="$(awk '$0 ~ /^vtnet0:\ flags=/ {++n;next}; n == 1 && $1 == "inet" {print $2;exit}' ${VM_OUTPUT})"
  if [ -n "${FNASTESTIP}" ] ; then
    echo "FNASTESTIP=${FNASTESTIP}"
  else
    echo "FNASTESTIP=0.0.0.0"
    echo "ERROR: No ip address assigned to VM. FNASTESTIP not set."
    fi
  fi
}

vm_destroy()
{
  export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
  yes | $VM_BHYVE poweroff ${VM}
  sleep 5
  yes | $VM_BHYVE destroy ${VM}
}

vm_stop_all()
{
  $VM_BHYVE stopall
}

vm_destroy_all()
{
  rm -rf $vm_dir/*
}

