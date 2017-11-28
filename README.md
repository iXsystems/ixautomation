Jenkins automation testing framework for iX projects
===========

The scripts in this repo will allow you to test iX projects, either as an automated job from Jenkins or manually.

It includes support to test the following projects:

 * FreeNAS
 * TrueOS
 * iocage

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

Jenkins Requirements:
* One master node
* Slave nodes for running ixautomation

Required Jenkins Plugins:

* [Log parser](https://wiki.jenkins.io/display/JENKINS/Log+Parser+Plugin)
* [Workspace Whitespace Replacement](https://wiki.jenkins.io/display/JENKINS/Workspace+Whitespace+Replacement+Plugin)
* [Copy Artifact](https://wiki.jenkins.io/display/JENKINS/Copy+Artifact+Plugin)
* [Xvfb Plugin](https://wiki.jenkins.io/display/JENKINS/Xvfb+Plugin)


Getting Started
============

To prep a new system for testing, first download the repo:

```
git clone --depth=1 https://github.com/iXsystems/ixautomation.git
```

Enter the directory for running ixautomation from git:

```
cd ixautomation/src/
```


VM Tests
============

To install iXautomation dependencies run:

```
sudo ./src/bin/ixautomation bootstrap
```

Make sure vm-bhyve is enabled, and we set the vm location for ixautomation

```
sysrc -f /etc/rc.conf vm_enable="YES"
sysrc -f vm_dir="/usr/local/ixautomation/vms"
```

Specify a connected ethernet interface with access to DHCP for VMs ( Substitue re0 with your interface )

```
sysrc -f /etc/rc.conf ixautomation_iface="re0"
```

# Edit ixautomation.cfg and set location of git repo with tests when running local

```
cp src/etc/ixautomation.cfg.dist src/etc/ixautomation.cfg
edit src/etc/ixautomation.cfg
```

Enter the directory for running ixautomation

```
cd bin
```

Create a VM, and test install using vm-bhyve

```
sudo ./ixautomation vm-tests freenas
sudo ./ixautomation vm-tests trueos
```

Stop, and destroy all VMs

```
sudo ./ixautomation vm-destroy-all
```


ReST API Tests
============

*This requires following the steps above in VM tests.*

Create a VM, test install using vm-bhyve, and run API tests:
```
sudo ./ixautomation vm-tests freenas api-tests
```


Selenium Tests
============
To install iXautomation dependencies run:

```
sudo ./ixautomation bootstrap-webui
```

Test webui with selenium
```
sudo ./ixautomation freenas-webui-tests
```


iocage Tests
============
```
sudo ./ixautomation iocage-tests
```
