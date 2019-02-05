Jenkins automation testing framework for iX projects
===========

The scripts in this repository will allow you to start Bhyve vm and run tests for some iX projects, either as an automated job from Jenkins or manually.

It includes support to test the following projects:

 * FreeNAS
 * TrueOS Server

Requirements
============

Recommended hardware:
* CPU: 4 Cores or more
* Memory: 16GB
* Disk: 100GB
* Wired Ethernet connection for vm-bhyve bridge

Required OS:

* [TrueOS Unstable](https://pkg.trueos.org/iso/unstable)
* [Project Trident](https://project-trident.org/download/)
* [GhostBSD](http://www.ghostbsd.org/download)

Jenkins Requirements:
* One master node
* Slave nodes for running ixautomation

Required Jenkins Plugging:

* [Log parser](https://wiki.jenkins.io/display/JENKINS/Log+Parser+Plugin)
* [Workspace Whitespace Replacement](https://wiki.jenkins.io/display/JENKINS/Workspace+Whitespace+Replacement+Plugin)
* [Copy Artifact](https://wiki.jenkins.io/display/JENKINS/Copy+Artifact+Plugin)
* [Xvfb Plugin](https://wiki.jenkins.io/display/JENKINS/Xvfb+Plugin)
* [Workspace Cleanup](https://wiki.jenkins.io/display/JENKINS/Workspace+Cleanup+Plugin)


Install the framework on TrueOS, Project Trident and GhostBSD
============

From package:

```
sudo pkg install py36-ixautomation
```

Specify a connected Ethernet interface with access to DHCP for VMs ( Substitute re0 with your interface )

```
sysrc -f /etc/rc.conf ixautomation_iface="re0"
```

Add the ixautomation service

```
rc-update add ixautomation
```

Start the ixautomation service

```
service ixautomation start
```

To use manualy
============

Set location of the git repository with the tests in /user/local/etc/ixautomation.conf

```
## When running outside of Jenkins set WORKSPACE to the path of the local git repository containing tests
FreeNAS = "/home/eturgeon/projects/ixsystems/freenas"
TrueOS = "/home/eturgeon/projects/trueos/trueos-server"
WebUI = "/home/eturgeon/projects/ixsystems/webui"
```
Put the iso to run with the VM in freenas/tests/iso/

VM Tests
============
Create a VM, and test install using vm-bhyve

```
sudo ixautomation --run vm-tests --systype freenas
sudo ixautomation --run vm-tests --systype trueos
```

To keep the vm runing use --keep-alive option
```
sudo ixautomation --run vm-tests --systype freenas --keep-alive
```

To Shutdown, and cleanup all running vms
```
sudo ixautomation --destroy-all-vm
```

To Shutdown, and cleanup a VM
```
sudo ixautomation --destroy-vm ABCD
```

FreeNAS REST API Tests
============
Run API test with VM tests

API 1.0

```
sudo ixautomation --run api-tests --systype freenas
```

API 2.0

```
sudo ixautomation --run api2-tests --systype freenas
```

Run API test from VM or real machine

```
sudo ixautomation --run api-tests --systype freenas --ip 192.168.0.2
```
For a real machine add the driver card to use.

```
sudo ixautomation --run api-tests --systype freenas --ip 192.168.0.2:re0
```

Selenium Tests
============
In order to run VM tests remove --ip
```
sudo ixautomation --run webui-test --systype freenas --ip 192.168.0.2
```
