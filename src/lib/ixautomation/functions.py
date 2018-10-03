#!/usr/bin/env python3.6

import os
import signal
import sys
from subprocess import Popen, run, PIPE
from shutil import copyfile
import random
import string
from functions_vm import vm_destroy, vm_setup, vm_select_iso
from functions_vm import vm_boot, vm_install, vm_stop_all, vm_destroy_all


def create_workdir():
    builddir = "/tmp/ixautomation"
    global tempdir
    tempdir = ''.join(random.choices(string.ascii_uppercase, k=4))
    global MASTERWRKDIR
    MASTERWRKDIR = f'{builddir}/{tempdir}'
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    os.makedirs(MASTERWRKDIR)
    return MASTERWRKDIR


def cleanup_workdir(MASTERWRKDIR):
    mounted = Popen("mount", shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    for line in mounted.stdout:
        if f"on {MASTERWRKDIR} /" in line:
            mountpoint = line.split()[2]
            run(f"umount -f {mountpoint}", shell=True)
    mounted = Popen("mount", shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    # Should be done with unmount
    if f"on {MASTERWRKDIR} /" not in mounted.stdout.read():
        run(f"chflags -R noschg  {MASTERWRKDIR}", shell=True)
        run(f"rm -rf {MASTERWRKDIR}", shell=True)
    os.remove(f'/usr/local/ixautomation/vms/.iso/{select_iso}')


def exit_clean(MASTERWRKDIR):
    print('## iXautomation is stopping! Clean up time!')
    vm_destroy(MASTERWRKDIR)
    cleanup_workdir(MASTERWRKDIR)
    sys.exit(0)


def exit_fail(arg1, arg2):
    os.system('reset')
    print('## iXautomation got terminated! Clean up time!')
    vm_destroy(MASTERWRKDIR)
    cleanup_workdir(MASTERWRKDIR)
    sys.exit(1)


def jenkins_vm_tests(workspace, systype, ipnc, test, keep_alive):
    if ipnc is None:
        create_workdir()
        signal.signal(signal.SIGTERM, exit_fail)
        signal.signal(signal.SIGHUP, exit_fail)
        signal.signal(signal.SIGINT, exit_fail)
        vm_setup()
        global select_iso
        select_iso = vm_select_iso(MASTERWRKDIR, systype, workspace)
        vm_install(MASTERWRKDIR, systype, workspace)
        netcard = "vtnet0"
        ip = vm_boot(MASTERWRKDIR, systype, workspace, netcard)
    else:
        if ":" in ipnc:
            ipnclist = ipnc.split(":")
            ip = ipnclist[0]
            netcard = ipnclist[1]
        else:
            ip = ipnc
            netcard = "vtnet0"
    if test == "api-tests":
        jenkins_api_tests(workspace, systype, ip, netcard)
    elif test == "api2-tests":
        jenkins_api2_tests(workspace, systype, ip, netcard)
    elif test == "webui-tests":
        jenkins_webui_tests(workspace, ip)
    # clean up vm if --keep-alive is not specify
    if keep_alive is False:
        exit_clean(MASTERWRKDIR)


def jenkins_api_tests(workspace, systype, ip, netcard):
    apipath = f"{workspace}/tests"
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", f"{apipath}/config.py")
    os.chdir(apipath)
    cmd = f"python3.6 runtest.py --ip {ip} " \
        f"--password testing --interface {netcard}"
    run(cmd, shell=True)
    os.chdir(workspace)


def jenkins_api2_tests(workspace, systype, ip, netcard):
    apipath = f"{workspace}/tests"
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", f"{apipath}/config.py")
    os.chdir(apipath)
    cmd = f"python3.6 runtest.py --ip {ip} " \
        f"--password testing --interface {netcard} --api 2.0"
    run(cmd, shell=True)
    os.chdir(workspace)


def jenkins_webui_tests(workspace, ip):
    webUIpath = f"{workspace}/tests/"
    os.chdir(webUIpath)
    cmd1 = f"python3.6 -u runtest.py --ip {ip}"
    run(cmd1, shell=True)
    os.chdir(workspace)


def jenkins_vm_destroy_all():
    vm_stop_all()
    vm_destroy_all()
    sys.exit(0)
    return 0
