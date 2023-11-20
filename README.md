Tool to automate TrueNAS VM creation for Jenkins for API, UI testing
===========

iXautomation allow you to start TrueNAS VMs with Bhyve on FreeBSD and KVM on Debian it can be use to spin VM either as an automated job from Jenkins or manually for for API test and UI test.

### Requirements

**Recommended hardware:**

* CPU: 4 Cores or more
* Memory: 16GB
* Disk: 200GB
* Wired Ethernet connection

**Required OS:**

* FreeBSD base
* Debian base

**Jenkins Requirements:**
* One master node
* Slave nodes for running ixautomation

**Required Jenkins Plugging:**

* [Log parser](https://wiki.jenkins.io/display/JENKINS/Log+Parser+Plugin)
* [Workspace Whitespace Replacement](https://wiki.jenkins.io/display/JENKINS/Workspace+Whitespace+Replacement+Plugin)
* [Copy Artifact](https://wiki.jenkins.io/display/JENKINS/Copy+Artifact+Plugin)
* [Xvfb Plugin](https://wiki.jenkins.io/display/JENKINS/Xvfb+Plugin)
* [Workspace Cleanup](https://wiki.jenkins.io/display/JENKINS/Workspace+Cleanup+Plugin)


### Install and setup iXautomation on FreeBSD or Debian.

**From GitHub:**

```
git clone --depth 1 --branch libvirt https://github.com/ixsystems/ixautomation.git
cd ixautomation/
sudo python3 setup_workstation.py
cd src
sudo python3 setup.py install
```

Put the iso to run with the VM in **middleware/tests/iso/** or **webui/tests/iso/**

#### Start VM and clean
Create a VM, and test the installation using vm-bhyve.

```
cd middleware
```
or
```
cd webui
sudo ixautomation --run vm-tests
```

Starting ixautomation with WORKSPACE and custom name
```
WORKSPACE=/path/to/middleware ixautomation --vm-name scale-vm
```

To stop, and clean up all running vms.
```
sudo ixautomation --destroy-all-vm
```

To shutdown, and clean up a VM.
```
sudo ixautomation --destroy-vm the-vm-name
```

To stop and and clean olly the stopped vms
```
sudo ixautomation --destroy-stopped-vm
```

iXautomaion will output the vm ip, name, ISO version and network interface like below
```
TrueNAS_IP=192.186.0.58
TrueNAS_VM_NAME=scale-vm
TrueNAS_VERSION=TrueNAS-SCALE-22.12-MASTER-20220921-015225
TrueNAS_NIC=enp1s0
```

It also create tests/config.cfg that webui test and pipeline uses ti looks like bellow.

```
[NAS_CONFIG]
ip = 192.186.0.58
password = testing
version = TrueNAS-SCALE-22.12-MASTER-20220921-015225
nic = enp1s0
```