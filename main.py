import logging
from selenium.webdriver.chrome.service import Service
from config import AUTH, set_intercept_request
from webdriver_manager.chrome import ChromeDriverManager

from utils import Driver, MainGUI
from base import BaseFunctions

logging.basicConfig(level=logging.WARNING)

def main(type_open_links):
    if type_open_links == 59 or type_open_links == 79: type_open_links = True
    driver = Driver(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(10)
    driver.request_interceptor = set_intercept_request(AUTH.login_admin, AUTH.password_admin)

    functions = BaseFunctions(driver, type_open_links=type_open_links)
    gui = MainGUI(functions)

    functions.login()
    gui.start()

if __name__ == '__main__':
    print(
        'Из-за некоторых проблем с вкладками и скоростью загрузки страницы '
        'быстрое их открытие теперь по-умолчанию выключено'
    )
    type_speed = ord(input('Установить скоростное открытие вкладок? [Y/[N]]'))
    main(type_speed)