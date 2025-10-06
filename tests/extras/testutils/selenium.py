import contextlib
from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select

if TYPE_CHECKING:
    from pytest_django.live_server_helper import LiveServer
    from selenium.webdriver.common.timeouts import Timeouts


class SmartDriver(WebDriver):
    live_server: "LiveServer"

    @classmethod
    def factory(cls, driver, live_server):
        driver.live_server = live_server
        driver.go = cls.go.__get__(driver)
        driver.select2 = cls.select2.__get__(driver)
        driver.highlight = cls.highlight.__get__(driver)
        driver.with_timeouts = cls.with_timeouts.__get__(driver)
        driver.set_input_value = cls.set_input_value.__get__(driver)

        driver.wait_for = cls.wait_for.__get__(driver)
        driver.wait_for_url = cls.wait_for_url.__get__(driver)
        driver.login = cls.login.__get__(driver)
        return driver

    @contextlib.contextmanager
    def with_timeout(self, wait=None, page=None, script=None):
        _current: Timeouts = self.timeouts
        if wait:
            self.implicitly_wait(wait)
        if page:
            self.set_page_load_timeout(page)
        if script:
            self.set_script_timeout(script)
        yield
        self.timeouts = _current

    def go(self, path, wait=True):
        self.get(f"{self.live_server.url}{path}")
        if wait:
            self.wait_for_url(path)

    def select2(self, selector, value, by=By.ID):
        el = self.wait_for(by, f"select2-id_{selector}-container")
        el.click()
        el = self.wait_for(By.CLASS_NAME, "select2-search__field")
        el.click()
        el.send_keys(value)
        self.switch_to.active_element.send_keys(Keys.ENTER)

    def highlight(self, by_or_element, selector=None):
        if selector:
            el = self.wait_for(by_or_element.CLASS_NAME, selector)
        else:
            el = by_or_element
        self.execute_script("arguments[0].setAttribute('style', 'background: yellow; border: 2px solid red;');", el)

    @contextlib.contextmanager
    def with_timeouts(self, wait=None, page=None, script=None):
        _current: Timeouts = self.timeouts
        if wait:
            self.implicitly_wait(wait)
        if page:
            self.set_page_load_timeout(page)
        if script:
            self.set_script_timeout(script)
        yield
        self.timeouts = _current

    def login(self, user, tenant, base_url="/"):
        from importlib import import_module

        from django.conf import settings
        from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY

        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        with self.with_timeouts(page=10):
            self.go(base_url)

        session = SessionStore()
        session[SESSION_KEY] = user._meta.pk.value_to_string(user)
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()

        self.add_cookie({"name": settings.SESSION_COOKIE_NAME, "value": session.session_key, "path": "/"})
        self.refresh()
        self.go(base_url)
        select = Select(self.wait_for(By.NAME, "tenant"))
        select.select_by_value(str(tenant.pk))

    def wait_for(self, *args, timeout=10, clickable=False):
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(self, timeout)
        if clickable:
            wait.until(EC.element_to_be_clickable((*args,)))
        else:
            wait.until(EC.visibility_of_element_located((*args,)))
        return self.find_element(*args)

    def wait_for_url(self, url):
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(self, 10)
        wait.until(EC.url_contains(url))

    def set_input_value(self, *args):
        rules = args[:-1]
        el = self.find_element(*rules)
        el.clear()
        el.send_keys(args[-1])


class MaxParentsReached(NoSuchElementException):
    pass


#
# def find_relative(obj, selector_type, path, max_parents=3):
#     """Tries to find a SINGLE element with a common ancestor"""
#     for c in range(max_parents, 0, -1):
#         try:
#             wait_for(obj, selector_type, f'./{"../" * c}/{path}')
#             elems = obj.find_elements(selector_type, f'./{"../" * c}/{path}')
#             if len(elems) == 1:
#                 return elems[0]
#         except Exception:
#             if max_parents == c:
#                 raise MaxParentsReached()
#     raise NoSuchElementException()
#
#
# def parent_element(obj, up=1):
#     return obj.find_elements(By.XPATH, f'.{"/.." * up}')
