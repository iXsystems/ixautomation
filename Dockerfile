FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update
RUN apt-get -y install build-essential debootstrap libjson-perl firefox-geckodriver git npm python3 python3-pip python3-venv samba smbclient sshpass squashfs-tools unzip snmp
RUN git clone https://github.com/iXsystems/ixautomation.git --depth=1
RUN cd ixautomation/src && python3 setup.py install
RUN git clone https://github.com/truenas/middleware.git
RUN cd middleware/src/middlewared/ && python3 ./setup_client.py install && python3 ./setup_test.py install
RUN ln -s /usr/local/bin/pytest /usr/local/bin/pytest-3
RUN cp /usr/local/etc/ixautomation.conf.dist /usr/local/etc/ixautomation.conf
RUN git clone https://github.com/lukejpreston/xunit-viewer --depth=1
RUN cd xunit-viewer/ && npm i -g xunit-viewer
