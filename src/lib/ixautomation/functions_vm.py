#!/usr/bin/env python3.6

import os
import sys
from subprocess import run
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
    iso_cnt = len(iso_list)
    # Download the latest FreeNas ISO if no ISO found in $iso_dir
    if iso_cnt is 0:
        print(f'Please put a {sysname} ISO in "{iso_dir}"')
        sys.exit(1)
    # Our to-be-determined file name of the ISO to test; must be inside iso_dir
    iso_name = ""
    # If there's only one ISO in the $iso_dir, assume it's for testing.
    if iso_cnt == 1:
        # Snatch the first (only) ISO listed in the directory
        iso_name = iso_list[0]
    else:
        # Otherwise, loop until we get a valid user selection
        count = 0
        while True:
            print(f"Please select which ISO to test (0-{iso_cnt}): ")
            for iso in iso_list:
                # Listing ISOs
                print(f" {count} - {iso}")
                count += 1
            iso_selection = input("Enter your selection and press [ENTER]: ")
            # add 1 to iso_cnt to look in the full range.
            if int(iso_selection) in range(0, int(iso_cnt + 1)):
                iso_name = iso_list[int(iso_selection)]
                break
            else:
                print("Invalid selection..")
                sleep(2)
    name_iso = iso_name.replace('.iso', '').partition('_')[0]
    new_iso = f"{name_iso}_{vm}.iso"
    os.chdir(iso_dir)
    os.rename(iso_name, new_iso)
    os.chdir(workspace)
    iso_file = iso_dir + new_iso
    iso_path = iso_file.replace("(", "\(").replace(")", "\)")
    run(f"vm iso {iso_path}", shell=True)
    run(f"vm create -t {systype} {vm}", shell=True)
    run(f"vm install {vm} {new_iso}", shell=True)
    return new_iso


def vm_start(vm):
    run(f"vm start {vm}", shell=True)
    sleep(5)


def vm_stop(vm):
    run(f"yes | vm poweroff {vm}", shell=True)
    wait_text = f"Waitting for vm {vm} to stop "
    print(wait_text, end='', flush=True)
    while True:
        if not os.path.exists("dev/vmm"):
            print('.')
            break
        elif vm in os.listdir("/dev/vmm"):
            print('.', end='', flush=True)
            sleep(1)
        else:
            print('.')
            break
    print(f"vm {vm} successfully stop")


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
        if systype == 'freenas' and 'http://' in line:
            # Reset/clear to get native term dimensions
            os.system('reset')
            os.system('clear')
            os.chdir(workspace)
            VMIP = line.rstrip().split('//')[1]
            print(f"{sysname}_IP={VMIP}")
            print(f"{sysname}_VM_NAME={vm}")
            return VMIP
        elif systype == 'trueview' and 'IP Address:' in line:
            os.system('reset')
            os.system('clear')
            os.chdir(workspace)
            VMIP = line.split(':')[1].strip()
            print(f"{sysname}_IP={VMIP}")
            print(f"{sysname}_VM_NAME={vm}")
            return VMIP
    else:
        VMIP = "0.0.0.0"
        print(f"{sysname}_IP={VMIP}")
        print(f"{sysname}_VM_NAME={vm}")
        return VMIP


def vm_destroy(vm):
    run(f"yes | vm poweroff {vm}", shell=True)
    sleep(5)
    run(f"yes | vm destroy {vm}", shell=True)


def clean_vm(vm):
    # Remove vm directory only
    vm_dir = f"/usr/local/ixautomation/vms/{vm}"
    run(f"rm -rf {vm_dir}", shell=True)
    # Remove vm iso
    iso_dir = f"/usr/local/ixautomation/vms/.iso/*{vm}.iso"
    run(f"rm -rf {iso_dir}", shell=True)


def vm_stop_all():
    run("vm stopall", shell=True)


def clean_all_vm():
    # Remove all vm directory only
    vm_dir = "/usr/local/ixautomation/vms/*"
    run(f"rm -rf {vm_dir}", shell=True)
    # Remove all iso
    iso_dir = "/usr/local/ixautomation/vms/.iso/*"
    run(f"rm -rf {iso_dir}", shell=True)
