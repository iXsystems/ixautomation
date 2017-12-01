#!/usr/bin/env python3.6

import os
import sys
from subprocess import run
from time import sleep
# from functions import exit_fail


def vm_setup():
    run("vm init", shell=True)


def vm_select_iso(MASTERWRKDIR, systype, workspace):
    VM = MASTERWRKDIR.split('/')[-1]
    if systype == "freenas":
        sysname = "FreeNAS"
    elif systype == "trueos":
        sysname = "TrueOS"
    # if [ -n "$USING_JENKINS" ] ; then return 0 ; fi
    # [ -z "${IXBUILD_ROOT_ZVOL}" ] && export IXBUILD_ROOT_ZVOL="tank"
    # IXBUILD_ROOT_ZVOL = "tank"

    # If we aren't running as part of the build process, list ISO in the iso_dir
    # if [ -z "$SFTPHOST" -o -z "$SFTPUSER" ] ; then
    iso_dir = "%s/tests/%s/iso/" % (workspace, systype)
    # [ ! -d "${iso_dir}" ] && "Directory not found: ${iso_dir}" && exit_clean
    if not os.path.isdir(iso_dir):
        os.makedirs(iso_dir)

    # List ISOs in iso_dir and allow the user to select the target
    iso_list = os.listdir(iso_dir)
    iso_list.remove(".keepme")
    iso_cnt = len(iso_list)

    # Download the latest FreeNas ISO if no ISO found in $iso_dir
    if iso_cnt is 0:
        print('Please put a %s ISO in "%s"' % (sysname, iso_dir))
        sys.exit(1)
        # ask = "No local ISO found would you like to fetch the latest "
        # ask += systype + " ISO? (Y/n): "
        # answer = input(ask)
        # if answer in ["Y", "y", "Yes", "yes", "YES"]:
        #     # cd iso_dir
        #     print("Fetching $iso_name...")
        #     # fetch $iso_url
        #     # USER=$(sh -c 'echo ${SUDO_USER}')
        #     # if USER is empty we are not running with sudo get the real user
        #     # if [ -z "$USER" ] ; then
        #     #    USER=$(id -nu)
        #     #    chown $USER ${SYSNAME}*.iso
        #     # cd -
        # else:
        #     print("Please put a ${SYSNAME} ISO in \"${iso_dir}\"")
        #     # exit_fail()
        #     exit()

    # Repopulate the list iso_dir and allow the user to select the target
    iso_list = os.listdir(iso_dir)
    iso_list.remove(".keepme")
    iso_cnt = len(iso_list)

    # Our to-be-determined file name of the ISO to test; must be inside $iso_dir
    iso_name = ""

    # If there's only one ISO in the $iso_dir, assume it's for testing.
    if iso_cnt == 1:
        # Snatch the first (only) ISO listed in the directory
        iso_name = iso_list[0]
    else:
        # Otherwise, loop until we get a valid user selection
        count = 0
        while True:
            print("Please select which ISO to test (0-%s): " % iso_cnt)
            for iso in iso_list:
                # Listing ISOs
                print(" %s - %s" % (count, iso))

            iso_selection = input("Enter your selection and press [ENTER]: ")
            # add 1 to iso_cnt to look in the full range.
            if int(iso_selection) in range(0, int(iso_cnt + 1)):
                iso_name = iso_list[int(iso_selection)]
                # Confirm our user's ISO selection with another prompt
                ask = 'You have selected "%s", ' % iso_name
                ask += 'is this correct?(Y/n): '
                confirm = input(ask)
                if confirm in ["Y", "y", "Yes", "yes", "YES"]:
                    break
            else:
                print("Invalid selection..")
                sleep(2)
    iso_path = iso_dir + "/" + iso_name
    run("vm iso %s" % iso_path, shell=True)
    run("vm create -t %s %s" % (systype, VM), shell=True)
    run("vm install %s %s" % (VM, iso_name), shell=True)


def vm_start(MASTERWRKDIR):
    VM = MASTERWRKDIR.split('/')[-1]
    run("vm start " + VM, shell=True)
    sleep(5)


def vm_stop(MASTERWRKDIR):
    VM = MASTERWRKDIR.split('/')[-1]
    run("yes | vm stop " + VM, shell=True)
    sleep(10)


def vm_install(MASTERWRKDIR, systype, workspace):
    VM = MASTERWRKDIR.split('/')[-1]
    # Get console device for newly created VM
    sleep(1)
    vm_output = "/tmp/%sconsole.log" % VM
    # Run our expect/tcl script to automate the installation dialog
    expectcnd = 'expect %s/tests/%s/bhyve-installer.exp "%s" "%s"' % (workspace,
                                                                      systype,
                                                                      VM,
                                                                      vm_output)
    run(expectcnd, shell=True)
    # Reset/clear to get native term dimensions
    os.system('clear')
    # echo -e \\033c
    print("Success: Shutting down the installation VM..")
    vm_stop(MASTERWRKDIR)


def vm_boot(MASTERWRKDIR, systype, workspace):
    vm_start(MASTERWRKDIR)
    VM = MASTERWRKDIR.split('/')[-1]
    sleep(1)
    # COM_LISTEN = `cat ${vm_dir}/${VM}/console | cut -d/ -f3`
    vm_output = "/tmp/%sconsole.log" % VM
    expectcnd = 'expect %s/tests/%s/bhyve-bootup.exp "%s" "%s"' % (workspace,
                                                                   systype, VM,
                                                                   vm_output)
    run(expectcnd, shell=True)

    # Reset/clear to get native term dimensions
    os.system('clear')
    # echo -e \\033c
    consolelog = open(vm_output, 'r')
    outputlog = consolelog.read()
    outputloglist = consolelog.readlines()
    if "web user interface" in outputlog:
        for line in outputloglist:
            if "http" in line:
                FNASTESTIP = line.replace("http://" "")
    try:
        FNASTESTIP
    except NameError:
        FNASTESTIP = "0.0.0.0"
        print("FNAESTIP=0.0.0.0")
        print("ERROR: No ip address assigned to VM. FNASTESTIP not set.")
    else:
        print("FNASTESTIP=%s" % FNASTESTIP)
    return FNASTESTIP


def vm_destroy(MASTERWRKDIR):
    VM = MASTERWRKDIR.split('/')[-1]
    run("yes | vm poweroff " + VM, shell=True)
    sleep(5)
    run("yes | vm destroy " + VM, shell=True)


def vm_stop_all():
    run("vm stopall", shell=True)


def vm_destroy_all():
    vm_dir = ""
    run("rm -rf " + vm_dir, shell=True)
