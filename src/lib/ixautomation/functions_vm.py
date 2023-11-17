#!/usr/bin/env python3

import os
import re
import sys
from platform import system
from subprocess import run, Popen, PIPE
from time import sleep


if system() == 'FreeBSD':
    os.environ['VIRSH_DEFAULT_CONNECT_URI'] = 'bhyve:///system'
else:
    pass


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


def setup_bhyve_install_template(vm_name, iso_path, vm_data_dir):
    template = open('/usr/local/ixautomation/vms/.templates/bhyve_truenas_iso_boot.xml').read()
    new_template = re.sub('nas_name', vm_name, template)
    install_template = re.sub('iso_path', iso_path, new_template)
    save_template = open(f'{vm_data_dir}/{vm_name}.xml', 'w')
    save_template.writelines(install_template)
    save_template.close()
    return f'{vm_data_dir}/{vm_name}.xml'


def setup_bhyve_first_boot_template(vm_name, vm_data_dir):
    template = open('/usr/local/ixautomation/vms/.templates/bhyve_truenas_hdd_boot.xml').read()
    boot_template = re.sub('nas_name', vm_name, template)
    save_template = open(f'{vm_data_dir}/{vm_name}.xml', 'w')
    save_template.writelines(boot_template)
    save_template.close()
    return f'{vm_data_dir}/{vm_name}.xml'


def bhyve_create_disks(vm_name):
    run(f'truncate -s 20G /data/ixautomation/{vm_name}/disk0.img', shell=True)
    run(f'truncate -s 20G /data/ixautomation/{vm_name}/disk1.img', shell=True)
    run(f'truncate -s 20G /data/ixautomation/{vm_name}/disk2.img', shell=True)
    run(f'truncate -s 20G /data/ixautomation/{vm_name}/disk3.img', shell=True)


def bhyve_install_vm(vm_data_dir, vm_name, xml_template):
    run(f'virsh define {xml_template}', shell=True)
    sleep(1)
    run(f'virsh start {vm_name}', shell=True)
    sleep(1)
    vm_output = f"{vm_data_dir}/console.log"
    expctcmd = f'expect tests/install.exp "{vm_name}" "{vm_output}"'
    process = run(expctcmd, shell=True, close_fds=True)
    # console_file = open(vm_output, 'r')
    if process.returncode == 0:
        print('\nTrueNAS installation successfully completed')
        run(f'virsh destroy {vm_name}', shell=True)
        sleep(1)
        return True
    else:
        print('\nTrueNAS installation failed')
        return False


def bhyve_boot_vm(vm_data_dir, vm_name, xml_template, version):
    run(f'virsh undefine {vm_name}', shell=True)
    sleep(1)
    run(f'virsh define {xml_template}', shell=True)
    sleep(1)
    run(f'virsh start {vm_name}', shell=True)
    sleep(1)
    # change workspace to test directory
    # COM_LISTEN = `cat ${vm_dir}/${vm}/console | cut -d/ -f3`
    vm_output = f"{vm_data_dir}/console.log"
    expectcnd = f'expect tests/boot.exp "{vm_name}" "{vm_output}"'
    run(expectcnd, shell=True)
    console_file = open(vm_output, 'r').read()
    # Reset/clear to get native term dimensions
    try:
        url = re.search(r'http://[0-9]+.[0-9]+.[0-9]+.[0-9]+', console_file)
        vmip = url.group().strip().partition('//')[2]
    except AttributeError:
        exit_vm_fail('Failed to get an IP!', vm_name)
    # try:
    #     vmnic = re.search(r'(em|vtnet|enp0s)[0-9]+', console_file).group()
    # except AttributeError:
    #     exit_vm_fail('Failed to get a network interface!', vm_name)
    print(f"\n\nTrueNAS_IP={vmip}")
    print(f"TrueNAS_VM_NAME={vm_name}")
    print(f"TrueNAS_VERSION={version}")
    # print(f"TrueNAS_NIC={vmnic}")
    nas_config = "[NAS_CONFIG]\n"
    nas_config += f"ip = {vmip}\n"
    nas_config += "password = testing\n"
    nas_config += f"version = {version}\n"
    # nas_config += f"nic = {vmnic}\n"
    if os.path.exists('tests/bdd'):
        file = open('tests/bdd/config.cfg', 'w')
    else:
        file = open('tests/config.cfg', 'w')
    file.writelines(nas_config)
    file.close()
    # return {'ip': vmip, 'nic': vmnic}


def setup_kvm_template(vm_name, vm_data_dir, profile):
    template = open(f'/usr/local/ixautomation/vms/.templates/{profile}.xml').read()
    boot_template = re.sub('nas_name', vm_name, template)
    save_template = open(f'{vm_data_dir}/{vm_name}.xml', 'w')
    save_template.writelines(boot_template)
    save_template.close()
    return f'{vm_data_dir}/{vm_name}.xml'


def kvm_create_disks(vm_name, profile):
    run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk0.qcow2 16G', shell=True)
    run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk1.qcow2 20G', shell=True)
    run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk2.qcow2 20G', shell=True)
    run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk3.qcow2 20G', shell=True)
    if profile == 'kvm_scale':
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk4.qcow2 20G', shell=True)
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk5.qcow2 20G', shell=True)
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk6.qcow2 20G', shell=True)
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk7.qcow2 20G', shell=True)
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk8.qcow2 20G', shell=True)
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk9.qcow2 20G', shell=True)
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk10.qcow2 20G', shell=True)
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk11.qcow2 20G', shell=True)
        run(f'qemu-img create -f qcow2 /data/ixautomation/{vm_name}/disk12.qcow2 20G', shell=True)


def kvm_install_vm(vm_data_dir, vm_name, xml_template, iso_path, profile):
    cdrom = 'sdn' if profile == 'kvm_scale' else 'sde'
    print(cdrom)
    print(profile)
    run(f'virsh define {xml_template}', shell=True)
    sleep(1)
    run(f'virsh change-media {vm_name} {cdrom} {iso_path}', shell=True)
    sleep(1)
    run(f'virsh start {vm_name}', shell=True)
    sleep(1)
    vm_output = f"{vm_data_dir}/console.log"
    expctcmd = f'expect tests/install.exp "{vm_name}" "{vm_output}"'
    process = run(expctcmd, shell=True, close_fds=True)
    # console_file = open(vm_output, 'r')
    if process.returncode == 0:
        print('\nTrueNAS installation successfully completed')
        run(f'virsh destroy {vm_name}', shell=True)
        sleep(1)
        run(f'virsh change-media {vm_name} {cdrom} --eject', shell=True)
        sleep(1)
        return True
    else:
        print('\nTrueNAS installation failed')
        run(f'virsh destroy {vm_name}', shell=True)
        sleep(1)
        run(f'virsh change-media {vm_name} {cdrom} --eject', shell=True)
        sleep(1)
        return False


def kvm_boot_vm(vm_data_dir, vm_name, xml_template, version):
    run(f'virsh start {vm_name}', shell=True)
    sleep(1)
    # change workspace to test directory
    # COM_LISTEN = `cat ${vm_dir}/${vm}/console | cut -d/ -f3`
    vm_output = f"{vm_data_dir}/console.log"
    expectcnd = f'expect tests/boot.exp "{vm_name}" "{vm_output}"'
    run(expectcnd, shell=True)
    console_file = open(vm_output, 'r').read()
    # Reset/clear to get native term dimensions
    try:
        url = re.search(r'http://[0-9]+.[0-9]+.[0-9]+.[0-9]+', console_file)
        vmip = url.group().strip().partition('//')[2]
    except AttributeError:
        exit_vm_fail('Failed to get an IP!', vm_name)
    # try:
    #     vmnic = re.search(r'(vtnet|enp0s|enp1s)[0-9]+', console_file).group()
    # except AttributeError:
    #     exit_vm_fail('Failed to get a network interface!', vm_name)
    print(f"\n\nTrueNAS_IP={vmip}")
    print(f"TrueNAS_VM_NAME={vm_name}")
    print(f"TrueNAS_VERSION={version}")
    # print(f"TrueNAS_NIC={vmnic}")
    nas_config = "[NAS_CONFIG]\n"
    nas_config += f"ip = {vmip}\n"
    nas_config += "password = testing\n"
    nas_config += f"version = {version}\n"
    # nas_config += f"nic = {vmnic}\n"
    if os.path.exists('tests/bdd'):
        file = open('tests/bdd/config.cfg', 'w')
    else:
        file = open('tests/config.cfg', 'w')
    file.writelines(nas_config)
    file.close()
    # return {'ip': vmip, 'nic': vmnic}


def exit_vm_fail(msg, vm_name):
    print(f'## {msg} Clean up time!')
    remove_vm(vm_name)
    sys.exit(1)


def remove_vm(vm_name):
    run(f'virsh destroy {vm_name}', shell=True)
    sleep(1)
    run(f'virsh undefine {vm_name}', shell=True)
    sleep(1)
    run(f'virsh undefine --nvram {vm_name}', shell=True)
    sleep(1)
    vm_dir = f"/data/ixautomation/{vm_name}"
    run(f"rm -rf {vm_dir}", shell=True)


def remove_all_vm():
    cmd = "virsh list --all"
    vm_list = Popen(cmd, shell=True, stdout=PIPE, universal_newlines=True)
    new_vmlist = vm_list.stdout.read()
    for line in new_vmlist.splitlines():
        if 'shut off' in line or 'running' in line:
            vm_info = line.strip().split()
            vm_name = vm_info[1]
            print(f'Removing {vm_name} VM files')
            run(f'virsh destroy {vm_name}', shell=True)
            sleep(1)
            run(f'virsh undefine {vm_name}', shell=True)
            sleep(1)
            run(f'virsh undefine --nvram {vm_name}', shell=True)
    for vm_name in os.listdir('/data/ixautomation'):
        vm_dir = f"/data/ixautomation/{vm_name}"
        run(f"rm -rf {vm_dir}", shell=True)


def remove_stopped_vm():
    cmd = "virsh list --inactive"
    vm_list = Popen(cmd, shell=True, stdout=PIPE, universal_newlines=True)
    new_vmlist = vm_list.stdout.read()
    for line in new_vmlist.splitlines():
        if 'shut off' in line:
            vm_info = line.strip().split()
            vm_name = vm_info[1]
            print(f'Removing {vm_name} VM files')
            run(f'virsh undefine {vm_name}', shell=True)
            sleep(1)
            run(f'virsh undefine --nvram {vm_name}', shell=True)
            vm_dir = f"/data/ixautomation/{vm_name}"
            run(f"rm -rf {vm_dir}", shell=True)
