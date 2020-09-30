#!/usr/bin/env python3

import os
import sys
from subprocess import run, Popen, PIPE
from time import sleep


def vm_setup():
    run("vm init", shell=True)


def vm_select_iso(tmp_vm_dir, vm, systype, sysname, workspace):
    iso_dir = f"{workspace}/tests/iso/"
    if not os.path.isdir(iso_dir):
        os.makedirs(iso_dir)
    # List ISOs in iso_dir and allow the user to select the target
    iso_list = os.listdir(iso_dir)
    if ".keepme" in iso_list:
        iso_list.remove(".keepme")
    iso_list.sort()
    # Download the latest FreeNas ISO if no ISO found in $iso_dir
    if len(iso_list) == 0:
        print(f'Please put a {sysname} ISO in "{iso_dir}"')
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
    name_iso = iso_name.replace('.iso', '').partition('_')[0]
    new_iso = f"{name_iso}_{vm}.iso"
    os.chdir(iso_dir)
    os.rename(iso_name, new_iso)
    os.chdir(workspace)
    iso_file = iso_dir + new_iso
    iso_path = iso_file.replace("(", "\(").replace(")", "\)")
    run(f"vm iso {iso_path}", shell=True)
    if "11.2" in iso_file:
        run(f"vm create -t {systype}11_2 {vm}", shell=True)
    else:
        run(f"vm create -t {systype} {vm}", shell=True)
    run(f"vm install {vm} {new_iso}", shell=True)
    return new_iso


def vm_start(vm):
    run(f"vm start {vm}", shell=True)
    sleep(2)


def vm_stop(vm):
    run(f"yes | vm poweroff {vm}", shell=True)
    wait_text = f"Waitting for vm {vm} to stop "
    print(wait_text, end='', flush=True)
    while True:
        if not os.path.exists(f"dev/vmm/{vm}"):
            print('.')
            break
        elif vm in os.listdir(f"/dev/vmm/{vm}"):
            print('.', end='', flush=True)
        sleep(1)
    print(f"vm {vm} successfully stop")
    sleep(2)


def vm_install(tmp_vm_dir, vm, systype, sysname, workspace):
    testworkspace = f'{workspace}/tests'
    # Get console device for newly created vm
    sleep(3)
    vm_output = f"/tmp/{vm}console.log"
    # change workspace to test directory
    os.chdir(testworkspace)
    # Run our expect/tcl script to automate the installation dialog
    expctcmd = f'expect install.exp "{vm}" "{vm_output}"'
    process = run(expctcmd, shell=True, close_fds=True)
    # console_file = open(vm_output, 'r')
    if process.returncode == 0:
        os.system('reset')
        os.system('clear')
        os.chdir(workspace)
        print(f"{sysname} installation successfully completed")
        vm_stop(vm)
        return True
    else:
        print(f"\n{sysname} installation failed")
        return False


def vm_boot(tmp_vm_dir, vm, systype, sysname, workspace):
    vm_start(vm)
    testworkspace = f'{workspace}/tests'
    sleep(3)
    # change workspace to test directory
    os.chdir(testworkspace)
    # COM_LISTEN = `cat ${vm_dir}/${vm}/console | cut -d/ -f3`
    vm_output = f"/tmp/{vm}console.log"
    expectcnd = f'expect boot.exp "{vm}" "{vm_output}"'
    run(expectcnd, shell=True)
    console_file = open(vm_output, 'r').readlines()
    reversed_console = reversed(console_file)
    for line in reversed_console:
        if 'freenas' in systype and 'http://' in line and '172.17' not in line:
            # Reset/clear to get native term dimensions
            os.system('reset')
            os.system('clear')
            os.chdir(workspace)
            VMIP = line.rstrip().split('//')[1]
            print(f"{sysname}_IP={VMIP}")
            print(f"{sysname}_VM_NAME={vm}")
            if 'webui' in systype:
                vm_config = f"VM_NAME={vm}\nIP={VMIP}"
                file = open(f'{testworkspace}/vm_config', 'w')
                file.writelines(vm_config)
                file.close()
            return VMIP
    else:
        VMIP = "0.0.0.0"
        print(f"{sysname}_IP={VMIP}")
        print(f"{sysname}_VM_NAME={vm}")
        return VMIP


def vm_destroy(vm):
    run(f"yes | vm poweroff {vm}", shell=True)
    sleep(2)


def clean_vm(vm):
    # Remove vm directory only
    vm_dir = f"/usr/local/ixautomation/vms/{vm}"
    run(f"rm -rf {vm_dir}", shell=True)
    # Remove vm iso
    iso_dir = f"/usr/local/ixautomation/vms/.iso/*{vm}.iso"
    run(f"rm -rf {iso_dir}", shell=True)
    run(f"rm -rf /tmp/{vm}console.log", shell=True)
    run(f"rm -rf /tmp/ixautomation/{vm}", shell=True)


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
