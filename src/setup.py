#!/usr/bin/env python3

# Author: Eric Turgeon
# License: BSD

import os
import platform
import shutil
from setuptools import setup

__VERSION__ = '22.04.21'

PROGRAM_VERSION = __VERSION__

system = platform.system()

install_requires = [
    'pexpect',
    'pytest==5.3.0',
    'pytest-bdd==4.1.0',
    'pytest-dependency',
    'pytest-rerunfailures',
    'pytest-timeout',
    'requests',
    'selenium'
]

# Hardcode prefix to /usr/local for BSD, Debian and Docker
prefix = '/usr/local'

init_list = [
    'etc/init.d/ixautomation',
]

etc_list = [
    'etc/ixautomation.conf.dist',
]

if system == 'FreeBSD':
    etc_list.append('etc/smb4.conf')

dot_templates_list = [
    'ixautomation/vms/.templates/truenas.conf',
    'ixautomation/vms/.templates/truenas_hdd_boot.xml',
    'ixautomation/vms/.templates/truenas_iso_boot.xml'
]

lib_ixautomation_list = [
    'lib/ixautomation/functions_vm.py',
    'lib/ixautomation/functions.py',
]

data_files = [
    (f'{prefix}/etc', etc_list),
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
