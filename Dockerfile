FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get -y install --no-install-recommends build-essential debootstrap libjson-perl firefox-geckodriver git npm python3 python3-pip python3-venv samba smbclient sshpass squashfs-tools unzip snmp \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && git clone https://github.com/iXsystems/ixautomation.git --depth=1 \
 && cd ixautomation/src && python3 setup.py install \
 && git clone https://github.com/truenas/middleware.git \
 && cd middleware/src/middlewared/ && python3 ./setup_client.py install && python3 ./setup_test.py install \
 && ln -s /usr/local/bin/pytest /usr/local/bin/pytest-3 \
 && git clone https://github.com/lukejpreston/xunit-viewer --depth=1 \
 && cd xunit-viewer/ && npm i -g xunit-viewer

COPY src/etc/ixautomation.conf.dist /usr/local/etc/ixautomation.conf
