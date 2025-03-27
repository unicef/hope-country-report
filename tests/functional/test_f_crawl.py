from typing import TYPE_CHECKING

import pytest

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from testutils.selenium import SmartDriver

from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice, User
    from hope_country_report.apps.power_query.models import ReportConfiguration, ReportDocument


@pytest.fixture
def afghanistan(transactional_db) -> "CountryOffice":
    from testutils.factories import CountryOfficeFactory

    return CountryOfficeFactory(name="Afghanistan")


#
# @pytest.fixture()
# def afg_user(user, afghanistan):
#     grant = user_grant_permissions(
#         user, ["power_query.view_reportconfiguration", "power_query.view_reportdocument"], afghanistan
#     )
#     grant.start()
#     yield user
#     grant.stop()


@pytest.fixture
def no_roles_user(user):
    return user


@pytest.fixture
def report_document(afghanistan, afg_user):
    from testutils.factories import HouseholdFactory, QueryFactory, ReportConfigurationFactory

    with state.set(must_tenant=False, tenant=afghanistan):
        ba = afghanistan.business_area
        HouseholdFactory(business_area=ba, withdrawn=True)
        HouseholdFactory(business_area=ba, withdrawn=False)
        query1 = QueryFactory(owner=afg_user)
        query1.execute_matrix()
        r: "ReportConfiguration" = ReportConfigurationFactory(
            name="Housholds", title="Households #0", owner=afg_user, query=query1, country_office=afghanistan
        )
        r.tags.add("tag1", "tag2")
        r.execute()
    return r.documents.first()


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
def test_login(browser: "SmartDriver", afg_user):
    """user can access only allows CO"""
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
def test_report_list(browser: "SmartDriver", report_document: "ReportDocument"):
    # browser.go("/")
    # browser.login(report_document.report.owner, report_document.country_office)
    # browser.go("/afghanistan/")
    config: ReportConfiguration = report_document.report
    user: User = config.owner

    browser.go("/")

    browser.find_element(By.NAME, "username").send_keys(user.username)
    browser.find_element(By.NAME, "password").send_keys("password")
    browser.find_element(By.TAG_NAME, "button").click()

    select = Select(browser.wait_for(By.NAME, "tenant"))
    select.select_by_visible_text("Afghanistan")

    browser.wait_for(By.LINK_TEXT, "Reports").click()
    browser.wait_for_url("/afghanistan/docs/")
    browser.wait_for(By.LINK_TEXT, "tag1").click()
    browser.wait_for(By.ID, "remove-filter").click()

    browser.wait_for(By.LINK_TEXT, report_document.title).click()
    browser.wait_for_url(f"/afghanistan/doc/{report_document.pk}/")
    assert browser.find_element(By.XPATH, "//div[@class='box']/h1").text == report_document.title


@pytest.mark.selenium
def test_report_config(browser: "SmartDriver", report_document: "ReportDocument"):
    config: ReportConfiguration = report_document.report
    user: User = config.owner
    # browser.go("/")
    # browser.login(config.owner)
    # browser.go("/afghanistan/")

    browser.go("/")

    browser.find_element(By.NAME, "username").send_keys(user.username)
    browser.find_element(By.NAME, "password").send_keys("password")
    browser.find_element(By.TAG_NAME, "button").click()

    select = Select(browser.wait_for(By.NAME, "tenant"))
    select.select_by_visible_text("Afghanistan")

    browser.wait_for(By.LINK_TEXT, "Settings").click()
    browser.wait_for_url("/afghanistan/configurations/")
    browser.wait_for(By.LINK_TEXT, "tag1").click()
    browser.wait_for(By.ID, "remove-filter").click()

    browser.wait_for(By.LINK_TEXT, config.title).click()
    browser.wait_for_url(f"/afghanistan/configuration/{config.pk}/")
    assert browser.find_element(By.XPATH, "//div[@class='box']/h1").text == config.title
