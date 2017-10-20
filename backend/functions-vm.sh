#!/usr/bin/env sh

bridge_setup()
{
  local VM_BRIDGE="bridge0"
  local VM_TAP="tap0"
  local VM_SWITCH="public"
  local VM_IFACE="`netstat -f inet -nrW | grep '^default' | awk '{ print $6 }'`"
  if ! ifconfig ${VM_BRIDGE} >/dev/null 2>/dev/null ; then
    ifconfig bridge create
  fi
  if ! ifconfig ${VM_TAP} >/dev/null 2>/dev/null ; then
  ifconfig tap create
  fi
  if ! ifconfig ${VM_BRIDGE} | grep -q ${VM_TAP} >/dev/null 2>/dev/null ; then
    ifconfig ${VM_BRIDGE} addm ${VM_TAP} 
  fi
  if ! ifconfig ${VM_BRIDGE} | grep -q "member: ${VM_IFACE}" ; then
     ifconfig ${VM_BRIDGE} addm ${VM_IFACE}
  fi
  if ! ifconfig ${VM_BRIDGE} | grep -q UP ; then
     ifconfig ${VM_BRIDGE} up
  fi
  if ! vm switch list | grep -q ${VM_SWITCH} ; then
     vm switch import ${VM_SWITCH} ${VM_BRIDGE}
  fi
  sysrc -f /etc/rc.conf cloned_interfaces="${VM_BRIDGE} ${VM_TAP}"
  sysrc -f /etc/rc.conf ifconfig_${VM_BRIDGE}="addm ${VM_IFACE} addm ${VM_TAP} up"
}

vm_setup()
{
  sysrc -f /etc/rc.conf vm_enable="YES"
  sysrc -f /etc/rc.conf vm_dir="/ixautomation/vms"
  if [ ! -L "/libexec/rc/init.d/started/vm" ] ; then
    service vm start
  fi
  if [ ! -L "/etc/runlevels/default/vm" ] ; then
    rc-update add vm
  fi
}

bhyve_select_iso()
{
  if [ -n "$USING_JENKINS" ] ; then return 0 ; fi
  [ -z "${IXBUILD_ROOT_ZVOL}" ] && export IXBUILD_ROOT_ZVOL="tank"

  # If we aren't running as part of the build process, list ISOs in the $ISODIR
  if [ -z "$SFTPHOST" -o -z "$SFTPUSER" ] ; then

    # Default to prompting for ISOs from ./ixbuild/freenas/iso/*
    if [ -n "$USING_JENKINS" ] ; then
      local ISODIR="${WORKSPACE/artifacts/iso}"
    else
      local ISODIR="${PROGDIR}${iso_folder}"
    fi
    # Allow $ISODIR to be overridden by $IXBUILD_FREENAS_ISODIR if it exists
    if [ -n "${IXBUILD_FREENAS_ISODIR}" ] ; then
      ISODIR="$(echo "${IXBUILD_FREENAS_ISODIR}" | sed 's|/$||g')/"
    elif [ -n "${IXBUILD_TRUEOS_ISODIR}" ] ; then
      ISODIR="$(echo "${IXBUILD_TRUEOS_ISODIR}" | sed 's|/$||g')/"
    fi

    # [ ! -d "${ISODIR}" ] && "Directory not found: ${ISODIR}" && exit_clean
    if [ ! -d "${ISODIR}" ] ; then
      echo "Please create ${ISODIR} directory first"
      exit_clean
    fi

    # List ISOs in ${ISODIR} and allow the user to select the target
    iso_cnt=`cd ${ISODIR} && ls -l *.iso 2>/dev/null | wc -l | sed 's| ||g'`

    # Download the latest FreeNas ISO if no ISO found in $ISODIR
    if [ $iso_cnt -lt 1 ] ; then
      echo -n "No local ISO found would you like to fetch the latest ${SYSNAME} ISO? (y/n): "
      read download_confirmed
      if test -n "${download_confirmed}" && test "${download_confirmed}" = "y" ; then
        cd ${ISODIR}
        echo "Fetching $iso_name..."
        fetch $iso_url
        USER=$(sh -c 'echo ${SUDO_USER}')
        chown $USER *.iso
        cd -
      else
        echo "Please put a ${SYSNAME} ISO in \"${ISODIR}\""
        exit_clean
      fi
    fi

    # Repopulate the list of ISOs in ${ISODIR} and allow the user to select the target
    iso_cnt=`cd ${ISODIR} && ls -l *.iso 2>/dev/null | wc -l | sed 's| ||g'`

    # Our to-be-determined file name of the ISO to test; must be inside $ISODIR
    local iso_name=""

    # If there's only one ISO in the $ISODIR, assume it's for testing.
    if [ $iso_cnt -eq 1 ] ; then
      # Snatch the first (only) ISO listed in the directory
      iso_name="$(cd "${ISODIR}" && ls -l *.iso | awk 'NR == 1 {print $9}')"
    else
      # Otherwise, loop until we get a valid user selection
      while :
      do
        echo "Please select which ISO to test (1-$iso_cnt):"

        # Listing ISOs in the ./freenas/iso/ directory, numbering the results for selection
        ls -l "${ISODIR}"*.iso | awk 'BEGIN{cnt=1} {print "    ("cnt") "$9; cnt+=1}'
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
          iso_name="$(cd "${ISODIR}" && ls -l *.iso | awk 'FNR == '$iso_selection' {print $9}')"
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
  cp ${ISODIR}/${iso_name} ${MASTERWRKDIR}
}

# $1 = The path to a FreeNAS/TrueNAS ISO for installation
bhyve_install_iso()
{
  export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
  if [ ! -f "/usr/local/share/uefi-firmware/BHYVE_UEFI.fd" ] ; then
    echo "File not found: /usr/local/share/uefi-firmware/BHYVE_UEFI.fd"
    echo "Install the \"uefi-edk2-bhyve\" port. Exiting."
    exit 1
  fi

  # Find the ISONAME
  ISONAME=`ls ${MASTERWORKDIR} *.iso`
  ISOFILE="${MASTERWRKDIR}/${ISONAME}"

  # Allow the $IXBUILD_BRIDGE, $IXBUILD_IFACE, $IXBUILD_TAP to be overridden
  [ -z "${IXBUILD_BRIDGE}" ] && export IXBUILD_BRIDGE="ixbuildbridge0"
  [ -z "${IXBUILD_IFACE}" ] && export IXBUILD_IFACE="`netstat -f inet -nrW | grep '^default' | awk '{ print $6 }'`"
  [ -z "${IXBUILD_TAP}" ] && export IXBUILD_TAP="tap"
  [ -z "${IXBUILD_ROOT_ZVOL}" ] && export IXBUILD_ROOT_ZVOL="tank"

  local VM_OUTPUT="/tmp/${VM}console.log"
  local VOLUME="${IXBUILD_ROOT_ZVOL}"
  local DATADISKOS="${VM}-os"
  local DATADISK1="${VM}-data1"
  local DATADISK2="${VM}-data2"
  local IXBUILD_DNSMASQ=$(test -n "${IXBUILD_DNSMASQ}" && echo "${IXBUILD_DNSMASQ}" || which dnsmasq 2>/dev/null)
  local BOOT_PIDFILE="/tmp/.cu-${VM}-boot.pid"
  local TAP_LOCKFILE="/tmp/.tap-${VM}.lck"

  service vboxnet stop >/dev/null 2>/dev/null
  sysctl net.link.bridge.ipfw=1

  # Verify kernel modules are loaded if this is a BSD system
  if which kldstat >/dev/null 2>/dev/null ; then
    kldstat | grep -q if_tap || kldload if_tap
    kldstat | grep -q if_bridge || kldload if_bridge
    kldstat | grep -q vmm || kldload vmm
    kldstat | grep -q nmdm || kldload nmdm
    kldstat | grep -q ipfw_nat || kldload ipfw_nat
    kldstat | grep -q ipdivert || kldload ipdivert
    kldstat | grep -q vboxnetflt || kldunload vboxnetflt
    kldstat | grep -q vboxnetadp || kldunload vboxnetadp
    kldstat | grep -q vboxdrv || kldunload vboxdrv
  fi

  echo "Setting up bhyve network interfaces..."

  # Auto-up tap devices and allow forwarding
  sysctl net.link.tap.up_on_open=1 &>/dev/null
  sysctl net.inet.ip.forwarding=1 &>/dev/null

  #
  # @TODO: If $IXBUILD_IFACE is wlan0, setup NAT with DHCP (using dnsmasq)
  #

  # Check the status of our network bridge
  if ! ifconfig ${IXBUILD_BRIDGE} >/dev/null 2>/dev/null ; then
    # Create the bridge if it does not exist
    bridge=$(ifconfig bridge create)
    ifconfig ${bridge} name ${IXBUILD_BRIDGE} >/dev/null
    # Create the initial tap device for the bridge
    local INITIAL_TAP_LOCKFILE="/tmp/.initial-tap-${VM}"
    ifconfig tap create > ${INITIAL_TAP_LOCKFILE} 
    # Ensure $IXBUILD_IFACE is a member of our bridge.
    if ! ifconfig ${IXBUILD_BRIDGE} | grep -q "member: ${IXBUILD_IFACE}" ; then
      ifconfig ${IXBUILD_BRIDGE} addm ${IXBUILD_IFACE}
    fi
    # Add the initial tap device to the bridge
    local INITIAL_TAP=$(cat /tmp/.initial-tap-${VM})
    ifconfig ${IXBUILD_BRIDGE} addm ${INITIAL_TAP}
    # Bring up the bridge
    ifconfig ${IXBUILD_BRIDGE} up
  fi

  # Lets check status of ${IXBUILD_TAP} device
  if ! ifconfig ${IXBUILD_TAP} >/dev/null 2>/dev/null ; then
    IXBUILD_TAP=$(ifconfig ${IXBUILD_TAP} create)
    # Save the tap interface name, generated or specified. Used for clean-up.
    echo ${IXBUILD_TAP} > ${TAP_LOCKFILE}
  fi

  # Ensure $IXBUILD_IFACE is a member of our bridge.
  if ! ifconfig ${IXBUILD_BRIDGE} | grep -q "member: ${IXBUILD_IFACE}" ; then
   ifconfig ${IXBUILD_BRIDGE} addm ${IXBUILD_IFACE}
  fi

  # Ensure $IXBUILD_TAP is a member of our bridge.
  if ! ifconfig ${IXBUILD_BRIDGE} | grep -q "member: ${IXBUILD_TAP}" ; then
    ifconfig ${IXBUILD_BRIDGE} addm ${IXBUILD_TAP}
  fi

  ###############################################
  # Now lets spin-up bhyve and do an installation
  ###############################################

  echo "Performing bhyve installation..."

  # Determine which nullmodem slot to use for the installation
  local com_idx=0
  until ! ls /dev/nmdm* 2>/dev/null | grep -q "/dev/nmdm${com_idx}A" ; do com_idx=$(expr $com_idx + 1); done
  local COM_BROADCAST="/dev/nmdm${com_idx}A"
  local COM_LISTEN="/dev/nmdm${com_idx}B"

  # Create our OS disk and data disks
  # To stop the host from sniffing partitions, which could cause the install
  # to fail, we set the zfs option volmode=dev on the OS parition
  local os_size=20
  local disk_size=50
  local freespace=$(df -h | awk '$6 == "/" {print $4}' | sed 's|G$||')
  # Decrease os and data disk sizes if less than 120G is avail on the root mountpoint
  if [ -n "$freespace" -a $freespace -le 120 ] ; then os_size=10; disk_size=5; fi

  zfs create -s -V ${os_size}G -o volmode=dev ${VOLUME}/${DATADISKOS}
  zfs create -s -V ${disk_size}G ${VOLUME}/${DATADISK1}
  zfs create -s -V ${disk_size}G ${VOLUME}/${DATADISK2}

  # Install from our ISO
#  if [ ${SYSTYPE} = "FreeNAS" ] ; then
    ( bhyve -w -A -H -P -c 1 -m 2G \
      -s 0:0,hostbridge \
      -s 1:0,lpc \
      -s 2:0,virtio-net,${IXBUILD_TAP} \
      -s 4:0,ahci-cd,${ISOFILE} \
      -s 5:0,ahci-hd,/dev/zvol/${VOLUME}/${DATADISKOS} \
      -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd \
      -l com1,${COM_BROADCAST} \
      $VM ) &
#  else
#    ( bhyveload -c ${COM_BROADCAST} -m 2G -d ${ISOFILE} $VM )
#    ( bhyve -A -H -P -c 1 -m 2G \
#      -s 0:0,hostbridge \
#      -s 1:0,lpc \
#      -s 2:0,virtio-net,${IXBUILD_TAP} \
#      -s 4:0,ahci-cd,${ISOFILE} \
#      -s 5:0,ahci-hd,/dev/zvol/${VOLUME}/${DATADISKOS} \
#      -l com1,${COM_BROADCAST} \
#      $VM ) &
#  fi
  # -s 16,fbuf,tcp=127.0.0.1:5909,w=1280,h=720,wait \
  # Run our expect/tcl script to automate the installation dialog
  ${PROGDIR}/${SYSTYPE}/bhyve-installer.exp "${COM_LISTEN}" "${VM_OUTPUT}"
  echo -e \\033c # Reset/clear to get native term dimensions
  echo "Success: Shutting down the installation VM.."

  # Shutdown VM, stop output
  sleep 5
  bhyvectl --destroy --vm=$VM &>/dev/null &

  # If this cmd returned instead of hanging, it would be preferable to use. The alternative writes to a tmp file.
  # local COM_LISTEN=$(boot_bhyve | tee /dev/tty | grep "^Listen: " | sed 's|Listen: ||g')
  local BHYVE_BOOT_OUTPUT="/tmp/.boot-${VM}output"
  bhyve_boot > ${BHYVE_BOOT_OUTPUT}
  local COM_LISTEN=$(cat ${BHYVE_BOOT_OUTPUT} | grep '^Listen: ' | sed 's|^Listen: ||')
  echo "COM: ${COM_LISTEN}"
  ${PROGDIR}/${SYSTYPE}/bhyve-bootup.exp "${COM_LISTEN}" "${VM_OUTPUT}"

  echo -e \\033c # Reset/clear to get native term dimensions

  local EXIT_STATUS=1
  if grep -q "Starting nginx." ${VM_OUTPUT} || grep -q "Plugin loaded: SSHPlugin" ${VM_OUTPUT} ; then
    export FNASTESTIP="$(awk '$0 ~ /^vtnet0:\ flags=/ {++n;next}; n == 1 && $1 == "inet" {print $2;exit}' ${VM_OUTPUT})"
    if [ -n "${FNASTESTIP}" ] ; then
      echo "FNASTESTIP=${FNASTESTIP}"
      EXIT_STATUS=0
    else
      echo "FNASTESTIP=0.0.0.0"
      echo "ERROR: No ip address assigned to VM. FNASTESTIP not set."
      exit_fail
    fi
  fi
  return $EXIT_STATUS
}

# Boots installed FreeNAS/TrueNAS bhyve VM
bhyve_boot()
{
  export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
  local VOLUME="${IXBUILD_ROOT_ZVOL}"
  local DATADISKOS="${VM}-os"
  local DATADISK1="${VM}-data1"
  local DATADISK2="${VM}-data2"
  local TAP_LOCKFILE="/tmp/.tap-${VM}.lck"

  [ -z "${IXBUILD_TAP}" ] && export IXBUILD_TAP="tap"

  # If $TAP_LOCKFILE exists and ifconfig shows active $IXBUILD_TAP, skip network setup
  if [ -f "${TAP_LOCKFILE}" ] && ifconfig ${IXBUILD_TAP} >/dev/null 2>/dev/null ; then
    # If restarting existing boot-up, TAP_LOCKFILE will contain the correct tap name,
    # and $IXBUILD_TAP will be 'tap'
    IXBUILD_TAP=$(cat "${TAP_LOCKFILE}")
  else
    [ -f "${TAP_LOCKFILE}" ] && cat "${TAP_LOCKFILE}" | xargs -I {} ifconfig {} destroy && rm "${TAP_LOCKFILE}"

    # Lets check status of ${IXBUILD_TAP} device
    if ! ifconfig ${IXBUILD_TAP} >/dev/null 2>/dev/null ; then
      IXBUILD_TAP=$(ifconfig ${IXBUILD_TAP} create)
      # Save the tap interface name, generated or specified. Used for clean-up.
      echo ${IXBUILD_TAP} > ${TAP_LOCKFILE}
    fi
  fi

  echo "Determining which nullmodem slot to use for boot-up.."
  local com_idx=0
  until ! ls /dev/nmdm* 2>/dev/null | grep -q "/dev/nmdm${com_idx}A" ; do com_idx=$(expr $com_idx + 1); done
  local COM_BROADCAST="/dev/nmdm${com_idx}A"
  local COM_LISTEN="/dev/nmdm${com_idx}B"
  echo "Broadcast: ${COM_BROADCAST}"
  echo "Listen: ${COM_LISTEN}"

  # Fixes: ERROR: "vm_open: Invalid argument"
  sleep 10

  ( bhyve -w -A -H -P -c 1 -m 2G \
    -s 0:0,hostbridge \
    -s 1:0,lpc \
    -s 2:0,virtio-net,${IXBUILD_TAP} \
    -s 5:0,ahci-hd,/dev/zvol/${VOLUME}/${DATADISKOS} \
    -s 6:0,ahci-hd,/dev/zvol/${VOLUME}/${DATADISK1} \
    -s 7:0,ahci-hd,/dev/zvol/${VOLUME}/${DATADISK2} \
    -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd \
    -l com1,${COM_BROADCAST} \
    $VM ) &

  return 0
}

bhyve_stop()
{
  # Shutdown VM, stop output, and cleanup
  export VM=`echo "${MASTERWRKDIR}" | cut -f 4 -d '/'`
  local VM_OUTPUT="/tmp/${VM}console.log"
  local VOLUME="${IXBUILD_ROOT_ZVOL}"
  local DATADISKOS="${VM}-os"
  local DATADISK1="${VM}-data1"
  local DATADISK2="${VM}-data2"

  # Destroy the VM
  bhyvectl --destroy --vm=$VM &>/dev/null &

  # Wait for VM to be destroyed
  sleep 5

  # Remove the tap interface
  ifconfig ${IXBUILD_BRIDGE} deletem ${IXBUILD_TAP}
 
  # Wait for tap to be removed
  sleep 5 

  # Destroy the tap interface
  ifconfig ${IXBUILD_TAP} destroy &>/dev/null

  # Remove log, locking, and pidfiles
  rm "${VM_OUTPUT}" &>/dev/null
  [ -f "${BOOT_PIDFILE}" ] && cat "${BOOT_PIDFILE}" | xargs -I {} kill {} &>/dev/null
  [ -f "${TAP_LOCKFILE}" ] && cat "${TAP_LOCKFILE}" | xargs -I {} ifconfig {} destroy && rm "${TAP_LOCKFILE}"

  # Destroy zvols
  zfs destroy ${VOLUME}/${DATADISKOS} &>/dev/null &
  zfs destroy ${VOLUME}/${DATADISK1} &>/dev/null &
  zfs destroy ${VOLUME}/${DATADISK2} &>/dev/null &
}
