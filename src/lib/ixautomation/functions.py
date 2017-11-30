#!/usr/bin/env python3.6

import os
import signal
import sys
from subprocess import Popen, run, PIPE
import random
import string
from functions_vm import vm_destroy, vm_setup, vm_select_iso
from functions_vm import vm_boot, vm_install, vm_stop_all, vm_destroy_all


def create_workdir(workspace, systype):
    # if [ -n "$USING_JENKINS" ] ; then return 0
    builddir = "%s/tests/%s/build" % (workspace, systype)
    tempdir = random.choices(string.ascii_uppercase, k=4)
    global MASTERWRKDIR
    MASTERWRKDIR = builddir + '/' + tempdir
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    os.makedirs(MASTERWRKDIR)
    return MASTERWRKDIR


def cleanup_workdir():
    # if [ -n "$USING_JENKINS" ] ; then return 0 ; fi
    # if [ -z "$MASTERWRKDIR" ] ; then return 0 ; fi
    # if [ ! -d "$MASTERWRKDIR" ] ; then return 0 ; fi
    # if [ "$MASTERWRKDIR" = "/" ] ; then return 0 ; fi
    mounted = Popen("mount", shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    for line in mounted.stdout:
        if "on %s /" % MASTERWRKDIR in line:
            run("umount -f " + line.split()[2], shell=True)
    mounted = Popen("mount", shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    # Should be done with unmounts
    if "on %s /" % MASTERWRKDIR not in mounted.stdout.read():
        run("chflags -R noschg  " + MASTERWRKDIR, shell=True)
        run("rm -rf " + MASTERWRKDIR, shell=True)


def exit_clean():
    vm_destroy(MASTERWRKDIR)
    cleanup_workdir()
    sys.exit(0)
    return 0


def exit_fail():
    vm_destroy(MASTERWRKDIR)
    cleanup_workdir()
    sys.exit(1)
    return 1


def jenkins_vm_tests():
    create_workdir()
    vm_setup()
    vm_select_iso()
    vm_install(MASTERWRKDIR)
    vm_boot(MASTERWRKDIR)
    # if [ "${TEST}" = "api-tests" ]; then
    #     cd "${cwd}/freenas/api-test" || exit_clean
    #     python3.6 runtest.py --ip ${FNASTESTIP} --password testing --interface vtnet0
    # cd -
    exit_clean()


def jenkins_start_vm():
    create_workdir()
    vm_setup()
    vm_select_iso()
    vm_install()
    vm_boot()


def jenkins_vm_destroy_all():
    vm_stop_all()
    vm_destroy_all()


def jenkins_api_tests():
    create_workdir()
    vm_setup()
    vm_select_iso()
    vm_install()
    vm_boot()
    # cd "${cwd}/freenas/api-test" || exit_clean
    # python3.6 runtest.py --ip ${FNASTESTIP} --password testing --interface vtnet0
    # cd -
    exit_clean()


def jenkins_freenas_webui_tests():
    pass
    # export DISPLAY=:0
    # cd "${WORKSPACE}/tests/${SYSTYPE}/webui-tests" || exit_clean
    # python runtest.py
    # cd -


def jenkins_iocage_tests():
    gitrepo = "https://www.github.com/iocage/iocage"
    exit_clean()


for sgnl in [signal.SIGHUP, signal.SIGTERM, signal.SIGINT]:
    signal.signal(sgnl, exit_fail)
