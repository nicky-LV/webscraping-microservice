import unittest
import pytest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from webscraping_engine.utils import WebscrapingUtils


@pytest.fixture
def engine():
    return WebscrapingUtils()


def test_shutdown(engine) -> None:
    engine.quit()


def test_scraping_accommodation_names(engine):
    accommodation_urls = engine.get_accommodation_urls(
        university_url="https://www.studentcrowd.com/university-l1003919-s1008319-the_university_of_liverpool-liverpool")

    for accomm_url in accommodation_urls:
        # Navigate to accommodation page
        engine.selenium_driver.get(accomm_url)

        # Retrieve accommodation name
        accomm_name = engine.get_accommodation_name()
        if accomm_name is None:
            raise TypeError("accomm_name is None")


def test_scraping_accommodation_picture(engine):
    test_accommodation_url = \
        "https://www.studentcrowd.com/hall-l1005196-s1044625-rees-hall-university_of_portsmouth-portsmouth#booking"
    engine.get(url=test_accommodation_url)
    src = engine.get_accommodation_picture()
    assert src == "https://media.studentcrowd.net/w426-h284-q70-cfill/20170905-1044625.jpg"