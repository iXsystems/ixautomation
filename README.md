Jenkins automation framework for iX projects
===========

The scripts in this repo will allow you to test iX projects, either as an automated job from Jenkins or manually.

It includes support to test the following projects:

 * FreeNAS
 * iocage
 * TrueOS
 * TrueView
 * SysAdm

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
* sshpass

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
sudo ./jenkins install-dependencies
```

Using the testing framework
============

FreeNAS
```
sudo ./jenkins.sh freenas-tests
sudo ./jenkins.sh freenas-webui-tests
```

iocage
```
sudo ./jenkins.sh iocage-tests
```

TrueOS
```
sudo ./jenkins.sh trueos-tests
```

TrueView
```
sudo ./jenkins.sh trueview-webui-tests
```

SysAdm
```
sudo ./jenkins.sh sysadm-cli-tests
```
