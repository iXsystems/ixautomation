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
          'turnoffConfirm' : "/html/body/div[3]/div/div[2]/md-dialog-container/app-confirm/div[2]/button[1]",
          'status' : "/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[14]/md-card/md-list/md-list-item[1]/div/p/em"
        }

class configure_ssh_test(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        driver.implicitly_wait(30)
        pass

    def test_01_turnon_ssh (self):
        print (" turning on the ssh service")
        time.sleep(5)
        #Click Service Menu
        driver.find_element_by_xpath(xpaths['navService']).click()

        #check if the Services page is opens
        time.sleep(1)
        #get the ui element
        ui_element=driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/app-breadcrumb/div/ul/li")
        #get the weather data
        page_data=ui_element.text
        print ("the Page now is: " + page_data)
        #assert response
        self.assertTrue("Services" in page_data)

        #scroll down
        driver.find_element_by_tag_name('html').send_keys(Keys.END)
        time.sleep(2)
        #check if the element is present

        #get the ui element
        ui_element_status=driver.find_element_by_xpath(xpaths['status'])
        #get the weather data
        status_data=ui_element_status.text
        print ("current status is: " + status_data)
        if status_data == "stopped": 
            #Click on the ssh toggle button
            driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[14]/md-card/md-toolbar/div/md-toolbar-row/md-slide-toggle/label/div").click()
            time.sleep(1)
            print ("status has now changed to running")
        else:
            print ("current status is--: " + status_data)
        #re-confirming if the turning off the service
        if self.is_element_present(By.XPATH,xpaths['turnoffConfirm']):
            driver.find_element_by_xpath(xpaths['turnoffConfirm']).click()

    def test_02_configure_ssh(self):
        print (" configuring ssh service with root access")
        time.sleep(2)
        #click on configure button
        driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[14]/md-card/md-card-actions/button").click()
        #click on Login as Root with Passsword
        driver.find_element_by_xpath("//*[@id='2']/form-checkbox/div/md-checkbox/label/div").click()
        #click on save button
        driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/ssh-edit/entity-form/md-card/div/form/md-card-actions/button[1]").click()
        time.sleep(10)


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
        #driver.close()
        pass


def run_configure_ssh_test(webdriver):
    global driver
    driver = webdriver
    suite = unittest.TestLoader().loadTestsFromTestCase(configure_ssh_test)
    xmlrunner.XMLTestRunner(output=results_xml, verbosity=2).run(suite)
