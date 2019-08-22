#!/usr/bin/env python3.6

import os
import signal
import sys
from subprocess import Popen, run, PIPE, call
import re
from shutil import copyfile
import random
import string
from functions_vm import vm_destroy, vm_setup, vm_select_iso, clean_vm
from functions_vm import vm_boot, vm_install, vm_stop_all, clean_all_vm
from functions_vm import vm_destroy_stopped_vm

ixautomation_config = '/usr/local/etc/ixautomation.conf'

notnics = [
    "lo",
    "fwe",
    "fwip",
    "tap",
    "plip",
    "pfsync",
    "pflog",
    "tun",
    "sl",
    "faith",
    "ppp",
    "wlan",
    "brige",
    "ixautomation",
    "vm-ixautomation"
]


def create_ixautomation_interface():
    ncard = 'ifconfig -l'
    nics = Popen(ncard, shell=True, stdout=PIPE, close_fds=True,
                 universal_newlines=True)
    netcard = nics.stdout.readlines()[0].rstrip().split()
    if "vm-ixautomation" not in netcard or "ixautomation" not in netcard:
        os.remove(f'/usr/local/ixautomation/vms/.config/system.conf')
        call('vm switch create ixautomation', shell=True)
        for line in netcard:
            card = line.rstrip()
            nc = re.sub(r'\d+', '', card)
            if nc not in notnics:
                call(f'vm switch add ixautomation {card}', shell=True)
                taping = Popen('ifconfig tap create', shell=True, stdout=PIPE,
                               close_fds=True, universal_newlines=True)
                tap = taping.stdout.readlines()[0].rstrip()
                call(f'ifconfig vm-ixautomation addm {tap}', shell=True)
                break
    else:
        print("ixautomation switch interface already running")


def ssh_cmd(command, username, passwrd, host):
    cmd_list = [] if passwrd is None else ["sshpass", "-p", passwrd]
    cmd_list += [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "VerifyHostKeyDNS=no",
        f"{username}@{host}",
    ]
    cmd_list += command.split()
    run(cmd_list)


def get_file(file, destination, username, passwrd, host):
    cmd = [] if passwrd is None else ["sshpass", "-p", passwrd]
    cmd += [
        "scp",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "VerifyHostKeyDNS=no",
        f"{username}@{host}:{file}",
        destination
    ]
    process = run(cmd, stdout=PIPE, universal_newlines=True)
    output = process.stdout
    if process.returncode != 0:
        return {'result': False, 'output': output}
    else:
        return {'result': True, 'output': output}


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
    clean_vm(vm)


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


def start_vm(wrkspc, systype, sysname, keep_alive):
    create_workdir()
    set_sig()
    vm_setup()
    global select_iso
    select_iso = vm_select_iso(tmp_vm_dir, vm, systype, sysname, wrkspc)
    install = vm_install(tmp_vm_dir, vm, systype, sysname, wrkspc)
    if install is False:
        exit_fail('iXautomation stop on installation failure!')
    ip = vm_boot(tmp_vm_dir, vm, systype, sysname, wrkspc)
    if ip == '0.0.0.0' and keep_alive is False:
        exit_fail('iXautomation stop because IP is 0.0.0.0!')
    elif ip == '' and keep_alive is False:
        exit_fail('iXautomation stop because IP is None!')
    return {'ip': ip, 'netcard': "vtnet0", 'iso': select_iso}


def start_automation(wrkspc, systype, sysname, ipnc, tst, keep_alive, srvr_ip):
    # ipnc is None start a vm
    if ipnc is None:
        vm_info = start_vm(wrkspc, systype, sysname, keep_alive)
        ip = vm_info['ip']
        netcard = vm_info['netcard']
    else:
        ipnclist = ipnc.split(":")
        ip = ipnclist[0]
        netcard = "vtnet0" if len(ipnclist) == 1 else ipnclist[1]

    if tst != 'vmtest':
        run_test(wrkspc, tst, systype, ip, netcard, srvr_ip)

    if keep_alive is False and ipnc is None:
        exit_clean(tmp_vm_dir)


def run_test(wrkspc, test, systype, ip, netcard, server_ip):
    if test == "api-tests":
        api_tests(wrkspc, systype, ip, netcard, server_ip)
    elif test == "websocket-tests":
        websocket_tests(wrkspc, systype, ip, netcard, server_ip)
    elif test == "api2-tests":
        api2_tests(wrkspc, systype, ip, netcard)
    elif test == "webui-tests":
        webui_tests(wrkspc, ip)
    elif test == "kyua-tests":
        kyua_tests(wrkspc, systype, ip, netcard)


def kyua_tests(wrkspc, systype, ip, netcard):
    test_path = f"{wrkspc}/tests"
    root_report_txt = '/root/test-report.txt'
    root_report_xml = '/root/test-report.xml'
    tests_report_txt = f'{test_path}/test-report.txt'
    tests_report_xml = f'{test_path}/test-report.xml'
    if os.path.exists(ixautomation_config):
        copyfile(ixautomation_config, f"{test_path}/config.py")
    os.chdir(test_path)
    # run ssh API to enable
    cmd = f"python3.6 runtest.py --ip {ip} " \
        f"--password testing --interface {netcard} --api 2.0 --test ssh"
    run(cmd, shell=True)
    # install kyua
    cmd = 'pkg update -f'
    ssh_cmd(cmd, 'root', 'testing', ip)
    cmd = 'pkg install -y kyua'
    ssh_cmd(cmd, 'root', 'testing', ip)
    cmd = "cd /usr/tests; kyua test -k /usr/tests/Kyuafile"
    ssh_cmd(cmd, 'root', 'testing', ip)
    cmd = "cd /usr/tests; kyua report --verbose " \
        "--results-filter passed,skipped,xfail," \
        f"broken,failed --output {root_report_txt}"
    ssh_cmd(cmd, 'root', 'testing', ip)
    cmd = f"cd /usr/tests; kyua report-junit --output={root_report_xml}"
    ssh_cmd(cmd, 'root', 'testing', ip)
    os.chdir(wrkspc)
    # get test-report.txt
    get_file(root_report_txt, tests_report_txt, 'root', 'testing', ip)
    # get test-report.xml
    get_file(root_report_xml, tests_report_xml, 'root', 'testing', ip)


def api_tests(wrkspc, systype, ip, netcard, server_ip):
    if systype == 'truecommand':
        apipath = f"{wrkspc}/tests/api"
        if server_ip is not None:
            server_cfg = """--servers-ip '{"server1": "%s"}'""" % server_ip
        else:
            server_cfg = ''
        cmd = f"python3.6 runtests.py --ip {ip} {server_cfg} --vm-name {vm}"
        print(cmd)
    else:
        apipath = f"{wrkspc}/tests"
        cmd = f"python3.6 runtest.py --ip {ip} " \
            f"--password testing --interface {netcard} --vm-name {vm}"
        if os.path.exists(ixautomation_config):
            copyfile(ixautomation_config, f"{apipath}/config.py")
    os.chdir(apipath)
    run(cmd, shell=True)
    os.chdir(wrkspc)


def websocket_tests(wrkspc, systype, ip, netcard, server_ip):
    if systype == 'truecommand':
        apipath = f"{wrkspc}/tests/websocket"
        if server_ip is not None:
            server_cfg = """--servers-ip '{"server1": "%s"}'""" % server_ip
        else:
            server_cfg = ''
        cmd = f"python3.6 runtests.py --ip {ip} {server_cfg} --vm-name {vm}"
        print(cmd)
    else:
        apipath = f"{wrkspc}/tests"
        cmd = f"python3.6 runtest.py --ip {ip} " \
            f"--password testing --interface {netcard} --vm-name {vm}"
    os.chdir(apipath)
    run(cmd, shell=True)
    os.chdir(wrkspc)


def api2_tests(wrkspc, systype, ip, netcard):
    apipath = f"{wrkspc}/tests"
    if os.path.exists(ixautomation_config):
        copyfile(ixautomation_config, f"{apipath}/config.py")
    os.chdir(apipath)
    cmd = f"python3.6 runtest.py --ip {ip} " \
        f"--password testing --interface {netcard} --api 2.0 --vm-name {vm}"
    run(cmd, shell=True)
    os.chdir(wrkspc)


def webui_tests(wrkspc, ip):
    webUIpath = f"{wrkspc}/tests/"
    os.chdir(webUIpath)
    cmd1 = f"python3.6 -u runtest.py --ip {ip}"
    run(cmd1, shell=True)
    os.chdir(wrkspc)


def destroy_all_vm():
    print(f'Stop all VM')
    vm_stop_all()
    print(f"Removing all VM's files and all ISO's")
    clean_all_vm()
    sys.exit(0)


def destroy_stopped_vm():
    print(f'Stop all VM not running')
    vm_destroy_stopped_vm()
    sys.exit(0)


def destroy_vm(vm):
    print(f'Poweroff and destroy {vm} VM')
    vm_destroy(vm)
    print(f'Removing {vm} VM files and {vm} ISO')
    clean_vm(vm)
    sys.exit(0)
