#!/usr/bin/env python3.6

# Author: Eric Turgeon
# License: BSD

import os
import sys

from setuptools import setup

# silence pyflakes, __VERSION__ is properly assigned below...
__VERSION__ = '0.10'
# for line in file('networkmgr').readlines():
#    if (line.startswith('__VERSION__')):
#        exec(line.strip())
PROGRAM_VERSION = __VERSION__

data_files = [
    ('{prefix}/bin'.format(prefix=sys.prefix), ['src/bin/ixautomation']),
    ('{prefix}/etc/init.d'.format(prefix=sys.prefix), ['src/etc/init.d/ixautomation']),
    ('{prefix}/etc'.format(prefix=sys.prefix), ['src/etc/ixautomation.conf.dist']),
    ('{prefix}/etc/rc.d'.format(prefix=sys.prefix), ['src/etc/rc.d/ixautomation']),
    ('{prefix}/etc/sudoers.d'.format(prefix=sys.prefix), ['src/etc/sudoers.d/ixautomation']),
    ('{prefix}/ixautomation/vms/.config/'.format(prefix=sys.prefix), ['src/ixautomation/vms/.config/system.conf']),
    ('{prefix}/ixautomation/vms/.templates'.format(prefix=sys.prefix), ['src/ixautomation/vms/.templates/freenas.conf']),
    ('{prefix}/ixautomation/vms/.templates'.format(prefix=sys.prefix), ['src/ixautomation/vms/.templates/trueos.conf']),
    ('{prefix}/lib/ixautomation'.format(prefix=sys.prefix), ['src/lib/ixautomation/functions-vm.sh']),
    ('{prefix}/lib/ixautomation'.format(prefix=sys.prefix), ['src/lib/ixautomation/functions.sh']),
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
    #scripts=['src/bin/ixautomation',]
)
# cmdclass = cmdclass,