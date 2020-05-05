Jenkins automation testing framework for iX projects
===========

The scripts in this repository will allow you to start Bhyve VM and run tests for some FreeNAS and TrueNAS, either as an automated job from Jenkins or manually.

### Requirements

**Recommended hardware:**

* CPU: 4 Cores or more
* Memory: 16GB
* Disk: 100GB
* Wired Ethernet connection for vm-bhyve bridge

**Required OS:**

* [FreeBSD](https://www.freebsd.org/where.html)
* [GhostBSD](https://www.ghostbsd.org/download)

**Jenkins Requirements:**
* One master node
* Slave nodes for running ixautomation

**Required Jenkins Plugging:**

* [Log parser](https://wiki.jenkins.io/display/JENKINS/Log+Parser+Plugin)
* [Workspace Whitespace Replacement](https://wiki.jenkins.io/display/JENKINS/Workspace+Whitespace+Replacement+Plugin)
* [Copy Artifact](https://wiki.jenkins.io/display/JENKINS/Copy+Artifact+Plugin)
* [Xvfb Plugin](https://wiki.jenkins.io/display/JENKINS/Xvfb+Plugin)
* [Workspace Cleanup](https://wiki.jenkins.io/display/JENKINS/Workspace+Cleanup+Plugin)


### Install the framework on FreeBSD and GhostBSD

**From GitHub:**

```
pkg install python3 py37-pytest py37-requests py37-selenium py37-ws4py vm-bhyve expect sshpass bhyve-firmware dnsmasq
git clone --depth 1 https://github.com/ixsystems/ixautomation.git
cd ixautomation/src
sudo python3 setup.py install
```

### Setting iXautomation

Configure vm-bhyve for ixautomation

```
sysrc -f /etc/rc.conf vm_enable="YES"
sysrc -f /etc/rc.conf vm_dir="/usr/local/ixautomation/vms"
```
### To use manually

Set location of the git repository with the tests in **/user/local/etc/ixautomation.conf**

```
## When running outside of Jenkins set WORKSPACE to the path of the local git repository containing tests
FreeNAS = "/home/eturgeon/projects/ixsystems/freenas"
WebUI = "/home/eturgeon/projects/ixsystems/webui"
```
Put the iso to run with the VM in **freenas/tests/iso/**

#### Start VM and clean
Create a VM, and test the installation using vm-bhyve.

```
sudo ixautomation --run vm-tests
```

To keep the vm running use --keep-alive option.
```
sudo ixautomation --run vm-tests --keep-alive
```

To shutdown, and clean up all running vms.
```
sudo ixautomation --destroy-all-vm
```

To shutdown, and clean up a VM.
```
sudo ixautomation --destroy-vm ABCD
```

#### FreeNAS REST API tests

Creating a VM and run API 1.0 tests.

```
sudo ixautomation --run api-tests
```

Creating a VM and run API 2.0 tests.

```
sudo ixautomation --run api2-tests
```

Run API test on a Bhyve VM.

```
sudo ixautomation --run api-tests --ip 192.168.0.10
```
For a VM or a real machine add the interface to use.

```
sudo ixautomation --run api-tests --ip 192.168.0.10:re0
```
Run Kyua test on a VM or a real machine

```
sudo ixautomation --run kyua-tests --ip 192.168.0.10
```
