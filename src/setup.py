#!/usr/bin/env python3

# Author: Eric Turgeon
# License: BSD

import os
import shutil
from platform import system
from setuptools import setup
from time import sleep
from subprocess import run

__VERSION__ = '22.04.21'

PROGRAM_VERSION = __VERSION__

install_requires = [
    'boto3',
    'pexpect',
    'pytest==5.3.0',
    'pytest-bdd==4.1.0',
    'pytest-dependency',
    'pytest-rerunfailures',
    'pytest-timeout',
    'pytz',
    'pyyaml',
    'requests',
    'selenium==3.141.0' if system() == 'FreeBSD' else 'selenium',
    'websocket',
    'websocket-client'
]

# Hardcode prefix to /usr/local for BSD, Debian and Docker
prefix = '/usr/local'

init_list = [
    'etc/init.d/ixautomation',
]

etc_list = [
    'etc/ixautomation.conf.dist',
]

if system() == 'FreeBSD':
    etc_list.append('etc/smb4.conf')

dot_templates_list = [
    'ixautomation/vms/.templates/truenas.conf',
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
    install_requires=install_requires,
    scripts=['bin/ixautomation']
)


if system() == 'Linux':
    os.remove('etc/smb.conf')

# Since we can import a module installed from and in setup.py we run a separate
# script to path pytest_bdd for Jira.
sleep(1)
run('python3 patch_pytest_bdd.py', shell=True)
