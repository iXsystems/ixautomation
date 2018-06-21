#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

import sys

from setuptools import setup

# silence pyflakes, __VERSION__ is properly assigned below...
__VERSION__ = '0.10'
# for line in file('networkmgr').readlines():
#    if (line.startswith('__VERSION__')):
#        exec(line.strip())
PROGRAM_VERSION = __VERSION__

data_files = [
    # ('{prefix}/bin'.format(prefix=sys.prefix), ['bin/ixautomation']),
    ('{prefix}/etc/init.d'.format(prefix=sys.prefix),
     ['etc/init.d/ixautomation']),
    ('{prefix}/etc'.format(prefix=sys.prefix),
     ['etc/ixautomation.conf.dist']),
    ('{prefix}/etc/rc.d'.format(prefix=sys.prefix),
     ['etc/rc.d/ixautomation']),
    ('{prefix}/etc/sudoers.d'.format(prefix=sys.prefix),
     ['etc/sudoers.d/ixautomation']),
    ('{prefix}/ixautomation/vms/.config/'.format(prefix=sys.prefix),
     ['ixautomation/vms/.config/system.conf']),
    ('{prefix}/ixautomation/vms/.templates'.format(prefix=sys.prefix),
     ['ixautomation/vms/.templates/freenas.conf']),
    ('{prefix}/ixautomation/vms/.templates'.format(prefix=sys.prefix),
     ['ixautomation/vms/.templates/trueos.conf']),
    ('{prefix}/lib/ixautomation'.format(prefix=sys.prefix),
     ['lib/ixautomation/functions_vm.py']),
    ('{prefix}/lib/ixautomation'.format(prefix=sys.prefix),
     ['lib/ixautomation/functions.py']),
    ('{prefix}/lib/ixautomation'.format(prefix=sys.prefix),
     ['lib/ixautomation/freenas-11.2-userboot.so']),
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
