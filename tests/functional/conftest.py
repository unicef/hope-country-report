from typing import TYPE_CHECKING

import contextlib
import os

import pytest

if TYPE_CHECKING:
    from testutils.selenium import SmartDriver


def pytest_configure(config):
    if not config.option.driver:
        setattr(config.option, "driver", "chrome")
    os.environ["DISPLAY"] = ":10.0"


@pytest.fixture
def capabilities(capabilities):
    capabilities["loggingPrefs"] = {"browser": "ALL"}
    capabilities["acceptInsecureCerts"] = True
    return capabilities


@pytest.fixture
def edge_options(request, edge_options):
    if not request.config.getvalue("show_browser"):
        edge_options.add_argument("--headless")
    edge_options.add_argument("start-maximized")
    edge_options.add_argument("--lang=en-GB")
    edge_options.add_argument("--disable-infobars")
    edge_options.add_argument("--disable-extensions")
    edge_options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 1,
            "profile.default_content_setting_values.notifications": 1,
        },
    )
    # https://stackoverflow.com/questions/53902507/unknown-error-session-deleted-because-of-page-crash-from-unknown-error-cannot
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--disable-browser-side-navigation")
    edge_options.add_argument("--dns-prefetch-disable")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--disable-popup-blocking")

    # ssl
    edge_options.add_argument("--ignore-certificate-errors")
    edge_options.add_argument("--allow-insecure-localhost")

    return edge_options


@pytest.fixture
def chrome_options(request, chrome_options):
    # chrome_options = Options()
    if not request.config.getvalue("show_browser"):
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--lang=en-GB")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")

    prefs = {"profile.default_content_setting_values.notifications": 1}  # explicitly allow notifications
    chrome_options.add_experimental_option("prefs", prefs)

    return chrome_options


SELENIUM_DEFAULT_PAGE_LOAD_TIMEOUT = 20
SELENIUM_DEFAULT_IMPLICITLY_WAIT = 1
SELENIUM_DEFAULT_SCRIPT_TIMEOUT = 1


@contextlib.contextmanager
def timeouts(driver, wait=None, page=None, script=None):
    from selenium.webdriver.common.timeouts import Timeouts

    _current: Timeouts = driver.timeouts
    if wait:
        driver.implicitly_wait(wait)
    if page:
        driver.set_page_load_timeout(page)
    if script:
        driver.set_script_timeout(script)
    yield
    driver.timeouts = _current


def go(driver, path):
    return driver.get(f"{driver.live_server.url}{path}")


def set_input_value(driver, *args):
    rules = args[:-1]
    el = driver.find_element(*rules)
    el.clear()
    el.send_keys(args[-1])


@pytest.fixture
def browser(transactional_db, driver, live_server, settings, monkeypatch) -> "SmartDriver":
    from django.core.handlers.wsgi import WSGIRequest

    from testutils.utils import find_by_css, force_login, wait_for, wait_for_url

    monkeypatch.setattr(WSGIRequest, "user_ip", "127.0.0.1", raising=False)

    driver.live_server = live_server

    driver.go = go.__get__(driver)
    driver.with_timeouts = timeouts.__get__(driver)
    driver.set_input_value = set_input_value.__get__(driver)

    driver.wait_for = wait_for.__get__(driver)
    driver.find_by_css = find_by_css.__get__(driver)
    driver.wait_for_url = wait_for_url.__get__(driver)
    driver.login = force_login.__get__(driver)
    # driver.maximize_window()
    # driver.fullscreen_window()

    yield driver


@pytest.fixture()
def logged_in_browser(browser: "SmartDriver", user):
    from testutils.utils import force_login

    dim = browser.get_window_size()

    browser.implicitly_wait(SELENIUM_DEFAULT_IMPLICITLY_WAIT)
    browser.set_page_load_timeout(SELENIUM_DEFAULT_PAGE_LOAD_TIMEOUT)
    browser.set_script_timeout(SELENIUM_DEFAULT_SCRIPT_TIMEOUT)

    browser.set_window_size(1100, dim["height"])
    browser.user = user

    force_login(browser, user, browser.live_server.url)

    return browser


def superuser(db):
    from testutils.factories import SuperUserFactory

    return SuperUserFactory(username="superuser")
