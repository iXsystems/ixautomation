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

A system running TrueOS, with at minimum 16GB of memory.
(Building TrueOS packages in a reasonable time works best with 48GB or more)

Recommended hardware:
* CPU: 8 Cores or more
* Memory: 16GB (For FreeNAS) 48GB (For TrueOS)
* Disk: 20GB (For FreeNAS) 200GB (For TrueOS)
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
To isntall all iXautomation dependencies run:

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
