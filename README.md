Jenkins automation testing framework for iX projects
===========

The scripts in this repo will allow you to test iX projects, either as an automated job from Jenkins or manually.

It includes support to test the following projects:

 * FreeNAS
 * TrueOS Server

Requirements
============

Recommended hardware:
* CPU: 1 Cores or more
* Memory: 16GB
* Disk: 100GB
* Wired ethernet connection for vm-bhyve bridge

Required OS:

* [TrueOS Unstable](http://download.trueos.org/unstable/amd64/)

Required Packages:

* See Run Depends in port Makefile

Jenkins Requirements:
* One master node
* Slave nodes for running ixautomation

Required Jenkins Plugins:

* [Log parser](https://wiki.jenkins.io/display/JENKINS/Log+Parser+Plugin)
* [Workspace Whitespace Replacement](https://wiki.jenkins.io/display/JENKINS/Workspace+Whitespace+Replacement+Plugin)
* [Copy Artifact](https://wiki.jenkins.io/display/JENKINS/Copy+Artifact+Plugin)
* [Xvfb Plugin](https://wiki.jenkins.io/display/JENKINS/Xvfb+Plugin)
* [Workspace Cleanup](https://wiki.jenkins.io/display/JENKINS/Workspace+Cleanup+Plugin)


Install the framework using package method
============

```
sudo pkg install py36-ixautomation
```

Specify a connected ethernet interface with access to DHCP for VMs ( Substitue re0 with your interface )

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

Set location of git repo with tests when running local

```
## When running outside of jenkins set WORKSPACE to the path of the local git repo containing tests
FreeNAS = "/home/eturgeon/projects/ixsystems/freenas"
TrueOS = "/home/eturgeon/projects/trueos/trueos-server"
WebUI = "/home/eturgeon/projects/ixsystems/webui"
```


VM Tests
============
Create a VM, and test install using vm-bhyve

```
sudo ixautomation --run vm-tests --systype freenas
sudo ixautomation --run vm-tests --systype trueos
```

Shutdown, and cleanup all running vms
```
sudo ixautomation --destroy-all-vm
```

API Tests
============
In order to run VM tests remove --ip
```
sudo ixautomation --run api-tests --systype freenas --ip 192.168.0.2
```

Middlewared Tests
============
In order to run VM tests remove --ip
```
sudo ixautomation --run middleware-tests --systype freenas --ip 192.168.0.2
```

Selenium Tests
============
In order to run VM tests remove --ip
```
sudo ixautomation --run webui-test --systype freenas --ip 192.168.0.2
```
