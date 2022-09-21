#!/usr/bin/env python3

# Author: Eric Turgeon
# License: BSD

import os
import shutil
from platform import system
from setuptools import setup

__VERSION__ = '22.04.21'

PROGRAM_VERSION = __VERSION__

# Hardcode prefix to /usr/local for BSD, Debian and Docker
prefix = '/usr/local'

init_list = [
    'etc/init.d/ixautomation',
]

etc_list = []

if system() == 'FreeBSD':
    etc_list.append('etc/smb4.conf')

dot_templates_list = [
    'ixautomation/vms/.templates/bhyve_truenas_hdd_boot.xml',
    'ixautomation/vms/.templates/bhyve_truenas_iso_boot.xml',
    'ixautomation/vms/.templates/kvm_scale_api.xml',
    'ixautomation/vms/.templates/kvm_truenas.xml'
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

if system() == 'Linux':
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
    scripts=['bin/ixautomation']
)


if system() == 'Linux':
    os.remove('etc/smb.conf')
