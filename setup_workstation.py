#!/usr/bin/env python3

# Author: Eric Turgeon
# License: BSD

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


if system() == 'Linux':
    setup_Linux()
elif system() == 'FreeBSD':
    setup_FreeBSD()
else:
    print(f'{system()} is not supported yet')
