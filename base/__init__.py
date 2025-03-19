import re
import typing
from collections import deque
from time import sleep

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from config import (
    AUTH, xpaths,
    max_experience,
    max_windows as stop_num,
    spec_vacancies,
    ReturnValue
)

from utils import send_msg


class BaseFunctions:
    def __init__(self, driver):
        self.driver = driver
        self.pages: list[dict] = []
        self.raw_pages: list = []

    def login(self):
        self.driver.get("https://office.gms.tech")
        user = self.driver.find_element(By.ID, "username")
        user.send_keys(AUTH.login_admin)
        passw = self.driver.find_element(By.ID, "password")
        passw.send_keys(AUTH.password_admin)
        self.driver.find_element(By.XPATH, xpaths.login_button).click()

    def re_login(self):
        self.driver.execute_script("localStorage.clear()")
        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.login()

    def open_link(self, link):
        self.driver.create_new_tab(link)

    def close_all_windows(self):
        browser_list = self.driver.window_handles
        for window in browser_list[1:]:
            self.driver.switch_to.window(window)
            self.driver.close()

    def find_and_open_link(self, raw_condition, is_pop=True, is_eval=True, pre_func=None, eval_args: dict =None):
        for i, otklik in enumerate(self.pages):
            res = pre_func() if callable(pre_func) else None
            if res == ReturnValue.breaking: break
            eval_args.update({'otklik': otklik})
            condition = eval(raw_condition, eval_args) if is_eval else raw_condition
            if condition:
                self.open_link(otklik['link'])
                if is_pop: self.pages.pop(i)

    def exness_vac(self):
        send_msg(f'{AUTH.login_admin} открыл Exness')
        self.find_and_open_link("otklik['profile_status'] == 'Профиль создан' and otklik['grade'] != 'C' and '@ Exness' in otklik['vacancy_name']")

    def how_many_pages(self):
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.get('https://office.gms.tech/candidate_applications?filter=waiting_for_review&page=1')
        try:
            num_page = int(self.driver.find_element(By.XPATH, xpaths.pagination).text.split('\n')[-2].strip())
        except:
            num_page = 1

        self.driver.switch_to.window(self.driver.window_handles[0])
        return num_page

    def pages_analizing(self, gms=False):
        def soup_analize(soup):
            for i in soup.find('table', class_='table table-hover table-sm').find_all('tr')[1:]:
                all_td = i.find_all('td')
                otklick_dict = {'link': 'https://office.gms.tech' + all_td[0].find('a').get('href'),
                                'vacancy_name': all_td[2].text.strip(),
                                'grade': all_td[4].text.strip(),
                                'profile_status': all_td[6].text.strip(),
                                'verification_status': all_td[7].text.strip(),
                                'mail': all_td[3].text.split(' ')[1].strip()
                                }
                for_analize.append(otklick_dict)
                raw_pages.append(i)

        for_analize = []
        raw_pages = []
        for num in range(1, self.how_many_pages() + 1):
            self.driver.get(f'https://office.gms.tech/candidate_applications?filter=waiting_for_review&page={num}{"&gms=true" if gms else ""}')
            _ = self.driver.find_element(By.XPATH, xpaths.table_body)
            soup_analize(BeautifulSoup(self.driver.page_source, 'lxml'))

        return for_analize, raw_pages

    def refresh_pages_analizing(self):
        self.pages.clear()
        self.raw_pages.clear()
        pages = self.pages_analizing()
        self.pages += pages[0]
        self.raw_pages += pages[1]

    def get_otkliks(self):
        send_msg(f'{AUTH.login_admin} открыл Только РФ')
        otkliks = []
        for otklik in self.pages:
            if otklik['profile_status'] == 'Профиль создан' and otklik['grade'] != 'C' and '@' in otklik['vacancy_name']:
                    otkliks.append(otklik)
        return iter(otkliks)

    def all_vacancies(self, companies):
        eval_args = dict(companies=companies)
        self.find_and_open_link("otklik['vacancy_name'].split('@')[1].strip() in companies", eval_args=eval_args)

    def specific_vacancies(self, vacancies):
        eval_args = dict(vacancies=vacancies)
        self.find_and_open_link("otklik['vacancy_name'] in vacancies", eval_args=eval_args)

    def exness_check(self):
        def sum_exp(soup):
            return sum([int(exp[0]) * 12 + int(exp[1]) for exp in
                        [re.findall(r'\d+', exp.find('div', class_='fs-body-2 muted g-mb-8').text.split(',')[1].strip())
                         for exp in soup.find_all('app-experience')]])

        def otkaz_exness():
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            company = soup.find_all(class_='table table-hover table-sm')[1].find_all('tr')[2].find_all('td')[1].text
            check = self.driver.find_element(By.XPATH, xpaths.item_button).text

            if check == 'Отказать в представлении' and company == ' #16 Exness ':
                try:
                    self.driver.find_element(By.XPATH, xpaths.item_button).click()
                    sleep(1)
                    self.driver.close()
                except:
                    pass

        print('проверка откликов Exness')
        send_msg(f'{AUTH.login_admin} автоотказ Exness')
        browser_list = self.driver.window_handles
        norm_eng_level = ['C2', 'C1', 'B2']
        ne_norm_eng_level = ['B1', 'A2', 'A1', 'NA']
        for i in browser_list[1:]:
            sleep(1)
            self.driver.switch_to.window(i)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            pars = soup.find_all('app-card')[1].find('div', class_='g-mt-20').text
            if 'Языки Английский' in pars:
                eng_level = pars.split('  : ')[1].replace(' Немецкий', '').replace(' Французский', '')
            else:
                eng_level = 'NA'

            if eng_level[:2] in norm_eng_level:
                if sum_exp(soup) < max_experience[0] and sum_exp(soup) != 0:
                    otkaz_exness()
            elif eng_level[:2] in ne_norm_eng_level:
                otkaz_exness()

    def refuse_close_page(self):
        check = self.driver.find_element(By.XPATH, xpaths.item_button).text
        if check == 'Отказать в представлении':
            try:
                check.click()
                sleep(1.5)
                self.driver.close()
            except:
                pass

    def city_check(self, cities, countries, not_this_cities=False, not_this_countries=False):  #
        send_msg(f'{AUTH.login_admin} автоотказ Только РФ')
        for i in self.driver.window_handles[1:]:
            sleep(1)
            self.driver.switch_to.window(i)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            location = soup.find(class_='b-profile__location').text.replace('Живёт в городе ', '').strip()
            city = location.split(',')[0]
            country = location.split(',')[1][1:]
            if (not_this_cities ^ (city in cities)) or (not_this_countries ^ (country in countries)):
                self.refuse_close_page()
                print('отказал', city)

    def open_profile_for_grade(self, grade):
        if grade == 1:
            grade = 'A'
        elif grade == 2:
            grade = 'B'
        elif grade == 3:
            grade = 'Не классифицирован'

        eval_args = dict(grade=grade)
        self.find_and_open_link(
            "otklik['profile_status'] == 'Профиль создан' and otklik['grade'] == grade",
            pre_func=self.find_stop_count_opened_windows, eval_args=eval_args
        )

    def find_stop_count_opened_windows(self):
        browser_list = self.driver.window_handles
        if len(browser_list) > stop_num:
            return ReturnValue.breaking

    def special_vac(self):
        send_msg(f'{AUTH.login_admin} открыл спец вакансии')

        full_vacancy_name = spec_vacancies  # вставить сюда название вакансии в формате: 'UX/UI Designer @ Leroy Merlin'
        eval_args = dict(full_vacancy_name=full_vacancy_name)
        self.find_and_open_link(
            "otklik['profile_status'] == 'Профиль создан' and otklik['grade'] != 'C' and otklik['vacancy_name'] in full_vacancy_name",
            pre_func=self.find_stop_count_opened_windows, eval_args=eval_args
        )


    def browser_list_for_auto(self, browser_list) -> typing.Generator[tuple[BeautifulSoup, str, str, str, str], None, None]:
        for i in browser_list[1:]:
            self.driver.switch_to.window(i)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            grade = soup.find_all('tbody')[0].find_all('tr')[3].text.replace('Грейд', '').strip()
            comment, button_check, company = "", "", ""
            for i in soup.find_all('tbody')[1].find_all('tr'):
                if i.find_all('td')[0].text == 'Сопроводительный комментарий':
                    comment = i.find_all('td')[1].text.strip()
            try:
                button_check = soup.find(class_='btn btn-success').text.strip()
            except:
                try:
                    button_check = soup.find(class_='btn btn-success mr-3').text.strip()
                except:
                    comment = 1
            yield soup, grade, comment, button_check, company

    def find_company(self, soup):
        return [f"{i.find_all('td')[1].text}".strip() for i in soup.find_all('tbody')[1].find_all('tr') if
                i.find_all('td')[0].text == 'В компанию'][-1]

    def send_but(self, company=''):
        send_but = self.driver.find_element(By.XPATH, xpaths.send_but_other if company != '#' else xpaths.send_but)
        send_but.click()
        sleep(1)

    def if_button_check(self, button_check) -> ReturnValue:
        if button_check == 'Тест представления':
            return ReturnValue.test
        elif button_check == 'Верифицировать' or button_check == 'Кандидат GMS готов':
            return ReturnValue.verify_or_GMS

    def code_on_auto_a_and_auto_b(self, value, soup):
        match value:
            case ReturnValue.test:
                self.driver.find_element(By.XPATH, xpaths.button_check).click()
                sleep(1)
                self.driver.close()
            case ReturnValue.verify_or_GMS:
                self.send_but()
                company = self.find_company(soup)
                self.send_but(company)
                self.driver.close()
            case _:
                sleep(1)
                return

    def auto_b_without_vac(self):
        browser_list = self.driver.window_handles
        for soup, grade, comment, button_check, company in self.browser_list_for_auto(browser_list):
            self.code_on_auto_a_and_auto_b(self.if_button_check(button_check), soup)

    def auto_a(self):
        send_msg(f'{AUTH.login_admin} автопредставления А')
        browser_list = self.driver.window_handles
        for soup, grade, comment, button_check, company in self.browser_list_for_auto(browser_list):
            if grade == 'A' and comment == '':
                self.code_on_auto_a_and_auto_b(self.if_button_check(button_check), soup)

    def open_b_without_vac(self):
        send_msg(f'{AUTH.login_admin} открыть В-грейды без откликов')
        self.find_and_open_link("tklik['profile_status'] == 'Профиль создан' and '@' not in otklik['vacancy_name']")


    def open_all_c(self):
        send_msg(f'{AUTH.login_admin} открыть все С-грейд')
        self.find_and_open_link("otklik['grade'] == 'C'")

    def gms_vac(self):
        send_msg(f'{AUTH.login_admin} открыть вакансии GMS')
        self.find_and_open_link("otklik['profile_status'] == 'Профиль создан'")

    def next_candidate(self, counter, to_predst):
        self.driver.switch_to.window(self.driver.window_handles[0])
        for i in to_predst[counter[0]][1:]:
            self.driver.switch_to.new_window('tab')
            self.driver.get(f'https://office.gms.tech/{i}')

        counter[0] += 1

    def cycle_predst(self):
        send_msg(f'{AUTH.login_admin} цикличное представления')

        all_otklik = []
        for i in self.pages:
            if i['profile_status'] == 'Профиль создан':
                all_otklik.append([i['mail'], i['link']])

        all_mails = set()
        for i in all_otklik:
            all_mails.add(i[0])
        to_predst = []
        for i in all_mails:
            candidate = [i]
            for n in all_otklik:
                if n[0] == i: candidate.append(n[1])
            to_predst.append(candidate)
        to_predst.sort(key=len, reverse=True)

        counter = [0]

        return counter, to_predst

    def how_many_vac(self):
        send_msg(f'{AUTH.login_admin} подсчет вакансий')

        number = 0
        for num in range(1, self.how_many_pages() + 1):
            self.driver.get(f'https://office.gms.tech/candidate_applications?filter=waiting_for_review&page={num}')
            _ = self.driver.find_element(By.XPATH, xpaths.table_body)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            for i in soup.find(class_='table table-hover table-sm').find_all('tr')[1:]:
                if i.find_all('td')[6].text == 'Профиль создан': number += 1
        print('Сейчас надо представить:', number, 'вакансий')


