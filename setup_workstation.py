#!/usr/bin/env python3

import os
from platform import system
from subprocess import run


def sysrc(service, option, rc_path=None):
    arg = f'-f {rc_path}' if rc_path is not None else ''
    run(f'sysrc {arg} {service}={option}', shell=True)


def freebsd_service(service, option):
    run(f'service {service} {option}', shell=True)


def setup_Linux():
    packages = open('linux-packages').read().replace('\n', ' ')
    run(f'apt install -y {packages}', shell=True)


def setup_FreeBSD():
    packages = open('freebsd-packages').read().replace('\n', ' ')
    run(f'pkg install -y {packages}', shell=True)
    sysrc('vm_enable', 'YES')
    sysrc('vm_dir', '/usr/local/ixautomation/vms')
    sysrc('libvirtd_enable', 'YES')
    freebsd_service('vm', 'start')
    freebsd_service('libvirtd', 'start')
    print('Install iXautomation with the following command as root:')
    print('# cd src ; python setup.py install\n')
    print('After to setup the bridge run ixautomation with --setup-bridge and '
          'the interface to setup the bridge like bellow: ')
    print('# ixautomation --setup-bridge <interface>\n')
    print("Replace <interface> with you interface like igb1")


if system() == 'Linux':
    setup_Linux()
elif system() == 'FreeBSD':
    setup_FreeBSD()
else:
    print(f'{system()} is not supported yet')
    exit(1)

# create /data' if it does not exist
if os.path.exists('/data'):
    os.system('chown root:libvirt /data')
    os.system('chmod 770 /data')
else:
    os.mkdir('/data')
    os.system('chown root:libvirt /data')
    os.system('chmod 770 /data')
