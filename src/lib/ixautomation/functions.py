#!/usr/bin/env python3.6

import os
import signal
import sys
from subprocess import Popen, run, PIPE
from shutil import copyfile
import random
import string
from functions_vm import vm_destroy, vm_setup, vm_select_iso
from functions_vm import vm_boot, vm_install, vm_stop_all, clean_all_vm


def create_workdir():
    builddir = "/tmp/ixautomation"
    tmp = ''.join(random.choices(string.ascii_uppercase, k=4))
    global vm
    vm = tmp
    global tmp_vm_dir
    tmp_vm_dir = f'{builddir}/{vm}'
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    os.makedirs(tmp_vm_dir)
    return tmp_vm_dir


def cleanup_workdir(tmp_vm_dir):
    mounted = Popen("mount", shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    for line in mounted.stdout:
        if f"on {tmp_vm_dir} /" in line:
            mountpoint = line.split()[2]
            run(f"umount -f {mountpoint}", shell=True)
    mounted = Popen("mount", shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    # Should be done with unmount
    if f"on {tmp_vm_dir} /" not in mounted.stdout.read():
        run(f"chflags -R noschg  {tmp_vm_dir}", shell=True)
        run(f"rm -rf {tmp_vm_dir}", shell=True)
    os.remove(f'/usr/local/ixautomation/vms/.iso/{select_iso}')


def exit_clean(tmp_vm_dir):
    print('## iXautomation is stopping! Clean up time!')
    vm_destroy(vm)
    cleanup_workdir(tmp_vm_dir)
    sys.exit(0)


def exit_terminated(arg1, arg2):
    os.system('reset')
    print('## iXautomation got terminated! Clean up time!')
    vm_destroy(vm)
    cleanup_workdir(tmp_vm_dir)
    sys.exit(1)


def exit_fail(msg):
    os.system('reset')
    print(f'## {msg} Clean up time!')
    vm_destroy(vm)
    cleanup_workdir(tmp_vm_dir)
    sys.exit(1)


def set_sig():
    signal.signal(signal.SIGTERM, exit_terminated)
    signal.signal(signal.SIGHUP, exit_terminated)
    signal.signal(signal.SIGINT, exit_terminated)


def start_vm(workspace, systype, sysname, keep_alive):
    create_workdir()
    set_sig()
    vm_setup()
    global select_iso
    select_iso = vm_select_iso(tmp_vm_dir, vm, systype, sysname, workspace)
    install = vm_install(tmp_vm_dir, vm, systype, sysname, workspace)
    if install is False:
        exit_fail('iXautomation stop on installation failure!')
    ip = vm_boot(tmp_vm_dir, vm, systype, sysname, workspace)
    if ip == '0.0.0.0' and keep_alive is False:
        exit_fail('iXautomation stop because IP is 0.0.0.0!')

    return {'ip': ip, 'netcard': "vtnet0", 'iso': select_iso}


def start_automation(workspace, systype, sysname, ipnc, test, keep_alive):
    # ipnc is None start a vm
    if ipnc is None:
        vm_info = start_vm(workspace, systype, sysname, keep_alive)
        ip = vm_info['ip']
        netcard = vm_info['netcard']
    else:
        ipnclist = ipnc.split(":")
        ip = ipnclist[0]
        netcard = "vtnet0" if len(ipnclist) == 1 else ipnclist[1]

    if test != 'vmtest':
        run_test(workspace, test, systype, ip, netcard)

    if keep_alive is False and ipnc is None:
        exit_clean(tmp_vm_dir)


def run_test(workspace, test, systype, ip, netcard):
    if test == "api-tests":
        api_tests(workspace, systype, ip, netcard)
    elif test == "api2-tests":
        api2_tests(workspace, systype, ip, netcard)
    elif test == "webui-tests":
        webui_tests(workspace, ip)


def api_tests(workspace, systype, ip, netcard):
    apipath = f"{workspace}/tests"
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", f"{apipath}/config.py")
    os.chdir(apipath)
    cmd = f"python3.6 runtest.py --ip {ip} " \
        f"--password testing --interface {netcard}"
    run(cmd, shell=True)
    os.chdir(workspace)


def api2_tests(workspace, systype, ip, netcard):
    apipath = f"{workspace}/tests"
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", f"{apipath}/config.py")
    os.chdir(apipath)
    cmd = f"python3.6 runtest.py --ip {ip} " \
        f"--password testing --interface {netcard} --api 2.0"
    run(cmd, shell=True)
    os.chdir(workspace)


def webui_tests(workspace, ip):
    webUIpath = f"{workspace}/tests/"
    os.chdir(webUIpath)
    cmd1 = f"python3.6 -u runtest.py --ip {ip}"
    run(cmd1, shell=True)
    os.chdir(workspace)


def destroy_all_vm():
    vm_stop_all()
    clean_all_vm()
    sys.exit(0)
    return 0
