from selenium import webdriver
import requests
import time
import os


def university_is_valid(university_name, retries=5):
    """
    We scrape through possible UK universities to check which we can scrape accommodation data from.
    :return: str[], list of university names
    """

    driver = webdriver.Chrome(executable_path="./chromedriver")
    driver.get("https://www.studentcrowd.com/")
    confirm_cookie_settings(driver)

    # Input university name into searchbar
    input_searchbar(driver=driver, input_text=university_name)
    time.sleep(0.5)
    submit_searchbar(driver=driver)
    time.sleep(1)

    # Check that the university is valid and we can scrape data from it.
    if retries > 0:
        if university_in_title(driver, university_name):
            return True

        else:
            return university_is_valid(university_name=university_name, retries=retries-1)

    else:
        return False


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
    # Confirm cookie settings.
    driver.find_element_by_id("onetrust-accept-btn-handler").click()
