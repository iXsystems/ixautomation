#!/usr/bin/env python3

import json
import os
import re
import requests
import signal
import sys
import time
from subprocess import Popen, run, PIPE, call, DEVNULL
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
    "bridge",
    "ixautomation",
    "vm-ixautomation",
    "wg"
]

capabilities = {
    'RXCSUM,': '-rxcsum',
    'TXCSUM,': '-txcsum',
    'TSO4,': '-tso4',
    'TSO6,': '-tso6',
    'LRO,': '-lro',
    'RXCSUM_IPV6': '-rxcsum6',
    'TXCSUM_IPV6': '-txcsum6'
}


def create_ixautomation_interface():
    ncard = 'ifconfig -l'
    nics = Popen(ncard, shell=True, stdout=PIPE, close_fds=True,
                 universal_newlines=True)
    netcard = nics.stdout.readlines()[0].rstrip().split()
    if "vm-ixautomation" not in netcard and "ixautomation" not in netcard:
        if os.path.exists('/usr/local/ixautomation/vms/.config/system.conf'):
            os.remove('/usr/local/ixautomation/vms/.config/system.conf')
        for nic in netcard:
            nc = re.sub(r'\d+', '', nic)
            if nc not in notnics:
                cmd = f'ifconfig {nic}'
                nic_output = Popen(
                    cmd,
                    shell=True,
                    stdout=PIPE,
                    close_fds=True,
                    universal_newlines=True
                )
                nic_info = nic_output.stdout.read()
                if 'status: active' in nic_info:
                    offload_options = ''
                    for capability in list(capabilities.keys()):
                        if capability in nic_info:
                            offload_options += f' {capabilities[capability]}'
                    break
        call(f'ifconfig {nic}{offload_options}', shell=True)
        call('vm switch create ixautomation', shell=True)
        call(f'vm switch add ixautomation {nic}', shell=True)
        print("ixautomation switch interface is ready")
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
    global vm
    if vm is None:
        vm = ''.join(random.choices(string.ascii_uppercase, k=4))
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


def start_vm(wrkspc, systype, sysname, keep_alive, scale):
    create_workdir()
    set_sig()
    vm_setup()
    select_iso = vm_select_iso(tmp_vm_dir, vm, systype, sysname, wrkspc)
    version = select_iso.partition('_')[0]
    install = vm_install(tmp_vm_dir, vm, systype, sysname, wrkspc)
    if install is False:
        exit_fail('iXautomation stop on installation failure!')
    ip = vm_boot(tmp_vm_dir, vm, systype, sysname, wrkspc, version)
    if ip == '0.0.0.0' and keep_alive is False:
        exit_fail('iXautomation stop because IP is 0.0.0.0!')
    elif ip == '' and keep_alive is False:
        exit_fail('iXautomation stop because IP is None!')
    nic = 'enp0s7' if 'scale' in scale else 'vtnet0'
    print(nic)
    return {'ip': ip, 'netcard': nic, 'iso': select_iso}


def start_automation(wrkspc, systype, sysname, ipnc, test_type, keep_alive, srvr_ip, scale, vm_name, dev_test):
    global vm
    vm = vm_name
    # if ipnc is None start a vm
    if ipnc is None:
        vm_info = start_vm(wrkspc, systype, sysname, keep_alive, scale)
        ip = vm_info['ip']
        netcard = vm_info['netcard']
    else:
        ipnclist = ipnc.split(":")
        ip = ipnclist[0]
        netcard = 'vtnet0' if len(ipnclist) == 1 else ipnclist[1]

    if test_type != 'vmtest':
        run_test(wrkspc, test_type, systype, ip, netcard, srvr_ip, scale, dev_test)

    if keep_alive is False and ipnc is None:
        exit_clean(tmp_vm_dir)


def run_test(wrkspc, test, systype, ip, netcard, server_ip, scale, dev_test):
    if test == "api-tests":
        api_tests(wrkspc, systype, ip, netcard, server_ip, scale, dev_test)
    elif test == "api2-tests":
        api2_tests(wrkspc, systype, ip, netcard)
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
    cmd = f"python3 runtest.py --ip {ip} " \
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


def api_tests(wrkspc, systype, ip, netcard, server_ip, scale, dev_test):
    test_path = f"{wrkspc}/tests"
    cmd = f"python3 runtest.py --ip {ip} " \
        f"--password testing --interface {netcard} --vm-name {vm}{scale}{dev_test}"
    print(cmd)
    if os.path.exists(ixautomation_config):
        copyfile(ixautomation_config, f"{test_path}/config.py")
    os.chdir(test_path)
    run(cmd, shell=True)
    os.chdir(wrkspc)


def api2_tests(wrkspc, systype, ip, netcard):
    test_path = f"{wrkspc}/tests"
    if os.path.exists(ixautomation_config):
        copyfile(ixautomation_config, f"{test_path}/config.py")
    os.chdir(test_path)
    cmd = f"python3 runtest.py --ip {ip} " \
        f"--password testing --interface {netcard} --api 2.0 --vm-name {vm}"
    run(cmd, shell=True)
    os.chdir(wrkspc)


def destroy_all_vm():
    print('Stop all VM')
    vm_stop_all()
    print("Removing all VM's files and all ISO's")
    clean_all_vm()
    sys.exit(0)


def destroy_stopped_vm():
    print('Stop all VM not running')
    vm_destroy_stopped_vm()
    sys.exit(0)


def destroy_vm(vm):
    print(f'Poweroff and destroy {vm} VM')
    vm_destroy(vm)
    print(f'Removing {vm} VM files and {vm} ISO')
    clean_vm(vm)
    sys.exit(0)


header = {'Content-Type': 'application/json', 'Vary': 'accept'}
auth = ('root', 'testing')


def get(test_url):
    get_it = requests.get(
        test_url,
        headers=header,
        auth=auth
    )
    return get_it


def post(test_url, payload=None):
    post_it = requests.post(
        test_url,
        headers=header,
        auth=auth,
        data=json.dumps(payload) if payload else None
    )
    return post_it


def delete(test_url, payload=None):
    delete_it = requests.delete(
        test_url,
        headers=header,
        auth=auth,
        data=json.dumps(payload) if payload else None
    )
    return delete_it


def new_boot(api_url):
    for num in range(1000):
        if f'newboot{num}' not in get(f'{api_url}/bootenv/').text:
            return f'newboot{num}'
    else:
        print('to many BE')
        exit(1)


def delete_old_new_boot_be(api_url, node, new_be):
    bootenv_list = get(f'{api_url}/bootenv/').json()
    for bootenv in bootenv_list:
        if 'newboot' in bootenv['id'] and new_be != bootenv['id'] and not bootenv['activated']:
            print(f'** Deleting {bootenv["id"]} boot environment on {node} **')
            results = delete(f'{api_url}/bootenv/id/{bootenv["id"]}/')
            job_id = results.json()
            while True:
                job_results = get(f'{api_url}/core/get_jobs/?id={job_id}')
                if job_results.json()[0]['state'] in ('SUCCESS', 'FAILED'):
                    break
                time.sleep(1)


def reset_vm(host):
    api_url = f'http://{host}/api/v2.0'
    be = new_boot(api_url)
    time.sleep(0.5)
    print(f'** Create {be} boot environment on {host} **')
    post(f'{api_url}/bootenv/', {"name": be, "source": "Initial-Install"})
    time.sleep(0.5)
    print(f'** Activating {be} boot environment on {host} **')
    post(f'{api_url}/bootenv/id/{be}/activate/')
    time.sleep(0.5)
    delete_old_new_boot_be(api_url, host, be)
    print(f'** rebooting NAS {host} **')
    post(f'{api_url}/system/reboot/')

    process = run(['ping', '-c', '1', host], stdout=DEVNULL)
    while process.returncode == 0:
        time.sleep(5)
        process = run(['ping', '-c', '1', host], stdout=DEVNULL)

    process = run(['ping', '-c', '1', host], stdout=DEVNULL)
    while process.returncode != 0:
        time.sleep(5)
        process = run(['ping', '-c', '1', host], stdout=DEVNULL)

    node = api_url.partition('//')[2].partition('/api')[0]
    status_code = 0
    while status_code != 200:
        try:
            status_code = get(f'{api_url}/bootenv/').status_code
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            continue
    results = get(f'{api_url}/bootenv/id/{be}/')
    assert results.json()['activated'] is True, results.text
    print(f'** Node {node} is online and ready **')
    exit(0)
