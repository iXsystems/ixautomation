#!/usr/bin/env sh

# Set the build tag
BUILDTAG="$BUILD"
export BUILDTAG

cleanup_workdir()
{
  if [ -n "$WORKSPACE" ] ; then return 0 ; fi
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
  if [ -n "$WORKSPACE" ] ; then return 0 ; fi
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

jenkins_freenas_tests()
{
  GITREPO="https://www.github.com/ixsystems/ixbuild.git"
  create_workdir
  cleanup_workdir
}

jenkins_iocage_tests()
{
  GITREPO="https://www.github.com/iocage/iocage"
  create_workdir
  cleanup_workdir
}
