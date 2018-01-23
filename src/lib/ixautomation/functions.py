#!/usr/bin/env python3.6

import os
import signal
import sys
from subprocess import Popen, run, PIPE
import random
import string
from functions_vm import vm_destroy, vm_setup, vm_select_iso
from functions_vm import vm_boot, vm_install, vm_stop_all, vm_destroy_all


def create_workdir(workspace):
    builddir = "%s/tests/build" % (workspace)
    tempdir = ''.join(random.choices(string.ascii_uppercase, k=4))
    global MASTERWRKDIR
    MASTERWRKDIR = builddir + '/' + tempdir
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    os.makedirs(MASTERWRKDIR)
    return MASTERWRKDIR


def cleanup_workdir():
    mounted = Popen("mount", shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    for line in mounted.stdout:
        if "on %s /" % MASTERWRKDIR in line:
            run("umount -f " + line.split()[2], shell=True)
    mounted = Popen("mount", shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    # Should be done with unmounts
    if "on %s /" % MASTERWRKDIR not in mounted.stdout.read():
        run("chflags -R noschg  " + MASTERWRKDIR, shell=True)
        run("rm -rf " + MASTERWRKDIR, shell=True)


def exit_clean(MASTERWRKDIR):
    vm_destroy(MASTERWRKDIR)
    cleanup_workdir()
    sys.exit(0)
    return 0


def exit_fail(*args):
    vm_destroy(MASTERWRKDIR)
    cleanup_workdir()
    sys.exit(1)
    return 1


def jenkins_vm_tests(workspace, systype, test):
    create_workdir(workspace)
    signal.signal(signal.SIGINT, exit_fail)
    signal.signal(signal.SIGTERM, exit_fail)
    vm_setup()
    vm_select_iso(MASTERWRKDIR, systype, workspace)
    vm_install(MASTERWRKDIR, systype, workspace)
    ip = vm_boot(MASTERWRKDIR, systype, workspace)
    if test == "api-tests":
        jenkins_api_tests(workspace, systype, ip)
    elif test == "middlewared-tests":
        jenkins_middleware_tests(workspace, systype, ip)


def jenkins_middleware_tests(workspace, systype, ip):
    middlewaretestpath = "%s/tests/%s/middlewared-tests" % (workspace, systype)
    os.chdir(middlewaretestpath)
    cmd1 = "python3.6 setup_client.py install --user "
    cmd1 += "--single-version-externally-managed --record"
    run(cmd1, shell=True)
    target = open('target.conf', 'w')
    target.writelines('[Target]\n')
    target.writelines('hostname = %s' % ip)
    target.writelines('api = /api/v2.0/')
    target.writelines('username = "root"')
    target.writelines('password = "testing"')
    target.close()
    cmd2 = "sed -i '' \"s|'freenas'|'testing'|g\" "
    cmd2 += "functional/test_0001_authentication.py"
    run(cmd2, shell=True)
    cmd3 = "python3.6 -m pytest -sv functional "
    cmd3 += "--junitxml=results/middlewared.xml"
    run(cmd3, shell=True)
    os.chdir(workspace)


def jenkins_api_tests(workspace, systype, ip):
    apipath = "%s/tests/%s/api-test" % (workspace, systype)
    os.chdir(apipath)
    cmd = "python3.6 runtest.py --ip %s" % ip
    cmd += " --password testing --interface vtnet0"
    run(cmd, shell=True)
    os.chdir(workspace)


def jenkins_vm_destroy_all():
    vm_stop_all()
    vm_destroy_all()
    sys.exit(0)
    return 0


def jenkins_freenas_webui_tests(workspace, systype):
    webUIpath = "%s/tests/%s/webui-tests" % (workspace, systype)
    os.chdir(webUIpath)
    cmd = "export DISPLAY=:0 && stdbuf -oL python3.6 -u runtest.py"
    run(cmd, shell=True)
    os.chdir(workspace)
