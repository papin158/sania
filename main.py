import logging

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from config import AUTH, set_intercept_request
from webdriver_manager.chrome import ChromeDriverManager

from utils import Driver, MainGUI
from base import BaseFunctions

logging.basicConfig(level=logging.INFO)

driver = Driver(service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(10)
driver.request_interceptor = set_intercept_request(AUTH.login_admin, AUTH.password_admin)

functions = BaseFunctions(driver)
gui = MainGUI(functions)

functions.login()
gui.start()