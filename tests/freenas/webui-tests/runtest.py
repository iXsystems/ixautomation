#/usr/bin/env python

from subprocess import call
from os import path
#when running for jenkins user driver, and when running on  an ubuntu system user driverU, because of  capabilities
#from driver import webDriver
from driverU import webDriver
## Importing test

from login import run_login_test
# from guide import run_guide_test
from group import run_create_group_test
from user import run_create_user_test
from ssh import run_configure_ssh_test
from afp import run_configure_afp_test
from webdav import run_configure_webdav_test
from logout import run_logout_test


global runDriver
runDriver = webDriver()


## Starting the test and genewratinf result
run_login_test(runDriver)
# run_guide_test(runDriver)
run_create_user_test(runDriver)
run_create_group_test(runDriver)
run_configure_ssh_test(runDriver)
run_configure_afp_test(runDriver)
run_configure_webdav_test(runDriver)
run_logout_test(runDriver)

## Example test run
# run_creat_nameofthetest(runDriver)

##cleaning up files
if path.exists('login.pyc'):
    call(["rm", "login.pyc"])

if path.exists('source.pyc'):
    call(["rm", "source.pyc"])

if path.exists('user.pyc'):
    call(["rm", "user.pyc"])

if path.exists('ssh.pyc'):
    call(["rm", "ssh.pyc"])

if path.exists('group.pyc'):
    call(["rm", "group.pyc"])

if path.exists('logout.pyc'):
    call(["rm", "logout.pyc"])

if path.exists('guide.pyc'):
    call(["rm", "guide.pyc"])

if path.exists('driver.pyc'):
    call(["rm", "driver.pyc"])

if path.exists('afp.pyc'):
    call(["rm", "afp.pyc"])

if path.exists('webdav.pyc'):
    call(["rm", "webdav.pyc"])

#if path.exists('example.pyc'):
#    call(["rm", "example.pyc"])

if path.exist('geckodriver.log'):
    call(["rm", "geckodriver.log"])

if path.exists('__pycache__'):
    call(["rm", "-r", "__pycache__"])

if path.isdir('.cache'):
    call(["rm", "-r", ".cache"])
