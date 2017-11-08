#!/usr/bin/env python

# Author: Eric Turgeon
# License: BSD
# Location for tests  of FreeNAS new GUI
#Test case count: 1

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


class logout_test(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        #driver.implicitly_wait(30)
        pass

    #Test navigation Account>Users>Hover>New User and enter username,fullname,password,confirmation and wait till user is  visibile in the list
    def test_01_logout(self):
        #Click on root account
        driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/topbar/md-toolbar/div/md-toolbar-row/button[6]").click()
        #Click on logout
        time.sleep(2)
        driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div/button[3]").click()
        #driver.find_element_by_xpath("//*[@id='cdk-overlay-12']/div/div/button[3]").click()
        time.sleep(2)
        #Click on OK when re-confirm logout
        driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[2]/md-dialog-container/confirm-dialog/div[2]/button[1]").click()
        time.sleep(2)
        #self.assertTrue(self.is_element_present(By.XPATH, "//input[@id='md-input-1']"),
                        #"Logout failed")

    # Next step-- To check if the new user is present in the list via automation


    #method to test if an element is present
    def is_element_present(self, how, what):
        """
        Helper met:hod to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        """
        try: driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True

    @classmethod
    def tearDownClass(inst):
        driver.close()

def run_logout_test(webdriver):
    global driver
    driver = webdriver
    suite = unittest.TestLoader().loadTestsFromTestCase(logout_test)
    xmlrunner.XMLTestRunner(output=results_xml, verbosity=2).run(suite)
