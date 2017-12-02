#/usr/bin/env python
# Author: Eric Turgeon
# License: BSD

from source import *
from login import run_login_test
from guide import run_guide_test
from group import run_create_group_test
from user import run_create_user_test
from ssh import run_configure_ssh_test
from logout import run_logout_test
from update import run_check_update_test
from os import path
from selenium import webdriver
#from example import run_creat_nameofthetest

def webDriver():
#marionette setting is fixed in selenium 3.0 and above by default
#    caps = webdriver.DesiredCapabilities().FIREFOX
#    caps["marionette"] = False
    global driver
    driver = webdriver.Firefox() #(capabilities=caps)
    driver.implicitly_wait(30)
    driver.maximize_window()
    return driver

