from typing import Any, TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from testutils.utils import wait_for

if TYPE_CHECKING:
    from pytest_django.live_server_helper import LiveServer


class SmartDriver(WebDriver):
    live_server: "LiveServer"

    def with_timeouts(self):
        ...

    def wait_for_url(self, url: str):
        ...

    def wait_for(self, by: "By", *args: Any, clickable: bool = False):
        ...

    def click_gdpr(self):
        ...


class MaxParentsReached(NoSuchElementException):
    pass


def find_relative(obj, selector_type, path, max_parents=3):
    """Tries to find a SINGLE element with a common ancestor"""
    for c in range(max_parents, 0, -1):
        try:
            wait_for(obj, selector_type, f'./{"../" * c}/{path}')
            elems = obj.find_elements(selector_type, f'./{"../" * c}/{path}')
            if len(elems) == 1:
                return elems[0]
        except Exception:
            if max_parents == c:
                raise MaxParentsReached()
    raise NoSuchElementException()


def parent_element(obj, up=1):
    return obj.find_elements(By.XPATH, f'.{"/.." * up}')
