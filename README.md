Jenkins automation framework for iX and related projects
===========

The scripts in this repo will allow you to test iX projects, either as an automated job from Jenkins or manually.

It includes support to test the following projects:

 * FreeBSD
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

* TrueOS STABLE, or UNSTABLE

[TrueOS Download Site](http://download.trueos.org/master/amd64/)

Required Packages:
* expect
* bhyve-firmware
* git
* curl
* bash
* spidermonkey24
* wget
* rsync
* vm-bhyve

Getting Started
============

To prep a new system for building, first download the repo and install with
the following:

```
git clone --depth=1 https://github.com/iXsystems/ixautomation.git
cd ixautomation
```
To install all iXautomation dependencies run:

```
sudo ./jenkins.sh install-dependencies
```

Using the testing framework
============

Create a VM, and test install using vm-bhyve

```
sudo ./jenkins.sh vm-tests freebsd
sudo ./jenkins.sh vm-tests freenas
sudo ./jenkins.sh vm-tests trueos
```

Stop, and destroy all VMs

```
sudo ./jenkins.sh vm-destroy-all
```

FreeNAS
```
sudo ./jenkins.sh freenas-api-tests
sudo ./jenkins.sh freenas-webui-tests
```

iocage
```
sudo ./jenkins.sh iocage-tests
```
