import contextlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs

from django.http import QueryDict
from django.urls import reverse

import responses
from selenium.webdriver.common.by import By


class MutableQueryDict(QueryDict):
    def __init__(self, query_string=None, mutable=False, encoding=None):
        super().__init__(query_string, mutable, encoding)
        self._mutable = True

    def unflat(self: QueryDict) -> dict:
        # Transform `{'attributes[]': 'size', 'attributes[]': 'gender'}` into
        # `{'attributes': ['size', 'gender']}`
        def handle_multiple_keys(multidict: QueryDict):
            data = dict()
            for k in multidict.keys():
                values = multidict.getlist(k)
                values = [handle_multiple_keys(v) if hasattr(v, "keys") else v for v in values]
                if len(k) > 2 and k.endswith("[]"):
                    k = k[:-2]
                else:
                    values = values[0]
                data[k] = values
            return data

        data = handle_multiple_keys(self)

        def make_tree(data):
            for k, v in list(data.items()):
                r = re.search(r"^([^\[]+)\[([^\[]+)\](.*)$", k)
                if r:
                    k0 = r.group(1)
                    k1 = r.group(2) + r.group(3)
                    data[k0] = data.get(k0, {})
                    data[k0][k1] = v
                    data[k0] = make_tree(data[k0])
                    del data[k]
            return data

        data = make_tree(data)

        # Transform `{'items': {'0': {'plan': 'pro-yearly'}}}` into
        # `{'items': [{'plan': 'pro-yearly'}]}`
        def transform_lists(data):
            if len(data) > 0 and all([re.match(r"^[0-9]+$", k) for k in data.keys()]):
                new_data = [(int(k), v) for k, v in data.items()]
                new_data.sort(key=lambda k: int(k[0]))
                data = []
                for k, v in sorted(new_data, key=lambda k: int(k[0])):
                    if type(v) is dict:
                        data.append(transform_lists(v))
                    else:
                        data.append(v)
                return data
            else:
                for k in data.keys():
                    if type(data[k]) is dict:
                        data[k] = transform_lists(data[k])
                return data

        data = transform_lists(data)

        return data


def payload(filename, section=None, merge: dict | None = None):
    data = json.load((Path(__file__).parent / filename).open())
    if section:
        return data[section]
    if merge:
        data = {**data, **merge}
    return data


def check_link_by_class(selenium, cls, view_name):
    link = selenium.find_element_by_class_name(cls)
    url = reverse(f"{view_name}")
    return f' href="{url}"' in link.get_attribute("innerHTML")


def get_all_attributes(driver, element):
    return list(
        driver.execute_script(
            "var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) {"
            " items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value"
            " }; return items;",
            element,
        )
    )


def is_clickable(driver, element):
    """Tries to click the element"""
    try:
        element.click()
        return True
    except Exception:
        return False


def mykey(group, request):
    return request.META["REMOTE_ADDR"][::-1]


def callable_rate(group, request):
    if request.user.is_authenticated:
        return None
    return (0, 1)


def matcher_address(address):
    def match(request):
        try:
            request_body = request.body.decode("utf-8")
            return address == json.loads(request_body)["address"], ""
        except responses.JSONDecodeError:
            return False
        except KeyError:
            return False

    return match


def matcher_debugger(return_value=True):
    def debugger(request_body):
        try:
            if isinstance(request_body, bytes):
                request_body = request_body.decode("utf-8")
            try:
                payload = json.loads(request_body)
            except responses.JSONDecodeError:
                try:
                    payload = parse_qs(request_body)
                except Exception:
                    payload = request_body
        except Exception:
            pass
        print("##### MATCHER_DEBUGGER", payload, return_value)
        return return_value

    return debugger


def _selenium_login(user, browser, live_server):
    browser.implicitly_wait(3)
    browser.get(f"{live_server.url}/i/")

    link = browser.find_element_by_partial_link_text("My Bob")
    link.click()

    browser.find_element_by_name("auth-username").send_keys(user.username)
    browser.find_element_by_name("auth-password").send_keys(user._password)
    browser.find_element_by_id("login-button").click()
    browser.live_server = live_server
    browser.user = user
    return browser


def wait_for(driver, *args, timeout=10, clickable=False):
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    wait = WebDriverWait(driver, timeout)
    if clickable:
        wait.until(EC.element_to_be_clickable((*args,)))
    else:
        wait.until(EC.visibility_of_element_located((*args,)))
    return driver.find_element(*args)


def wait_for_url(driver, url):
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains(url))


def find_by_css(browser, *args):
    return wait_for(browser, By.CSS_SELECTOR, *args)


@contextlib.contextmanager
def set_flag(flag_name, on_off):
    from flags.state import _set_flag_state, flag_state

    state = flag_state(flag_name)
    _set_flag_state(flag_name, on_off)
    yield
    _set_flag_state(flag_name, state)


def force_login(driver, *args):
    from importlib import import_module

    from django.conf import settings
    from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY

    user = args[0]
    base_url = args[1]

    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
    with driver.with_timeouts(page=10):
        driver.get(base_url)

    session = SessionStore()
    session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session.save()

    driver.add_cookie({"name": settings.SESSION_COOKIE_NAME, "value": session.session_key, "path": "/"})
    driver.refresh()


def get_messages(res):
    if hasattr(res, "context") and "messages" in res.context:
        return list(map(str, res.context["messages"]))
    return []


def assert_submit(res, name="form", code: int = 302):
    assert res.status_code == code, f"Expected {code} got {res.status_code}"
    assert not res.context[name].errors, res.context[name].errors


def assert_fail(res, name="form", code: int = 200):
    assert res.status_code == code, f"Expected {code} got {res.status_code}"
    assert res.context[name].errors, res.context[name].errors