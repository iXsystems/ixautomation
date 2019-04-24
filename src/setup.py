#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

import sys
from setuptools import setup


# silence pyflakes, __VERSION__ is properly assigned below...
__VERSION__ = '19.04.25'

PROGRAM_VERSION = __VERSION__

prefix = sys.prefix

init_list = [
    'etc/init.d/ixautomation',
    'etc/init.d/ixautomation-nat'
]

etc_list = [
    'etc/ixautomation.conf.dist',
    'etc/dnsmasq.conf'
]

dot_config_list = [
    'ixautomation/vms/.config/system.conf'
]

dot_templates_list = [
    'ixautomation/vms/.templates/freenas.conf',
    'ixautomation/vms/.templates/freenas11_2.conf',
    'ixautomation/vms/.templates/freenas_webui.conf',
    'ixautomation/vms/.templates/trueos.conf',
    'ixautomation/vms/.templates/trueview.conf'
]

lib_ixautomation_list = [
    'lib/ixautomation/functions_vm.py',
    'lib/ixautomation/functions.py',
    'lib/ixautomation/freenas-11.2-userboot.so'
]

data_files = [
    (f'{prefix}/etc/init.d', init_list),
    (f'{prefix}/etc', etc_list),
    (f'{prefix}/etc/rc.d', ['etc/rc.d/ixautomation']),
    (f'{prefix}/etc/sudoers.d', ['etc/sudoers.d/ixautomation']),
    (f'{prefix}/ixautomation/vms/.config/', dot_config_list),
    (f'{prefix}/ixautomation/vms/.templates', dot_templates_list),
    (f'{prefix}/lib/ixautomation', lib_ixautomation_list)
]

setup(
    name="ixautomation",
    version=PROGRAM_VERSION,
    description="Ixsystems automation framwork",
    license='BSD',
    author='Ixsystems',
    url='https://github/ixsystems/ixautomation/',
    package_dir={'': '.'},
    data_files=data_files,
    install_requires=['setuptools'],
    scripts=['bin/ixautomation']
)
