Jenkins automation framework for iX and related projects
===========

The scripts in this repo will allow you to test iX projects, either as an automated job from Jenkins or manually.

It includes support to test the following projects:

 * FreeNAS
 * iocage
 * TrueOS

Requirements
============

Recommended hardware:
* CPU: 1 Cores or more
* Memory: 4GB
* Disk: 20GB (For FreeNAS)
* Wired ethernet connection for bhyve bridge
* At least 1 ZFS pool named tank

Required OS:

* [TrueOS](http://download.trueos.org/master/amd64/)

Required Packages:
* expect
* bhyve-firmware
* git
* curl
* bash
* spidermonkey24
* wget
* rsync

Jenkins Requirements:
* One master node
* Slave nodes for running ixautomation

Required Jenkins Plugins:

* [Log parser](https://wiki.jenkins.io/display/JENKINS/Log+Parser+Plugin)
* [Workspace Whitespace Replacement](https://wiki.jenkins.io/display/JENKINS/Workspace+Whitespace+Replacement+Plugin)
* [Copy Artifact](https://wiki.jenkins.io/display/JENKINS/Copy+Artifact+Plugin)


Getting Started
============

To prep a new system for testing, first download the repo and install with
the following:

```
git clone --depth=1 https://github.com/iXsystems/ixautomation.git
cd ixautomation
```


VM Tests
============

To install iXautomation dependencies run:

```
sudo ./jenkins.sh bootstrap
```

Specify a connected ethernet interface with access to DHCP for VMs ( Substitue re0 with your interface )

```
sysrc -f /etc/rc.conf ixautomation_iface="re0"
```

Create a VM, and test install using vm-bhyve

```
sudo ./jenkins.sh vm-tests freenas
sudo ./jenkins.sh vm-tests trueos
```

Stop, and destroy all VMs

```
sudo ./jenkins.sh vm-destroy-all
```


ReST API Tests
============

*Note: This Requires following the steps above in VM tests.*

Create a VM, test install using vm-bhyve, and run API tests
```
/jenkins.sh vm-tests freenas api-tests
```


Selenium Tests
============
To install iXautomation dependencies run:

```
sudo ./jenkins.sh bootstrap-webui
```

Test webui with selenium
```
sudo ./jenkins.sh freenas-webui-tests
```


iocage Tests
============
```
sudo ./jenkins.sh iocage-tests
```
