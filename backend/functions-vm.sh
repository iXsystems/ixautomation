#!/usr/bin/env sh

# $1 = The path to a FreeNAS/TrueNAS ISO for installation
bhyve_install_iso()
{
  if [ ! -f "/usr/local/share/uefi-firmware/BHYVE_UEFI.fd" ] ; then
    echo "File not found: /usr/local/share/uefi-firmware/BHYVE_UEFI.fd"
    echo "Install the \"uefi-edk2-bhyve\" port. Exiting."
    exit 1
  fi

  # Allow the $IXBUILD_BRIDGE, $IXBUILD_IFACE, $IXBUILD_TAP to be overridden
  [ -z "${IXBUILD_BRIDGE}" ] && export IXBUILD_BRIDGE="ixbuildbridge0"
  [ -z "${IXBUILD_IFACE}" ] && export IXBUILD_IFACE="`netstat -f inet -nrW | grep '^default' | awk '{ print $6 }'`"
  [ -z "${IXBUILD_TAP}" ] && export IXBUILD_TAP="tap"
  [ -z "${IXBUILD_ROOT_ZVOL}" ] && export IXBUILD_ROOT_ZVOL="tank"

  local ISOFILE=$1
  local VM_OUTPUT="/tmp/${BUILDTAG}console.log"
  local VOLUME="${IXBUILD_ROOT_ZVOL}"
  local DATADISKOS="${BUILDTAG}-os"
  local DATADISK1="${BUILDTAG}-data1"
  local DATADISK2="${BUILDTAG}-data2"
  local IXBUILD_DNSMASQ=$(test -n "${IXBUILD_DNSMASQ}" && echo "${IXBUILD_DNSMASQ}" || which dnsmasq 2>/dev/null)
  local BOOT_PIDFILE="/tmp/.cu-${BUILDTAG}-boot.pid"
  local TAP_LOCKFILE="/tmp/.tap-${BUILDTAG}.lck"

  # Verify kernel modules are loaded if this is a BSD system
  if which kldstat >/dev/null 2>/dev/null ; then
    kldstat | grep -q if_tap || kldload if_tap
    kldstat | grep -q if_bridge || kldload if_bridge
    kldstat | grep -q vmm || kldload vmm
    kldstat | grep -q nmdm || kldload nmdm
  fi

  # Shutdown VM, stop output, and cleanup
  bhyvectl --destroy --vm=$BUILDTAG &>/dev/null &
  ifconfig ${IXBUILD_BRIDGE} destroy &>/dev/null
  ifconfig ${IXBUILD_TAP} destroy &>/dev/null
  rm "${VM_OUTPUT}" &>/dev/null
  [ -f "${BOOT_PIDFILE}" ] && cat "${BOOT_PIDFILE}" | xargs -I {} kill {} &>/dev/null
  [ -f "${TAP_LOCKFILE}" ] && cat "${TAP_LOCKFILE}" | xargs -I {} ifconfig {} destroy && rm "${TAP_LOCKFILE}"

  # Destroy zvols from previous runs
  local zfs_list=$(zfs list | awk 'NR>1 {print $1}')
  echo ${zfs_list} | grep -q "${VOLUME}/${DATADISKOS}" && zfs destroy ${VOLUME}/${DATADISKOS}
  echo ${zfs_list} | grep -q "${VOLUME}/${DATADISK1}" && zfs destroy ${VOLUME}/${DATADISK1}
  echo ${zfs_list} | grep -q "${VOLUME}/${DATADISK2}" && zfs destroy ${VOLUME}/${DATADISK2}

  echo "Setting up bhyve network interfaces..."

  # Auto-up tap devices and allow forwarding
  sysctl net.link.tap.up_on_open=1 &>/dev/null
  sysctl net.inet.ip.forwarding=1 &>/dev/null

  # Lets check status of ${IXBUILD_TAP} device
  if ! ifconfig ${IXBUILD_TAP} >/dev/null 2>/dev/null ; then
    IXBUILD_TAP=$(ifconfig ${IXBUILD_TAP} create)
    # Save the tap interface name, generated or specified. Used for clean-up.
    echo ${IXBUILD_TAP} > ${TAP_LOCKFILE}
  fi

  #
  # @TODO: If $IXBUILD_IFACE is wlan0, setup NAT with DHCP (using dnsmasq)
  #

  # Check the status of our network bridge
  if ! ifconfig ${IXBUILD_BRIDGE} >/dev/null 2>/dev/null ; then
    bridge=$(ifconfig bridge create)
    ifconfig ${bridge} name ${IXBUILD_BRIDGE} >/dev/null
  fi

  # Ensure $IXBUILD_IFACE is a member of our bridge.
  if ! ifconfig ${IXBUILD_BRIDGE} | grep -q "member: ${IXBUILD_IFACE}" ; then
    ifconfig ${IXBUILD_BRIDGE} addm ${IXBUILD_IFACE}
  fi

  # Ensure $IXBUILD_TAP is a member of our bridge.
  if ! ifconfig ${IXBUILD_BRIDGE} | grep -q "member: ${IXBUILD_TAP}" ; then
    ifconfig ${IXBUILD_BRIDGE} addm ${IXBUILD_TAP}
  fi

  # Finally, have our bridge pickup an IP Address
  ifconfig ${IXBUILD_BRIDGE} up && dhclient ${IXBUILD_BRIDGE}

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

  zfs create -V ${os_size}G -o volmode=dev ${VOLUME}/${DATADISKOS}
  zfs create -V ${disk_size}G ${VOLUME}/${DATADISK1}
  zfs create -V ${disk_size}G ${VOLUME}/${DATADISK2}

  # Install from our ISO
  ( bhyve -w -A -H -P -c 1 -m 2G \
    -s 0:0,hostbridge \
    -s 1:0,lpc \
    -s 2:0,virtio-net,${IXBUILD_TAP} \
    -s 4:0,ahci-cd,${ISOFILE} \
    -s 5:0,ahci-hd,/dev/zvol/${VOLUME}/${DATADISKOS} \
    -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd \
    -l com1,${COM_BROADCAST} \
    $BUILDTAG ) &

  # Run our expect/tcl script to automate the installation dialog
  ${PROGDIR}/scripts/bhyve-installer.exp "${COM_LISTEN}" "${VM_OUTPUT}"
  echo -e \\033c # Reset/clear to get native term dimensions
  echo "Success: Shutting down the installation VM.."

  # Shutdown VM, stop output
  sleep 5
  bhyvectl --destroy --vm=$BUILDTAG &>/dev/null &

  # If this cmd returned instead of hanging, it would be preferable to use. The alternative writes to a tmp file.
  # local COM_LISTEN=$(boot_bhyve | tee /dev/tty | grep "^Listen: " | sed 's|Listen: ||g')
  local BHYVE_BOOT_OUTPUT="/tmp/.boot-${BUILDTAG}output"
  bhyve_boot > ${BHYVE_BOOT_OUTPUT}
  local COM_LISTEN=$(cat ${BHYVE_BOOT_OUTPUT} | grep '^Listen: ' | sed 's|^Listen: ||')
  echo "COM: ${COM_LISTEN}"
  ${PROGDIR}/scripts/bhyve-bootup.exp "${COM_LISTEN}" "${VM_OUTPUT}"

  echo -e \\033c # Reset/clear to get native term dimensions

  local EXIT_STATUS=1
  if grep -q "Starting nginx." ${VM_OUTPUT} || grep -q "Plugin loaded: SSHPlugin" ${VM_OUTPUT} ; then
    local FNASTESTIP="$(awk '$0 ~ /^vtnet0:\ flags=/ {++n;next}; n == 1 && $1 == "inet" {print $2;exit}' ${VM_OUTPUT})"
    if [ -n "${FNASTESTIP}" ] ; then
      echo "FNASTESTIP=${FNASTESTIP}"
      EXIT_STATUS=0
    else
      echo "FNASTESTIP=0.0.0.0"
      echo "ERROR: No ip address assigned to VM. FNASTESTIP not set."
    fi
  fi

  return $EXIT_STATUS
}

# Boots installed FreeNAS/TrueNAS bhyve VM
bhyve_boot()
{
  local VOLUME="${IXBUILD_ROOT_ZVOL}"
  local DATADISKOS="${BUILDTAG}-os"
  local DATADISK1="${BUILDTAG}-data1"
  local DATADISK2="${BUILDTAG}-data2"
  local TAP_LOCKFILE="/tmp/.tap-${BUILDTAG}.lck"

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
    $BUILDTAG ) & disown

  return 0
}
