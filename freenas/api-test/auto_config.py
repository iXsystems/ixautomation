#!/usr/bin/env python3.6

import os

user = "root"
password = "testing"
ip = "192.168.2.26"
freenas_url = 'http://' + ip + '/api/v1.0'
interface = "vtnet0"
ntpServer = "10.20.20.122"
localHome = "/usr/home/eturgeon"
disk1 = "vtbd1"
disk2 = "vtbd2"
keyPath = "/usr/home/eturgeon/.ssh/test_id_rsa"
sshKey = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/iwwlteco3AcNJzcx6OJdKuNUAp7ljFDKs3Gtu+vOtpTye4TMQCGUpTeEEGqCqnzztS6dxmUE6rKYZeI8cLdb4M2XdoX1kVDtRH0WB5wv0fso7sR68WWjHGqGaS3xwohxvyH8bJ9WX1lEXNboU8qN4YQScRsk9mJWLYrDWuLo/S0ixoLcisyXuUwbxENilgFL8ey3khZUqwKWtOIOo+RyyWlJfa2iyndv+i118EevG80FtkmxflQKClD7S62HJDKXI/s5Sm/Ngp9hEBIdZo3dHWiNhD97timNFgWaO5WVa9sg6+A0du7DEXQpNlx58xaaJ/tP5tLgX9Oy4gY0onzd eturgeon@eric-laptop.tn.ixsystems.com"
