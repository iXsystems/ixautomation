#!/usr/bin/env python3.6

import os
import signal
import atexit
import sys
import shutil
from subprocess import Popen, run, PIPE
from shutil import copyfile
import random
import string
from functions_vm import vm_destroy, vm_setup, vm_select_iso
from functions_vm import vm_boot, vm_install, vm_stop_all, vm_destroy_all


def create_workdir():
    builddir = "/tmp/ixautomation"
    global tempdir
    tempdir = ''.join(random.choices(string.ascii_uppercase, k=4))
    global MASTERWRKDIR
    MASTERWRKDIR = builddir + '/' + tempdir
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    os.makedirs(MASTERWRKDIR)
    return MASTERWRKDIR


def cleanup_workdir(MASTERWRKDIR):
    VM = MASTERWRKDIR.split('/')[-1]
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
    os.remove(f'/usr/local/ixautomation/vms/.iso/{VM}.iso')


def exit_clean(MASTERWRKDIR):
    global terminated
    terminated = False
    print('## iXautomation is stopping! cleaning up time!')
    vm_destroy(MASTERWRKDIR)
    cleanup_workdir(MASTERWRKDIR)
    print("Gracefully cleaned and stopped")
    sys.exit(0)


def exit_fail(arg1, arg2):
    global terminated
    terminated = False
    print('## iXautomation got terminated! cleaning up time!')
    vm_destroy(MASTERWRKDIR)
    cleanup_workdir(MASTERWRKDIR)
    print("Gracefully cleaned and stopped")
    sys.exit(1)


def get_terinated():
    if terminated is True:
        print('## iXautomation got cancel! cleaning up time!')
        vm_destroy(MASTERWRKDIR)
        cleanup_workdir(MASTERWRKDIR)
        print("Gracefully cleaned and stopped")
        sys.exit(1)


def jenkins_vm_tests(workspace, systype, ipnc, test, keep_alive):
    global terminated
    terminated = True
    if ipnc is None:
        create_workdir()
        atexit.register(get_terinated)
        signal.signal(signal.SIGTERM, exit_fail)
        signal.signal(signal.SIGHUP, exit_fail)
        signal.signal(signal.SIGINT, exit_fail)
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
    # clean up vm if --keep-alive is not specify
    terminated = False
    if keep_alive is False:
        exit_clean(MASTERWRKDIR)


def jenkins_api_tests(workspace, systype, ip, netcard):
    apipath = "%s/tests" % (workspace)
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", apipath + "/config.py")
    os.chdir(apipath)
    cmd = f"python3.6 runtest.py --ip {ip} " \
          f"--password testing --interface {netcard}"
    run(cmd, shell=True)
    os.chdir(workspace)


def jenkins_api2_tests(workspace, systype, ip, netcard):
    apipath = "%s/tests" % (workspace)
    if os.path.exists("/usr/local/etc/ixautomation.conf"):
        copyfile("/usr/local/etc/ixautomation.conf", apipath + "/config.py")
    os.chdir(apipath)
    cmd = f"python3.6 runtest.py --ip {ip} " \
          f"--password testing --interface {netcard} --api 2.0"
    run(cmd, shell=True)
    os.chdir(workspace)


def jenkins_middleware_tests(workspace, systype, ip, netcard):
    middlewared_path = f"{workspace}/src/middlewared"
    middlewared_test_path = f"{middlewared_path}/middlewared/pytest"
    virtualenv_path = '/usr/local/ixautomation/virtualenv'
    global virtualenv_tmp_path
    virtualenv_tmp_path = f'{virtualenv_path}/{tempdir}'
    virtualenv_pip = f'{virtualenv_tmp_path}/bin/pip'
    virtualenv_python = f'{virtualenv_tmp_path}/bin/python'
    ixautomationconfig = "/usr/local/etc/ixautomation.conf"
    apipath = f"{workspace}/tests"
    apiconfig = f"{apipath}/config.py"
    os.chdir(virtualenv_path)
    run(f'virtualenv-3.6 {tempdir}', shell=True)
    run(f'{virtualenv_pip} install pytest', shell=True)
    run(f'{virtualenv_pip} install requests', shell=True)
    os.chdir(middlewared_path)
    run(f"{virtualenv_python} setup_client.py install", shell=True)
    if os.path.exists(ixautomationconfig):
        copyfile(ixautomationconfig, apiconfig)
    os.chdir(apipath)
    cmd = f"python3.6 runtest.py --ip {ip} " \
          f"--password testing --interface {netcard} --test network"
    run(cmd, shell=True)
    os.chdir(middlewared_test_path)
    target = open('target.conf', 'w')
    target.writelines('[Target]\n')
    target.writelines('hostname = %s\n' % ip)
    target.writelines('api = /api/v2.0/\n')
    target.writelines('username = root\n')
    target.writelines('password = testing\n')
    target.close()
    cmd4 = "sed -i '' \"s|'freenas'|'testing'|g\" " \
           "functional/test_0001_authentication.py"
    run(cmd4, shell=True)
    cmd5 = f"{virtualenv_python} -m pytest -sv functional " \
           "--junitxml=results/middlewared.xml"
    run(cmd5, shell=True)
    os.chdir(workspace)
    # remove virtualenv after test are done
    shutil.rmtree(virtualenv_tmp_path)


def jenkins_webui_tests(workspace, ip):
    webUIpath = "%s/tests/" % workspace
    os.chdir(webUIpath)
    cmd1 = "python3.6 -u runtest.py --ip %s" % ip
    run(cmd1, shell=True)
    os.chdir(workspace)


def jenkins_vm_destroy_all():
    vm_stop_all()
    vm_destroy_all()
    sys.exit(0)
    return 0
