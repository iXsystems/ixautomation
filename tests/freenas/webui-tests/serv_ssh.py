# Author: Rishabh Chauhan
# License: BSD
# Location for tests  of FreeNAS new GUI
# Test case count: 4

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
          'turnoffConfirm' : "/html/body/div[4]/div/div[2]/md-dialog-container/app-confirm/div[2]/button[1]",
          'status' : "/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[14]/md-card/div[2]/div[1]/md-chip"
        }

class configure_ssh_test(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        driver.implicitly_wait(30)
        pass

    def test_01_nav_services(self):
        # Click  Service menu
        print ("navigating to service menu")
        driver.find_element_by_xpath(xpaths['navService']).click()
        # allowing the button to load
        time.sleep(1)
        # get the ui element
        ui_element=driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/app-breadcrumb/div/ul/li")
        # get the weather data
        page_data=ui_element.text
        print ("the Page now is: " + page_data)
        # assert response
        self.assertTrue("Services" in page_data)



    def test_02_turnon_ssh (self):
        # click Service Menu
        driver.find_element_by_xpath(xpaths['navService']).click()
        # allowing the button to load
        time.sleep(1)
        print (" turning on the ssh service")
        # scroll down
        driver.find_element_by_tag_name('html').send_keys(Keys.END)
        time.sleep(2)
        self.status_change("14", "start")

    def test_03_configure_ssh(self):
        print (" configuring ssh service with root access")
        time.sleep(2)
        # click on configure button
        driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[14]/md-card/div[2]/div[3]/button").click()
        # click on Login as Root with Passsword
        driver.find_element_by_xpath("//*[@id='2']/form-checkbox/div/md-checkbox/label/div").click()
        # click on save button
        driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/ssh-edit/entity-form/md-card/div/form/md-card-actions/button[1]").click()


    def test_04_turnoff_ssh(self):
        # click Service Menu
        driver.find_element_by_xpath(xpaths['navService']).click()
        # allowing the button to load
        time.sleep(1)
        print (" turning off the ssh service")
        # scroll down
        driver.find_element_by_tag_name('html').send_keys(Keys.END)
        time.sleep(2)
        self.status_change("14", "stop")
        time.sleep(10)

        # Next step-- To check if the new user is present in the list via automation


    # method to test if an element is present
    def is_element_present(self, how, what):
        """
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        """
        try: driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True

    def status_change(self, which, to):
        print ("executing the status change function with input " + which + " + " + to)
        # get the ui element
        ui_element_status=driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[" + str(which) + "]/md-card/div[2]/div[1]/md-chip")
        # get the status data
        status_data=ui_element_status.text
        print ("current status is: " + status_data)
        if to == "start":        
            if status_data == "STOPPED": 
                # Click on the afp toggle button
                driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[" + str(which) + "]/md-card/div[2]/div[1]/button").click()
                time.sleep(1)
                print ("status has now changed to running")
            else:
                print ("the status is already " + status_data)
        elif to == "stop":
            if status_data == "RUNNING":
                #Click on the afp toggle button
                driver.find_element_by_xpath("/html/body/app-root/app-admin-layout/md-sidenav-container/div[6]/div/services/div/service[" + str(which) + "]/md-card/div[2]/div[1]/button").click()
                time.sleep(1)
                # re-confirming if the turning off the service
                if self.is_element_present(By.XPATH,xpaths['turnoffConfirm']):
                    driver.find_element_by_xpath(xpaths['turnoffConfirm']).click()
            else: 
                print ("the status is already" + status_data)


    @classmethod
    def tearDownClass(inst):
        pass


def run_configure_ssh_test(webdriver):
    global driver
    driver = webdriver
    suite = unittest.TestLoader().loadTestsFromTestCase(configure_ssh_test)
    xmlrunner.XMLTestRunner(output=results_xml, verbosity=2).run(suite)
