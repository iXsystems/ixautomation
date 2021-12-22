#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

import os
import platform
import shutil
from setuptools import setup

__VERSION__ = '21.12.21'

PROGRAM_VERSION = __VERSION__

system = platform.system()

install_requires = [
    'pexpect',
    'pytest',
    'pytest-bdd==4.1.0',
    'pytest-dependency',
    'pytest-timeout',
    'requests',
    'selenium'
]

# Hardcode prefix to /usr/local for BSD, Debian and Docker
prefix = '/usr/local'

init_list = [
    'etc/init.d/ixautomation',
    'etc/init.d/ixautomation-nat'
]

etc_list = [
    'etc/ixautomation.conf.dist',
    'etc/dnsmasq.conf'
]

if system == 'FreeBSD':
    etc_list.append('etc/smb4.conf')

dot_templates_list = [
    'ixautomation/vms/.templates/freenas.conf',
    'ixautomation/vms/.templates/freenas_webui.conf'
]

lib_ixautomation_list = [
    'lib/ixautomation/functions_vm.py',
    'lib/ixautomation/functions.py',
    'lib/ixautomation/freenas-11.2-userboot.so'
]

data_files = [
    (f'{prefix}/etc', etc_list),
    (f'{prefix}/etc/rc.d', ['etc/rc.d/ixautomation']),
    (f'{prefix}/etc/sudoers.d', ['etc/sudoers.d/ixautomation']),
    (f'{prefix}/ixautomation/vms/.templates', dot_templates_list),
    (f'{prefix}/lib/ixautomation', lib_ixautomation_list)
]

if system == 'Linux':
    shutil.copyfile('etc/smb4.conf', 'etc/smb.conf')
    data_files.append(('/etc/samba', ['etc/smb.conf']))

setup(
    name="ixautomation",
    version=PROGRAM_VERSION,
    description="iXsystems automation framework",
    license='BSD',
    author='iXsystems',
    url='https://github/ixsystems/ixautomation/',
    package_dir={'': '.'},
    data_files=data_files,
    install_requires=install_requires,
    scripts=['bin/ixautomation']
)


if system == 'Linux':
    os.remove('etc/smb.conf')
