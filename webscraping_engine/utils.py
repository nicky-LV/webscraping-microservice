from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

import requests
import time
import os

# Current working dir
current_dir = os.path.dirname(os.path.abspath(__file__))
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=f"{current_dir}/chromedriver", options=chrome_options)
wait = WebDriverWait(driver, 3)


def university_is_valid(university_name, confirm_cookies=False):
    """
    We scrape through possible UK universities to check which we can scrape accommodation data from.
    :return: str[], list of university names
    """
    driver.get("https://www.studentcrowd.com/")
    time.sleep(1)

    if confirm_cookies:
        confirm_cookie_settings(driver)

    # Input university name into searchbar
    input_searchbar(driver=driver, input_text=university_name)
    time.sleep(0.5)
    submit_searchbar(driver=driver)
    time.sleep(1)

    # Check that the university is valid and we can scrape data from it.
    if university_in_title(driver, university_name):
        return university_name, driver.current_url

    return None, None


def input_searchbar(driver, input_text: str) -> None:
    """
    Inputs text into the searchbar
    :param driver: object - driver object
    :param input_text: str - input text
    :return: None
    """
    # Populate searchbar
    searchbar = driver.find_element_by_class_name("search-box__input")
    searchbar.clear()
    searchbar.send_keys(input_text)


def submit_searchbar(driver) -> None:
    """
    Submits searchbar by pressing on submit button.
    :param driver: driver object.
    :return: None
    """
    driver.find_element_by_id("search-form__btn-submit").click()


def university_in_title(driver, university_name: str) -> bool:
    """
    Checks that university is in the title of the webpage.
    :param driver: object - driver object
    :param university_name: str - university name
    :return: bool
    """
    if university_name in driver.title:
        return True

    return False


def get_latitude_longitude_from_postcode(postcode: str) -> tuple:
    """
    Returns latitude and longitude from postcode
    :param postcode: str - postcode of accommodation. e.g. "L14 9VC"
    :return: (latitude, longitude)
    """
    data = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={postcode}&key={os.getenv('GEOCODING_API_KEY')}").json()
    location_data = data['results'][0]['geometry']['location']
    latitude, longitude = location_data['lat'], location_data['lng']

    return latitude, longitude


def confirm_cookie_settings(driver) -> None:
    """
    Presses confirmation button on "confirm cookie popup".
    :param driver: object - driver object
    :return: None
    """
    try:
        # Confirm cookie settings.
        cookie_button = wait.until(ec.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler")))
        if cookie_button:
            cookie_button.click()

    except TimeoutException:
        pass
