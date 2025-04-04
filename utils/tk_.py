import ctypes
import inspect
import multiprocessing, threading
import sys
import tkinter as tk
from functools import partial
from time import sleep

from base import BaseFunctions
from config import AUTH, max_experience, russia, other_countries
from utils import send_msg

def _async_raise(tid):
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(SystemExit))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class ThreadWithExc(threading.Thread):
    def _get_my_tid(self):
        if not self.is_alive(): # Note: self.isAlive() on older version of Python
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        # TODO: in python 2.6, there's a simpler way to do: self.ident

        raise AssertionError("could not determine the thread's id")

    def raise_exc(self):
        if sys.version_info[:2] > (3,3):
            _async_raise(self.ident)
        else:
            _async_raise(self._get_my_tid())


# class Button(tk.Button):
#     def __init__(self, master=None, cnf={}, type="", **kw):
#         if type != "stop":
#             kw.get('command')



# tk.Button = Button

class NextNum:
    __counts = {0: 0}

    def __call__(self, column):
        self.__counts[column] = self.__counts.get(column, 1) + 1
        return {'row': self.__counts[column], "column": column}
        


class Main:
    def __init__(self, functions: BaseFunctions):
        self.root = tk.Tk()
        self.root.title('v.1: Дорогу осилит идущий')
        self.experience = None
        self.experience_ERR = None
        self.functions = functions
        self.cur_proc: multiprocessing.Process | None = None
        self.cur_thread: ThreadWithExc | None = None

        # Получаем разрешение экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Задаем размеры окна
        window_width = 630
        window_height = 450

        # Задаем координаты окна
        x = screen_width - window_width
        y = 0

        # Устанавливаем размеры и координаты окна
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        send_msg(f'{AUTH.login_admin} запустил скрипт')

    def __create(self):
        panel_window = tk.Toplevel(self.root)
        panel_window.title('v.1')

        panel_window.title('v.1: Дорогу осилит идущий')

        # Получаем разрешение экрана
        screen_width = panel_window.winfo_screenwidth()

        # Задаем размеры окна
        p_window_width = 150
        p_window_height = 100

        # Задаем координаты окна
        x = screen_width - p_window_width
        y = 0

        # Устанавливаем размеры и координаты окна
        panel_window.geometry(f"{p_window_width}x{p_window_height}+{x}+{y}")

        # Создаем кнопки и добавляем их на панель
        button1 = tk.Button(panel_window, text="следующий", command=lambda: self.functions.next_candidate(*self.functions.cycle_predst()))
        button1.pack(padx=10, pady=10)

        button2 = tk.Button(panel_window, text="Закрыть окно", command=panel_window.destroy)
        button2.pack(padx=10, pady=10)

    def change_exp(self):
        exp = self.experience.get()
        try:
            max_experience[0] = round(float(exp) * 12)
            self.experience_ERR['text'] = ''
        except ValueError:
            self.experience_ERR['text'] = 'Введите число'

    def change_text(self, label, func):
        text = str(func()).strip()
        label['text'] = text if text else ''

    def set_auto_row(self, auto_row, *elems):
        [elem.grid(**auto_row()) for elem in elems]


    def start_thread(self, function):
        if self.cur_thread is None or not self.cur_thread.is_alive():
            self.cur_thread = ThreadWithExc(target=function, daemon=True)
            self.cur_thread.start()
            return
        print("Сперва остановите другую операцию")

    def stop_thread(self):
        if self.cur_thread is not None and self.cur_thread.is_alive():
            self.cur_thread.raise_exc()
            self.cur_thread = None

    def quit(self):
        self.stop_thread()
        self.root.destroy()

    def start(self):
        self.__create()

        eng_level_text = """Для Exness
        (автоотказ для английского ниже В2"""
        how_many_vac_text = """Сколько
        вакансий
        надо представить"""

        experience_text = tk.Label(self.root, text='Установить проходной стаж')
        self.experience = tk.Entry(self.root)
        self.experience.insert(0, f"{max_experience[0] / 12}")
        experience_OK = tk.Button(self.root, text='ОК', command=self.change_exp)
        self.experience_ERR = tk.Label(self.root, text='', fg='red', font=('Arial', '20', 'bold'))

        how_many_vac_label = tk.Label(self.root, text='')
        how_many_vac = tk.Button(self.root, text=how_many_vac_text, command=lambda: self.change_text(how_many_vac_label, self.functions.get_string_vac))


        close_all = tk.Button(self.root, text="закрыть окна", command=self.functions.close_all_windows)
        exness = tk.Button(self.root, text="Exness", command=self.functions.exness_vac)
        eng_level = tk.Button(self.root, text=eng_level_text, command=lambda: self.start_thread(self.functions.exness_check), fg="red")
        rus_all = tk.Button(self.root, text="РФ все вакансии (открыть)", command=partial(self.functions.all_vacancies, russia.companies))
        rus_spec = tk.Button(self.root, text="РФ только по должностям (открыть)",
                             command=partial(self.functions.specific_vacancies, russia.vacancies))
        rus_auto_check = tk.Button(self.root, text="Только РФ (автоотказ)",
                                   command=lambda: self.start_thread(self.functions.city_check(russia.cities, ['Russia', 'Россия'])), fg="red")
        no_rus_vac_all = tk.Button(self.root, text="Вне РФ все вакансии (открыть)",
                                   command=partial(self.functions.all_vacancies, other_countries.companies))
        no_rus_vac_spec = tk.Button(self.root, text="Вне РФ только по должностям (открыть)",
                                    command=partial(self.functions.all_vacancies, other_countries.vacancies))
        no_rus_auto_check = tk.Button(self.root, text="Вне РФ (автоотказ)",
                                      command=lambda: self.start_thread(self.functions.city_check(other_countries.cities, ['Russia', 'Россия'], False,
                                                                 True)), fg="red")
        grade_a = tk.Button(self.root, text="А (открыть)", command=partial(self.functions.open_profile_for_grade, 1))
        grade_b = tk.Button(self.root, text="В (открыть)", command=partial(self.functions.open_profile_for_grade, 2))
        grade_without = tk.Button(self.root, text="Без грейда (открыть)", command=partial(self.functions.open_profile_for_grade, 3))
        special = tk.Button(self.root, text="Специальные вакансии (открыть)", command=self.functions.special_vac)
        auto_a_grade = tk.Button(self.root, text="Автопредставления А грейдов", command=lambda: self.start_thread(self.functions.auto_a), fg="red")
        auto_b_outvac = tk.Button(self.root, text="Верифицировать В (!Без вакансий!)", command=lambda: self.start_thread(self.functions.auto_b_without_vac), fg="red")
        auto_gms_outvac = tk.Button(self.root, text="Автопредставление GMS", command=lambda: self.start_thread(self.functions.auto_b_without_vac), fg="red")
        open_b_without = tk.Button(self.root, text="Открыть В грейды без вакансий", command=self.functions.open_b_without_vac)
        gms = tk.Button(self.root, text="GMS", command=self.functions.gms_vac)
        open_c_grade = tk.Button(self.root, text="Открыть все С", command=self.functions.open_all_c)
        cycle_button = tk.Button(self.root, text="Цикличное  представление", command=self.functions.cycle_predst)
        quit = tk.Button(self.root, text="Quit", command=self.quit)
        refresh_pages = tk.Button(self.root, text="Обновить страницы", command=lambda: self.start_thread(self.functions.refresh_pages_analysing))
        refresh_pages_gms = tk.Button(self.root, text="Обновить GMS", command=lambda: self.start_thread(lambda: self.functions.refresh_pages_analysing(True)))
        re_login = tk.Button(self.root, text="Перезайти на сайт", command=lambda: self.start_thread(self.functions.re_login), font=('Arial', '10', 'bold'), fg="red")
        stop_pred = tk.Button(self.root, text="Остановить работу", command=self.stop_thread, font=('Arial', '10', 'bold'), fg="red")

        auto_row = NextNum()

        self.set_auto_row(
            lambda: auto_row(0),
            refresh_pages,
            exness,
            rus_all,
            rus_spec,
            no_rus_vac_all,
            no_rus_vac_spec,
            special,
            grade_a,
            open_b_without,
            gms,
            grade_b,
            grade_without,
            open_c_grade,
            cycle_button
        )

        self.set_auto_row(
            lambda: auto_row(1),
            refresh_pages_gms,
            close_all,
            how_many_vac,
            how_many_vac_label,
            quit,
            experience_text,
            experience_OK,
            self.experience,
            self.experience_ERR,
            stop_pred
        )

        self.set_auto_row(
            lambda: auto_row(2),
            eng_level,
            rus_auto_check,
            no_rus_auto_check,
            auto_a_grade,
            auto_b_outvac,
            auto_gms_outvac,
            re_login
        )


        self.root.mainloop()



