# Author: Rishabh Chauhan
# License: BSD
# Location for tests  of FreeNAS new GUI
#Test case count: 7

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

xpaths = { 'themeBar' : "//*[@id='schemeToggle']/span/md-icon",
          'theme1' : "/html/body/div[3]/div[2]/div/div/md-grid-list/div/md-grid-tile[1]/figure/div/div[2]",
          'theme2' : "/html/body/div[3]/div[2]/div/div/md-grid-list/div/md-grid-tile[2]/figure/div/div[2]",
          'theme3' : "/html/body/div[3]/div[2]/div/div/md-grid-list/div/md-grid-tile[3]/figure/div/div[2]",
          'theme4' : "/html/body/div[3]/div[2]/div/div/md-grid-list/div/md-grid-tile[4]/figure/div/div[2]",
          'theme5' : "/html/body/div[3]/div[2]/div/div/md-grid-list/div/md-grid-tile[5]/figure/div/div[2]",
          'theme6' : "/html/body/div[3]/div[2]/div/div/md-grid-list/div/md-grid-tile[6]/figure/div/div[2]",
          'theme7' : "/html/body/div[3]/div[2]/div/div/md-grid-list/div/md-grid-tile[7]/figure/div/div[2]" 
          }


class change_theme_test(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        driver.implicitly_wait(30)
        pass

    #Test navigation Account>Users>Hover>New User and enter username,fullname,password,confirmation and wait till user is  visibile in the list
    def test_01_theme1(self):
        self.theme_change("1")

        #Click on the theme Button
#        driver.find_element_by_xpath(xpaths['themeBar']).click()
        #Select 1st theme
#        driver.find_element_by_xpath(xpaths['theme1']).click()
#        time.sleep(3)

    def test_02_theme2(self):
        #Click on the theme Button
        driver.find_element_by_xpath(xpaths['themeBar']).click()
        #Select 2nd theme
        driver.find_element_by_xpath(xpaths['theme2']).click()
        time.sleep(3)

    def test_03_theme3(self):
        #Click on the theme Button
        driver.find_element_by_xpath(xpaths['themeBar']).click()
        #Select 3rd theme
        driver.find_element_by_xpath(xpaths['theme3']).click()
        time.sleep(3)

    def test_04_theme4(self):
        #Click on the theme Button
        driver.find_element_by_xpath(xpaths['themeBar']).click()
        #Select 4th theme
        driver.find_element_by_xpath(xpaths['theme4']).click()
        time.sleep(3)

    def test_05_theme5(self):
        #Click on the theme Button
        driver.find_element_by_xpath(xpaths['themeBar']).click()
        #Select 5th theme
        driver.find_element_by_xpath(xpaths['theme5']).click()
        time.sleep(3)

    def test_06_theme6(self):
        #Click on the theme Button
        driver.find_element_by_xpath(xpaths['themeBar']).click()
        #Select 6th theme
        driver.find_element_by_xpath(xpaths['theme6']).click()
        time.sleep(3)

    def test_07_theme7(self):
        #Click on the theme Button
        driver.find_element_by_xpath(xpaths['themeBar']).click()
        #Select 7th theme
        driver.find_element_by_xpath(xpaths['theme7']).click()
        time.sleep(3)


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

    def theme_change(self, which):
        #Click on the theme Button
        driver.find_element_by_xpath(xpaths['themeBar']).click()
        #Select 1st theme
        driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div/md-grid-list/div/md-grid-tile[" + str(which) + "]/figure/div/div[2]").click()
        time.sleep(3)


    @classmethod
    def tearDownClass(inst):
        #if not the last module
        pass
        #if it is the last module
        #driver.close()

def run_change_theme_test(webdriver):
    global driver
    driver = webdriver
    suite = unittest.TestLoader().loadTestsFromTestCase(change_theme_test)
    xmlrunner.XMLTestRunner(output=results_xml, verbosity=2).run(suite)
