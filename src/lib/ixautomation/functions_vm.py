#!/usr/bin/env python3

import os
import re
import sys
from subprocess import run, Popen, PIPE
from time import sleep


def vm_setup():
    run("vm init", shell=True)


def vm_select_iso(workspace):
    iso_dir = f"{workspace}/tests/iso/"
    if not os.path.isdir(iso_dir):
        os.makedirs(iso_dir)
    # List ISOs in iso_dir and allow the user to select the target
    iso_list = os.listdir(iso_dir)
    if ".keepme" in iso_list:
        iso_list.remove(".keepme")
    iso_list.sort()
    # Download the latest TrueNAS ISO if no ISO found in $iso_dir
    if len(iso_list) == 0:
        print(f'Please put a TrueNAS ISO in "{iso_dir}"')
        sys.exit(1)
    # Our to-be-determined file name of the ISO to test; must be inside iso_dir
    iso_name = ""
    # If there's only one ISO in the $iso_dir, assume it's for testing.
    if len(iso_list) == 1:
        # Snatch the first (only) ISO listed in the directory
        iso_name = iso_list[0]
    else:
        # Otherwise, loop until we get a valid user selection
        while True:
            count = 0
            print(f"Please select which ISO to test (0-{len(iso_list) - 1}): ")
            for iso in iso_list:
                # Listing ISOs
                print(f" {count} - {iso}")
                count += 1
            try:
                iso_selection = int(input("Enter your selection and press [ENTER]: "))
                if iso_selection <= count:
                    iso_name = iso_list[int(iso_selection)]
                    break
                else:
                    raise ValueError
            except ValueError:
                print("Invalid selection..")
    iso_file = iso_dir + iso_name
    iso_path = iso_file.replace("(", r"\(").replace(")", r"\)")
    return {'iso-path': iso_path, 'iso-version': iso_name.replace('.iso', '')}


def setup_bhyve_install_template(vm_name, iso_path, tmp_vm_dir):
    template = open('/usr/local/ixautomation/vms/.templates/bhyve_truenas_iso_boot.xml').read()
    new_template = re.sub('nas_name', vm_name, template)
    install_template = re.sub('iso_path', iso_path, new_template)
    save_template = open(f'{tmp_vm_dir}/{vm_name}.xml', 'w')
    save_template.writelines(install_template)
    save_template.close()
    return f'{tmp_vm_dir}/{vm_name}.xml'


def setup_bhyve_first_boot_template(vm_name, tmp_vm_dir):
    template = open('/usr/local/ixautomation/vms/.templates/bhyve_truenas_iso_boot.xml').read()
    boot_template = re.sub('nas_name', vm_name, template)
    save_template = open(f'{tmp_vm_dir}/{vm_name}.xml', 'w')
    save_template.writelines(boot_template)
    save_template.close()
    return f'{tmp_vm_dir}/{vm_name}.xml'


def bhyve_create_disks(vm_name):
    run(f'truncate -s 32G /tmp/ixautomation/{vm_name}/disk0.img', shell=True)
    run(f'truncate -s 20G /tmp/ixautomation/{vm_name}/disk1.img', shell=True)
    run(f'truncate -s 20G /tmp/ixautomation/{vm_name}/disk2.img', shell=True)
    run(f'truncate -s 20G /tmp/ixautomation/{vm_name}/disk3.img', shell=True)


def bhyve_install_vm(tmp_vm_dir, vm_name, sysname, workspace):
    pass


def bhyve_boot_vm():
    pass


def setup_kvm_template(vm_name, tmp_vm_dir):
    template = open('/usr/local/ixautomation/vms/.templates/kvm_truenas.xml').read()
    boot_template = re.sub('nas_name', vm_name, template)
    save_template = open(f'{tmp_vm_dir}/{vm_name}.xml', 'w')
    save_template.writelines(boot_template)
    save_template.close()
    return f'{tmp_vm_dir}/{vm_name}.xml'


def kvm_create_disks(vm_name):
    run(f'qemu-img create -f qcow2 /tmp/ixautomation/{vm_name}/disk0.qcow2 32G', shell=True)
    run(f'qemu-img create -f qcow2 /tmp/ixautomation/{vm_name}/disk1.qcow2 20G', shell=True)
    run(f'qemu-img create -f qcow2 /tmp/ixautomation/{vm_name}/disk2.qcow2 20G', shell=True)
    run(f'qemu-img create -f qcow2 /tmp/ixautomation/{vm_name}/disk3.qcow2 20G', shell=True)


def kvm_install_vm(tmp_vm_dir, vm_name, sysname, workspace):
    pass


def kvm_boot_vm():
    pass


def vm_start(vm_name):
    run(f"vm start {vm_name}", shell=True)
    sleep(2)


def vm_stop(vm_name):
    run(f"yes | vm poweroff {vm_name}", shell=True)
    wait_text = f"Waitting for vm {vm_name} to stop "
    print(wait_text, end='', flush=True)
    while True:
        if not os.path.exists(f"dev/vmm/{vm_name}"):
            print('.')
            break
        elif vm_name in os.listdir(f"/dev/vmm/{vm_name}"):
            print('.', end='', flush=True)
        sleep(1)
    print(f"vm {vm_name} successfully stop")
    sleep(2)


def vm_install(tmp_vm_dir, vm_name, sysname, workspace):
    testworkspace = f'{workspace}/tests'
    # Get console device for newly created vm
    sleep(1)
    vm_output = f"/tmp/{vm_name}console.log"
    # change workspace to test directory
    os.chdir(testworkspace)
    # Run our expect/tcl script to automate the installation dialog
    expctcmd = f'expect install.exp "{vm_name}" "{vm_output}"'
    process = run(expctcmd, shell=True, close_fds=True)
    # console_file = open(vm_output, 'r')
    if process.returncode == 0:
        os.system('reset')
        os.system('clear')
        os.chdir(workspace)
        print(f"{sysname} installation successfully completed")
        vm_stop(vm_name)
        return True
    else:
        print(f"\n{sysname} installation failed")
        return False


def vm_boot(tmp_vm_dir, vm_name, test_type, sysname, workspace, version, keep_alive):
    vm_start(vm_name)
    testworkspace = f'{workspace}/tests'
    sleep(3)
    # change workspace to test directory
    os.chdir(testworkspace)
    # COM_LISTEN = `cat ${vm_dir}/${vm}/console | cut -d/ -f3`
    vm_output = f"/tmp/{vm_name}console.log"
    expectcnd = f'expect boot.exp "{vm_name}" "{vm_output}"'
    run(expectcnd, shell=True)
    console_file = open(vm_output, 'r').read()
    # Reset/clear to get native term dimensions
    os.system('reset')
    os.system('clear')
    os.chdir(workspace)
    try:
        url = re.search(r'http://[0-9]+.[0-9]+.[0-9]+.[0-9]+', console_file)
        vmip = url.group().strip().partition('//')[2]
    except AttributeError:
        if keep_alive:
            exit_and_keep_vm('Failed to get an IP!', vm_name)
        else:
            exit_vm_fail('Failed to get an IP!', vm_name)
    try:
        vmnic = re.search(r'(em|vtnet|enp0s)[0-9]+', console_file).group()
    except AttributeError:
        if keep_alive:
            exit_and_keep_vm('Failed to get a network interface!', vm_name)
        else:
            exit_vm_fail('Failed to get a network interface!', vm_name)
    print(f"{sysname}_IP={vmip}")
    print(f"{sysname}_VM_NAME={vm_name}")
    print(f"{sysname}_VERSION={version}")
    print(f"{sysname}_NIC={vmnic}")
    nas_config = "[NAS_CONFIG]\n"
    nas_config += f"ip = {vmip}\n"
    nas_config += "password = testing\n"
    nas_config += f"version = {version}\n"
    nas_config += f"nic = {vmnic}\n"
    if 'webui' in test_type:
        file = open(f'{testworkspace}/bdd/config.cfg', 'w')
    else:
        file = open(f'{testworkspace}/config.cfg', 'w')
    file.writelines(nas_config)
    file.close()
    return {'ip': vmip, 'nic': vmnic}


def exit_and_keep_vm(msg, vm):
    print(f'## {msg}', f'\nVM name: {vm}')
    sys.exit(1)


def exit_vm_fail(msg, vm_name):
    print(f'## {msg} Clean up time!')
    vm_destroy(vm_name)
    clean_vm(vm_name)
    sys.exit(1)


def vm_destroy(vm_name):
    run(f"yes | vm poweroff {vm_name}", shell=True)
    sleep(1)
    run(f"vm destroy -f {vm_name}", shell=True)
    sleep(1)
    run(f'bhyvectl --destroy --vm={vm_name}', shell=True)
    sleep(1)
    run(f'rm -rf /usr/vms/{vm_name}', shell=True)
    sleep(1)
    run(f"rm -rf /dev/vmm/{vm_name}", shell=True)
    sleep(1)
    run(f"rm -rf /dev/vmm.io/{vm_name}.bootrom", shell=True)


def clean_vm(vm_name):
    # Remove vm directory only
    vm_dir = f"/usr/local/ixautomation/vms/{vm_name}"
    run(f"rm -rf {vm_dir}", shell=True)
    # Remove vm iso
    iso_dir = f"/usr/local/ixautomation/vms/.iso/*{vm_name}.iso"
    run(f"rm -rf {iso_dir}", shell=True)
    run(f"rm -rf /tmp/{vm_name}console.log", shell=True)
    run(f"rm -rf /tmp/ixautomation/{vm_name}", shell=True)
    run(f"rm -rf /dev/vmm/{vm_name}", shell=True)
    run(f"rm -rf /dev/vmm.io/{vm_name}.bootrom", shell=True)


def vm_stop_all():
    run("vm stopall", shell=True)


def clean_all_vm():
    # Remove all vm directory only
    vm_dir = "/usr/local/ixautomation/vms/*"
    run(f"rm -rf {vm_dir}", shell=True)
    # Remove all iso
    iso_dir = "/usr/local/ixautomation/vms/.iso/*"
    run(f"rm -rf {iso_dir}", shell=True)
    run("rm -rf /tmp/*console.log", shell=True)
    run("rm -rf /tmp/ixautomation/*", shell=True)
    run("rm -rf /dev/vmm/*", shell=True)
    run("rm -rf /dev/vmm.io/*", shell=True)


def vm_destroy_stopped_vm():
    cmd = "vm list"
    vm_list = Popen(cmd, shell=True, stdout=PIPE, universal_newlines=True)
    new_vmlist = vm_list.stdout.read()
    for line in new_vmlist.splitlines():
        vm_info = line.split()
        state = vm_info[7]
        vm_name = vm_info[0]
        if state == 'Stopped':
            print(f'Removing {vm_name} VM files and {vm_name} ISO')
            clean_vm(vm_name)
