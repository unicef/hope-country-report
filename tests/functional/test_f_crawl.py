import pytest

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from testutils.perms import user_grant_permissions
from testutils.selenium import SmartDriver


@pytest.fixture()
def afghanistan(db):
    from testutils.factories import CountryOfficeFactory

    return CountryOfficeFactory(name="Afghanistan")


@pytest.fixture()
def afg_user(user, afghanistan):
    grant = user_grant_permissions(user, [], afghanistan)
    grant.start()
    yield user
    grant.stop()


@pytest.fixture()
def no_roles_user(user):
    return user


@pytest.mark.selenium
def test_no_co_available(browser: "SmartDriver", no_roles_user):
    """user without any roles will not have any CO available"""
    dim = browser.get_window_size()
    browser.set_window_size(1100, dim["height"])

    browser.go("/")

    browser.find_element(By.NAME, "username").send_keys(no_roles_user.username)
    browser.find_element(By.NAME, "password").send_keys(no_roles_user._password)
    browser.find_element(By.TAG_NAME, "button").click()

    browser.wait_for(By.NAME, "tenant")
    with pytest.raises(NoSuchElementException):
        browser.find_element(By.CSS_SELECTOR, "select.tenant option")


@pytest.mark.selenium
def test_access(browser: "SmartDriver", afg_user):
    """user can access only allowe CO"""
    dim = browser.get_window_size()
    browser.set_window_size(1100, dim["height"])

    browser.go("/")

    browser.find_element(By.NAME, "username").send_keys(afg_user.username)
    browser.find_element(By.NAME, "password").send_keys(afg_user._password)
    browser.find_element(By.TAG_NAME, "button").click()

    select = Select(browser.wait_for(By.NAME, "tenant"))

    options = browser.find_elements(By.XPATH, "//select[@name='tenant']/option")
    assert len(options) == 2
    select.select_by_visible_text("Afghanistan")

    browser.wait_for_url("/afghanistan/")
