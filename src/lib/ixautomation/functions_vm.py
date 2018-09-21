#!/usr/bin/env python3.6

import os
import sys
from subprocess import run, Popen, PIPE
from time import sleep


def vm_setup():
    run("vm init", shell=True)


def vm_select_iso(MASTERWRKDIR, systype, workspace):
    VM = MASTERWRKDIR.split('/')[-1]
    if systype == "freenas":
        sysname = "FreeNAS"
    elif systype == "trueos":
        sysname = "TrueOS"
    iso_dir = f"{workspace}/tests/iso/"
    if not os.path.isdir(iso_dir):
        os.makedirs(iso_dir)
    # List ISOs in iso_dir and allow the user to select the target
    iso_list = os.listdir(iso_dir)
    if len(iso_list) != 0:
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
    new_iso = f"{name_iso}_{VM}.iso"
    os.chdir(iso_dir)
    os.rename(iso_name, new_iso)
    os.chdir(workspace)
    iso_file = iso_dir + new_iso
    iso_path = iso_file.replace("(", "\(").replace(")", "\)")
    run(f"vm iso {iso_path}", shell=True)
    run(f"vm create -t {systype} {VM}", shell=True)
    run(f"vm install {VM} {new_iso}", shell=True)
    return new_iso


def vm_start(MASTERWRKDIR):
    VM = MASTERWRKDIR.split('/')[-1]
    run(f"vm start {VM}", shell=True)
    sleep(5)


def vm_stop(MASTERWRKDIR):
    VM = MASTERWRKDIR.split('/')[-1]
    run(f"yes | vm poweroff {VM}", shell=True)
    wait_text = f"Waitting for VM {VM} to stop "
    print(wait_text, end='', flush=True)
    while True:
        if not os.path.exists("dev/vmm"):
            print('.')
            break
        elif VM in os.listdir("/dev/vmm"):
            print('.', end='', flush=True)
            sleep(1)
        else:
            print('.')
            break
    print(f"VM {VM} successfully stop")


def vm_install(MASTERWRKDIR, systype, workspace):
    VM = MASTERWRKDIR.split('/')[-1]
    testworkspace = f'{workspace}/tests'
    # Get console device for newly created VM
    sleep(3)
    vm_output = f"/tmp/{VM}console.log"
    # change workspace to test directory
    os.chdir(testworkspace)
    # Run our expect/tcl script to automate the installation dialog
    expctcmd = f'expect install.exp "{VM}" "{vm_output}"'
    run(expctcmd, shell=True)
    # Reset/clear to get native term dimensions
    os.system('reset')
    os.system('clear')
    os.chdir(workspace)
    print("Installation successfully completed")
    vm_stop(MASTERWRKDIR)


def vm_boot(MASTERWRKDIR, systype, workspace, netcard):
    vm_start(MASTERWRKDIR)
    VM = MASTERWRKDIR.split('/')[-1]
    testworkspace = f'{workspace}/tests'
    sleep(3)
    # change workspace to test directory
    os.chdir(testworkspace)
    # COM_LISTEN = `cat ${vm_dir}/${VM}/console | cut -d/ -f3`
    vm_output = f"/tmp/{VM}console.log"
    expectcnd = f'expect boot.exp "{VM}" "{vm_output}"'
    run(expectcnd, shell=True)
    # Reset/clear to get native term dimensions
    os.system('reset')
    os.system('clear')
    os.chdir(workspace)
    cmd = f"cat '{vm_output}' | grep -A 5 '{netcard}: ' | grep -a 'inet '"
    cnsl = Popen(cmd, shell=True, stdout=PIPE, universal_newlines=True)
    inetcnsl = cnsl.stdout.readlines()
    if len(inetcnsl) != 0:
        FNASTESTIP = inetcnsl[0].strip().split()[1]
        if systype == 'freenas':
            print(f"FNASTESTIP={FNASTESTIP}")
    else:
        FNASTESTIP = "0.0.0.0"
        if systype == 'freenas':
            print(f"FNASTESTIP={FNASTESTIP}")
            print("ERROR: No ip address assigned to VM. FNASTESTIP not set.")
    return FNASTESTIP


def vm_destroy(MASTERWRKDIR):
    VM = MASTERWRKDIR.split('/')[-1]
    run(f"yes | vm poweroff {VM}", shell=True)
    sleep(5)
    run(f"yes | vm destroy {VM}", shell=True)


def vm_stop_all():
    run("vm stopall", shell=True)


def vm_destroy_all():
    # Remove all vm directory only
    vm_dir = "/usr/local/ixautomation/vms/*"
    run(f"rm -rf {vm_dir}", shell=True)
    # Remove all iso
    iso_dir = "/usr/local/ixautomation/vms/.iso/*"
    run(f"rm -rf {iso_dir}", shell=True)
