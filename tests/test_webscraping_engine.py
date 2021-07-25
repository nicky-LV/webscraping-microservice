import unittest
import pytest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class WebscrapingEngine:
    """
    NOTE: Must be ran once dockerized. This will not pass on localhost.
    """
    def __init__(self):
        # Tests startup of webdriver.
        self.driver = webdriver.Remote("http://selenium:4444/wd/hub", DesiredCapabilities.CHROME)

    def test_shutdown(self):
        self.driver.quit()


@pytest.fixture
def webscraping_engine_instance():
    return WebscrapingEngine()


def test_shutdown(webscraping_engine_instance):
    webscraping_engine_instance.test_shutdown()
