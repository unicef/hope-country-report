from typing import TYPE_CHECKING

import pytest

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from testutils.perms import user_grant_permissions
from testutils.selenium import SmartDriver

from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import Report


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


@pytest.fixture()
def report(afghanistan, afg_user):
    from testutils.factories import HouseholdFactory, QueryFactory, ReportFactory

    with state.set(must_tenant=False, tenant=afghanistan):
        ba = afghanistan.business_area
        HouseholdFactory(business_area=ba, withdrawn=True)
        HouseholdFactory(business_area=ba, withdrawn=False)
        query1 = QueryFactory(owner=afg_user)
        query1.execute_matrix()
        r = ReportFactory(name="Housholds", owner=afg_user, query=query1, country_office=afghanistan)
        r.execute()
    return r


@pytest.mark.selenium
def test_no_co_available(browser: "SmartDriver", no_roles_user):
    """user without any roles will not have any CO available"""
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
    browser.go("/")

    browser.find_element(By.NAME, "username").send_keys(afg_user.username)
    browser.find_element(By.NAME, "password").send_keys(afg_user._password)
    browser.find_element(By.TAG_NAME, "button").click()

    select = Select(browser.wait_for(By.NAME, "tenant"))

    options = browser.find_elements(By.XPATH, "//select[@name='tenant']/option")
    assert len(options) == 2
    select.select_by_visible_text("Afghanistan")

    browser.wait_for_url("/afghanistan/")


@pytest.mark.selenium
def test_report_list(browser: "SmartDriver", report: "Report"):
    browser.go("/")

    browser.find_element(By.NAME, "username").send_keys(report.owner.username)
    browser.find_element(By.NAME, "password").send_keys(report.owner._password)
    browser.find_element(By.TAG_NAME, "button").click()

    select = Select(browser.wait_for(By.NAME, "tenant"))

    options = browser.find_elements(By.XPATH, "//select[@name='tenant']/option")
    assert len(options) == 2
    select.select_by_visible_text("Afghanistan")

    browser.wait_for_url("/afghanistan/")
    browser.wait_for(By.LINK_TEXT, "Reports").click()
    browser.wait_for_url("/afghanistan/reports")
    browser.save_screenshot("a1.png")
    browser.wait_for(By.LINK_TEXT, report.name).click()
    browser.wait_for_url(f"/afghanistan/reports/{report.pk}/")

    browser.go(f"/afghanistan/reports/{report.pk}/")
