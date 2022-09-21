#!/usr/bin/env python3

import os
import re
from platform import system
from subprocess import run
from time import sleep

BRIDGE_RULES = """ACTION=="add", SUBSYSTEM=="module", KERNEL=="br_netfilter", \
      RUN+="/usr/lib/systemd/systemd-sysctl --prefix=/net/bridge"
"""

BRIDGE_CONF = """net.bridge.bridge-nf-call-arptables = 0
net.bridge.bridge-nf-call-ip6tables = 0
net.bridge.bridge-nf-call-iptables = 0
"""


def sysrc(service, option, rc_path=None):
    arg = f'-f {rc_path}' if rc_path is not None else ''
    run(f'sysrc {arg} {service}={option}', shell=True)


def freebsd_service(service, option):
    run(f'service {service} {option}', shell=True)


def setup_Linux():
    packages = open('linux-packages').read().replace('\n', ' ')
    run(f'apt install -y {packages}', shell=True)
    sleep(1)
    qemuconf = open('/etc/libvirt/qemu.conf').read()
    if '#user = "root"' in qemuconf:
        qemuconf = re.sub(r'#user = "root"', 'user = "root"', qemuconf)
    if '#user = "root"' in qemuconf:
        qemuconf = re.sub(r'#group = "root"', 'group = "root"', qemuconf)
    save_parser_file = open('/etc/libvirt/qemu.conf', 'w')
    save_parser_file.writelines(qemuconf)
    save_parser_file.close()

    save_bridge_rules = open('/etc/udev/rules.d/99-bridge.rules', 'w')
    save_bridge_rules.writelines(BRIDGE_RULES)
    save_bridge_rules.close()

    save_bridge_conf = open('/etc/sysctl.d/bridge.conf', 'w')
    save_bridge_conf.writelines(BRIDGE_CONF)
    save_bridge_conf.close()
    sleep(1)
    run('sysctl -p /etc/sysctl.d/bridge.conf', shell=True)
    run('systemctl restart libvirtd', shell=True)
    sleep(1)


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
