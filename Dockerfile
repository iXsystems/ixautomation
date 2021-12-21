FROM debian:bullseye
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update
RUN apt-get -y install git npm python3 python3-pip samba smbclient sshpass
RUN python3 -m pip install pytest pytest-dependency pytest-timeout requests websocket-client
RUN git clone https://github.com/iXsystems/ixautomation.git --depth=1
RUN cd ixautomation/ && cp -R src/* /usr/local/
RUN ln -s /usr/local/bin/pytest /usr/local/bin/pytest-3
