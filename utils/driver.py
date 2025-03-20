from seleniumwire import webdriver

class Driver(webdriver.Chrome):
    def __init__(self, *args, seleniumwire_options=None, **kwargs):
        super().__init__(*args, seleniumwire_options=seleniumwire_options, **kwargs)
        self._current_implicitly_wait = 0
        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    """
        })

    def __slow_open(self, url):
        self.switch_to.new_window('tab')
        self.get(url)

    def __fast_open(self, url):
        script = f"window.open('{url}','_blank');"
        return self.execute_script(script)
        # return self.execute_cdp_cmd("Target.createTarget", {"url": url})

    def create_new_tab(self, url='about:blank', slow=False):
        if slow: self.__slow_open(url)
        else: self.__fast_open(url)


    def close_last_tab(self):
        ...


    @property
    def current_implicitly_wait(self):
        return self._current_implicitly_wait

    def implicitly_wait(self, seconds):
        super().implicitly_wait(seconds)
        self._current_implicitly_wait = seconds


