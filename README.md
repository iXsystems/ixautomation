Jenkins automation testing framework for iX projects
===========

The scripts in this repository will allow you to start Bhyve VM and run tests for some iX projects, either as an automated job from Jenkins or manually.

**It includes support to test the following projects:**

 * FreeNAS
 * TrueOS
 * TrueView

### Requirements

**Recommended hardware:**
* CPU: 4 Cores or more
* Memory: 16GB
* Disk: 100GB
* Wired Ethernet connection for vm-bhyve bridge

**Required OS:**

* [TrueOS Unstable](https://pkg.trueos.org/iso/unstable)
* [Project Trident](https://project-trident.org/download/)
* [GhostBSD](http://www.ghostbsd.org/download)

**Jenkins Requirements:**
* One master node
* Slave nodes for running ixautomation

**Required Jenkins Plugging:**

* [Log parser](https://wiki.jenkins.io/display/JENKINS/Log+Parser+Plugin)
* [Workspace Whitespace Replacement](https://wiki.jenkins.io/display/JENKINS/Workspace+Whitespace+Replacement+Plugin)
* [Copy Artifact](https://wiki.jenkins.io/display/JENKINS/Copy+Artifact+Plugin)
* [Xvfb Plugin](https://wiki.jenkins.io/display/JENKINS/Xvfb+Plugin)
* [Workspace Cleanup](https://wiki.jenkins.io/display/JENKINS/Workspace+Cleanup+Plugin)


### Install the framework on TrueOS, Project Trident and GhostBSD

**From package:**

```
sudo pkg install py36-ixautomation
```

**From ports:**

```
sudo git clone --depth 1 https://github.com/trueos/trueos-ports.git /usr/ports
cd /usr/ports/sysutils/py-ixautomation
sudo make install clean
```

**From GitHub:**

```
pkg install py36-pytest py36-requests py36-selenium py36-websocket-client py36-unittest-xml-reporting ix-bhyve expect sshpass bhyve-firmware dnsmasq
git clone --depth 1 https://github.com/ixsystems/ixautomation.git
cd ixautomation/src
sudo python3.6 setup.py install
```
**Note:** ix-bhyve is a clone of vm-bhyve ixautomation should also work with vm-bhyve

### Setting iXautomation

Specify a connected Ethernet interface with access to DHCP for VMs ( Substitute `re0` with your interface )

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

### To use manually

Set location of the git repository with the tests in **/user/local/etc/ixautomation.conf**

```
## When running outside of Jenkins set WORKSPACE to the path of the local git repository containing tests
FreeNAS = "/home/eturgeon/projects/ixsystems/freenas"
TrueOS = "/home/eturgeon/projects/trueos/trueos-server"
WebUI = "/home/eturgeon/projects/ixsystems/webui"
TrueView = "/home/eturgeon/projects/ixsystems/TrueView-qt-spog"
```
Put the iso to run with the VM in **freenas/tests/iso/**

#### Start VM and clean
Create a VM, and test install using vm-bhyve

```
sudo ixautomation --run vm-tests --systype freenas
sudo ixautomation --run vm-tests --systype trueos
sudo ixautomation --run vm-tests --systype trueview
```

To keep the vm runing use --keep-alive option
```
sudo ixautomation --run vm-tests --systype freenas --keep-alive
```

To shutdown, and cleanup all running vms
```
sudo ixautomation --destroy-all-vm
```

To shutdown, and cleanup a VM
```
sudo ixautomation --destroy-vm ABCD
```

#### FreeNAS REST API tests

Run API 1.0 tests with VM tests

```
sudo ixautomation --run api-tests --systype freenas
```

Run API 2.0 tests with VM tests

```
sudo ixautomation --run api2-tests --systype freenas
```

Run API test on a VM or a real machine

```
sudo ixautomation --run api-tests --systype freenas --ip 192.168.0.2
```
For a real machine add the driver card to use.

```
sudo ixautomation --run api-tests --systype freenas --ip 192.168.0.2:re0
```

#### TrueView API Tests

Run REST API tests with VM tests

```
sudo ixautomation --run api-tests --systype trueview --server-ip 192.168.0.214
```

Run WebSocket API tests with VM tests

```
sudo ixautomation --run websocket-tests --systype freenas --server-ip 192.168.0.214
```


#### Selenium Tests

In order to run VM tests remove --ip
```
sudo ixautomation --run webui-test --systype freenas --ip 192.168.0.2
```
