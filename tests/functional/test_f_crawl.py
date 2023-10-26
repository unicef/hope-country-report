import pytest

from selenium.webdriver.common.by import By
from testutils.selenium import SmartDriver


@pytest.mark.selenium
def test_login_pwd_success(browser: "SmartDriver", user):
    browser.implicitly_wait(3)
    browser.get(f"{browser.live_server.url}/")
    dim = browser.get_window_size()
    browser.set_window_size(1100, dim["height"])

    browser.find_element(By.NAME, "username").send_keys(user.username)
    browser.find_element(By.NAME, "password").send_keys(user._password)
    browser.find_element(By.TAG_NAME, "button").click()

    browser.wait_for(By.NAME, "tenant")

    assert "/" in browser.current_url
