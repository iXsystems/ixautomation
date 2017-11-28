# Author: Rishabh Chauhan
# License: BSD
# Location for tests  of FreeNAS new GUI
#Test case count: 2

from source import *
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
import unittest
import xmlrunner
import random
try:
    import unittest2 as unittest
except ImportError:
    import unittest

xpaths = { 'navService' : "//*[@id='nav-8']/div/a[1]",
           'turnoffConfirm' : "/html/body/div[3]/div[2]/div[2]/md-dialog-container/app-confirm/div[2]/button[1]"
        }

class configure_afp_test(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        driver.implicitly_wait(30)
        pass

    #Test navigation Account>Users>Hover>New User and enter username,fullname,password,confirmation and wait till user is  visibile in the list
    def test_01_turnon_afp (self):
        print (" turning on the afp service")
        time.sleep(5)
        #Click Service Menu
        driver.find_element_by_xpath(xpaths['navService']).click()
        #scroll down
        driver.find_element_by_tag_name('html').send_keys(Keys.END)
        time.sleep(2)
        #Click on the afp toggle button
        driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[1]/md-card/md-toolbar/div/md-toolbar-row/md-slide-toggle/label/div").click()
        time.sleep(1)
        #re-confirming if the turning off the service
        if self.is_element_present(By.XPATH,xpaths['turnoffConfirm']):
            driver.find_element_by_xpath(xpaths['turnoffConfirm']).click()
        time.sleep(10)

#    def test_02_configure_afp(self):
#        time.sleep(1)
        #click on configure button
#        driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[1]/md-card/md-card-actions/button").click()
        #Click on the Guest access dropdownlist
#        driver.find_element_by_xpath("//*[@id='0']/form-select/div/md-select/div").click()
#        time.sleep(1)
        #Select userNAS for Guest Access (temporary)
#        driver.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/md-option[3]").click()
        #click on Guest Account checkbox
#        driver.find_element_by_xpath("//*[@id='1']/form-checkbox/div/md-checkbox/label/div").click()
        #click on save button
#        driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/afp-edit/entity-form/md-card/div/form/md-card-actions/button[1]").click()
#        time.sleep(5)
        # Next step-- To check if the new user is present in the list via automation

    #method to test if an element is present
    def is_element_present(self, how, what):
        """
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        """
        try: driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True

    @classmethod
    def tearDownClass(inst):
        pass

def run_configure_afp_test(webdriver):
    global driver
    driver = webdriver
    suite = unittest.TestLoader().loadTestsFromTestCase(configure_afp_test)
    xmlrunner.XMLTestRunner(output=results_xml, verbosity=2).run(suite)