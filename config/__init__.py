import enum
from dataclasses import dataclass

from .env_data import *
from .company_bases import *
from .scripts import *


@dataclass(frozen=True, order=True, slots=True)
class AUTH:
    login_admin: str = login_admin
    password_admin: str = password_admin

class XPATHs:
    button_check = '/html/body/app-root/div/app-candidate-application/app-candidate-application-item/div/div/div/div[3]/div/div[1]/form/div[2]/button[2]'
    send_but = '/html/body/app-root/div/app-candidate-application/app-candidate-application-item/div/div/div/div[3]/div/div[1]/div/button'
    send_but_other = '/html/body/app-root/div/app-candidate-application/app-candidate-application-item/div/div/div/div[3]/div/div[1]/form/div[2]/button[2]'
    table_body = '/html/body/app-root/div/app-candidate-applications/app-candidate-applications-list/table/tbody/tr[1]/td[1]'
    pagination = '/html/body/app-root/div/app-candidate-applications/app-candidate-applications-list/ngb-pagination[1]/ul'
    item_button = '/html/body/app-root/div/app-candidate-application/app-candidate-application-item/div/div/div/div[3]/div/div[2]/form/div/button'
    login_button = '/html/body/app-root/div/app-auth/div/div[3]/div/button'

class ReturnValue(enum.IntEnum):
    test = 0
    verify_or_GMS = 1


AUTH = AUTH()
xpaths = XPATHs()

__all__ = [
    "AUTH",
    "russia",
    "other_countries",
    "spec_vacancies",
    "max_experience",
    "xpaths",
    "ReturnValue",
    "max_windows",
    "get_txt_data",
    "set_intercept_request",
    "tg_token"
]