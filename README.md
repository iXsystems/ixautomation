Jenkins automation testing framework for iX projects
===========

The scripts in this repo will allow you to test iX projects, either as an automated job from Jenkins or manually.

It includes support to test the following projects:

 * FreeNAS
 * TrueOS

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


Getting Started using package method
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

Getting started using port method
============

Clone the latest ports tree from TrueOS:

```
sudo git clone --depth=1 https://www.github.com/trueos/freebsd-ports /usr/ports/
```

To prep a new system for testing, first download the repo:

```
git clone --depth=1 https://github.com/iXsystems/ixautomation.git
```

Enter the directory for installing ixautomation from git:

```
cd ixautomation/
```

Generate the port from the latest git commit
```
sudo ./mkport.sh /usr/ports/ /usr/ports/distfiles/
```

Install the port
```
cd /usr/ports/sysutils/py36-ixautomation
```

Generate the port from the latest git commit
```
sudo make install clean
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

Getting started using git
============

To prep a new system for testing, first download the repo:

```
git clone --depth=1 https://github.com/iXsystems/ixautomation.git
```

Enter the directory for installing ixautomation from git:

```
cd ixautomation/src/
```

Install the framework
```
sudo python3.6 setup.py install
```

Make sure vm-bhyve is enabled, and we set the vm location for ixautomation

```
sysrc -f /etc/rc.conf vm_enable="YES"
sysrc -f /etc/rc.conf vm_dir="/usr/local/ixautomation/vms"
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

Copy ixautomation conf.dist to ixautomation.conf 

```
cp /usr/local/etc/ixautomation.conf.dist /usr/local/etc/conf.ixautomation.cfg
```

Edit ixautomation.cfg

```
edit /usr/local/etc/ixautomation.cfg
```

Set location of git repo with tests when running local

```
# When running outside of jenkins set WORKSPACE to the path of the local git repo containing tests
WORKSPACE="/home/jmaloney/projects/ixsystems/ixautomation"
export WORKSPACE
```

VM Tests
============

Create a VM, and test install using vm-bhyve

```
sudo ixautomation --run vm-tests --systype freenas
sudo ixautomation --run vm-tests --systype trueos
```

API Tests (To run VM tests as well remove --ip)
============
```
sudo ixautomation --run api-tests --systype freenas --ip 192.168.0.2
```

Middlewared Tests (To run VM tests as well remove --ip)
============
```
sudo ixautomation --run middleware-tests --systype freenas --ip 192.168.0.2
```

Selenium Tests (To run VM tests as well remove --ip)
============

Test webui with selenium
```
sudo ixautomation --run webui-test --systype freenas --ip 192.168.0.2
```
