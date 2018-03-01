#!/usr/bin/env python3.6

import os
import signal
import sys
from subprocess import Popen, run, PIPE
from shutil import copyfile
import random
import string
from functions_vm import vm_destroy, vm_setup, vm_select_iso
from functions_vm import vm_boot, vm_install, vm_stop_all, vm_destroy_all
from pyvirtualdisplay import Display


def create_workdir():
    builddir = "/tmp/ixautomation"
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


def jenkins_vm_tests(workspace, systype, ipnc, test):
    if ipnc is None:
        create_workdir()
        signal.signal(signal.SIGINT, exit_fail)
        signal.signal(signal.SIGTERM, exit_fail)
        vm_setup()
        vm_select_iso(MASTERWRKDIR, systype, workspace)
        vm_install(MASTERWRKDIR, systype, workspace)
        netcard = "vtnet0"
        ip = vm_boot(MASTERWRKDIR, systype, workspace, netcard)
    else:
        if ":" in ipnc:
            ipnclist = ipnc.split(":")
            ip = ipnclist[0]
            netcard = ipnclist[1]
        else:
            ip = ipnc
            netcard = "vtnet0"
    if test == "api-tests":
        jenkins_api_tests(workspace, systype, ip, netcard)
    elif test == "api2-tests":
        jenkins_api2_tests(workspace, systype, ip, netcard)
    elif test == "middlewared-tests":
        jenkins_middleware_tests(workspace, systype, ip, netcard)
    elif test == "webui-tests":
        jenkins_webui_tests(workspace, ip)


def jenkins_api_tests(workspace, systype, ip, netcard):
    apipath = "%s/tests" % (workspace)
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", apipath + "/config.py")
    os.chdir(apipath)
    cmd = "python3.6 runtest.py --ip %s " % ip
    cmd += "--password testing --interface %s" % netcard
    run(cmd, shell=True)
    os.chdir(workspace)


def jenkins_api2_tests(workspace, systype, ip, netcard):
    apipath = "%s/tests" % (workspace)
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", apipath + "/config.py")
    os.chdir(apipath)
    cmd = "python3.6 runtest.py --ip %s " % ip
    cmd += "--password testing --interface %s --api 2.0" % netcard
    run(cmd, shell=True)
    os.chdir(workspace)


def jenkins_middleware_tests(workspace, systype, ip, netcard):
    middlewared_path = "%s/src/middlewared" % workspace
    middlewared_test_path = "%s/middlewared/pytest" % middlewared_path
    os.chdir(middlewared_path)
    cmd2 = "pip-3.6 uninstall -y middlewared.client"
    run(cmd2, shell=True)
    cmd3 = "python3.6 setup_client.py install --user "
    cmd3 += "--single-version-externally-managed --record $(mktemp)"
    run(cmd3, shell=True)
    # Run network test only
    apipath = "%s/tests" % (workspace)
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", apipath + "/config.py")
    os.chdir(apipath)
    cmd = "python3.6 runtest.py --ip %s " % ip
    cmd += "--password testing --interface %s --test network" % netcard
    run(cmd, shell=True)
    os.chdir(workspace)
    os.chdir(middlewared_test_path)
    target = open('target.conf', 'w')
    target.writelines('[Target]\n')
    target.writelines('hostname = %s\n' % ip)
    target.writelines('api = /api/v2.0/\n')
    target.writelines('username = root\n')
    target.writelines('password = testing\n')
    target.close()
    cmd4 = "sed -i '' \"s|'freenas'|'testing'|g\" "
    cmd4 += "functional/test_0001_authentication.py"
    run(cmd4, shell=True)
    cmd5 = "python3.6 -m pytest -sv functional "
    cmd5 += "--junitxml=results/middlewared.xml"
    run(cmd5, shell=True)
    os.chdir(workspace)


def jenkins_webui_tests(workspace, ip):
    webUIpath = "%s/tests/" % workspace
    os.chdir(webUIpath)
    try:
        import xmlrunner
    except ImportError:
        cmd = "pip-3.6 install unittest-xml-reporting"
        run(cmd, shell=True)
    display = Display(visible=0, size=(800, 600))
    display.start()
    os.chdir(webUIpath)
    cmd1 = "python3.6 -u runtest.py --ip %s" % ip
    run(cmd1, shell=True)
    os.chdir(workspace)
    display.stop()


def jenkins_vm_destroy_all():
    vm_stop_all()
    vm_destroy_all()
    sys.exit(0)
    return 0
