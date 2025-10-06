from typing import TYPE_CHECKING

import pytest
from django.db import transaction
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

if TYPE_CHECKING:
    from testutils.selenium import SmartDriver

    from hope_country_report.apps.core.models import User


# @pytest.fixture()
# def afghanistan(db):
#     from testutils.factories import CountryOfficeFactory
#
#     return CountryOfficeFactory(name="Afghanistan")


@pytest.mark.selenium
def test_user_profile(browser: "SmartDriver", afg_user: "User"):
    browser.go("/")

    browser.find_element(By.NAME, "username").send_keys(afg_user.username)
    browser.find_element(By.NAME, "password").send_keys(afg_user._password)
    browser.find_element(By.TAG_NAME, "button").click()

    select = Select(browser.wait_for(By.NAME, "tenant"))
    select.select_by_visible_text("Afghanistan")

    browser.wait_for(By.CLASS_NAME, "profile-link").click()
    browser.wait_for_url(reverse("user-profile"))

    browser.select2("timezone", "Rome")

    select = Select(browser.wait_for(By.NAME, "language"))
    select.select_by_visible_text("Spanish")

    browser.find_element(By.TAG_NAME, "button").click()
    transaction.get_autocommit()
    transaction.on_commit(lambda: afg_user.refresh_from_db())
    # assert afg_user.language == "en"
    # assert afg_user.timezone.key == "UTC"
