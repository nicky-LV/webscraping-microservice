from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains

import requests
import time
import os

# Current working dir
current_dir = os.path.dirname(os.path.abspath(__file__))
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")


def university_is_valid(university_name, confirm_cookies=False):
    """
    We scrape through possible UK universities to check which we can scrape accommodation data from.
    :return: str[], list of university names
    """
    selenium_driver = webdriver.Remote("http://selenium:4444/wd/hub", options=chrome_options)
    selenium_driver.get("https://www.studentcrowd.com/")
    time.sleep(1)

    if confirm_cookies:
        confirm_cookie_settings(driver=selenium_driver)

    # Input university name into searchbar
    input_searchbar(driver=selenium_driver, input_text=university_name)
    time.sleep(0.5)
    submit_searchbar(driver=selenium_driver)
    time.sleep(1)

    # Check that the university is valid and we can scrape data from it.
    if university_in_title(selenium_driver, university_name):
        return university_name, selenium_driver.current_url

    return None, None


def input_searchbar(driver, input_text: str) -> None:
    """
    Inputs text into the searchbar
    :param driver: instance - driver instance.
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
    :param driver: instance - driver instance.
    :return: None
    """
    driver.find_element_by_id("search-form__btn-submit").click()


def university_in_title(driver, university_name: str) -> bool:
    """
    Checks that university is in the title of the webpage.
    :param driver: instance - driver instance.
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
    :return: None
    """
    selenium_driver = webdriver.Remote("http://selenium:4444/wd/hub", options=chrome_options)
    wait = WebDriverWait(selenium_driver, 3)
    try:
        # Confirm cookie settings.
        cookie_button = wait.until(ec.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler")))
        if cookie_button:
            ActionChains(driver).click(cookie_button).perform()

    except TimeoutException:
        pass


def get_accommodation_name(driver):
    """
    Returns name of accommodation.
    :param driver: instance - driver instance.
    :return: str - accommodation name.
    """
    return driver.find_element_by_css_selector(".cl span").text


def get_accommodation_data(accommodation_url: str):
    """
    Returns accommodation data - such as telephone, postcode, weekly_price, etc.
    :param driver: instance - driver instance.
    :return:
    """
    selenium_driver = webdriver.Remote("http://selenium:4444/wd/hub", options=chrome_options)
    # Go to accommodation page
    selenium_driver.get(accommodation_url)

    data = {
        "name": get_accommodation_name(driver=selenium_driver)
    }

    # Select all table DOM elements
    tables = selenium_driver.find_elements_by_css_selector("table")

    # Filter table DOM elements to get table filled with accomm_page information
    info_table = None
    if tables:
        for element in tables:
            if element.get_attribute("itemprop") == "location":
                info_table = element

        table_rows = info_table.find_element_by_css_selector("tbody").find_elements_by_css_selector("tr")
        for row in table_rows:
            key_element, value_element = row.find_elements_by_css_selector("td")
            attrs = ["Telephone", "Postcode", "Price from", "Catering"]
            if key_element.text in attrs:
                # Conditional to transform the "Price from" key into "weekly_cost"
                if key_element.text == "Price from":
                    data["weekly_cost"] = value_element.text

                else:
                    data[key_element.text.lower()] = value_element.text

        return data


def get_university_accommodation_urls(university_url: str):
    """
    Returns the url of each accommodation to a university.
    :param driver: instance - driver instance.
    :return: str[] - list of URLs which correspond to the accommodations of a specific valid university.
    """
    selenium_driver = webdriver.Remote("http://selenium:4444/wd/hub", options=chrome_options)
    selenium_driver.get(url=university_url)
    accommodation_urls = []
    # Selects all h4 elements on the page.
    all_h4_elements = selenium_driver.find_elements_by_css_selector("h4")

    # Loops through each h4 element.
    for h4_element in all_h4_elements:
        # Checks if that h4 element has an anchor tag.
        child_link = h4_element.find_element_by_css_selector("a")
        if child_link:
            # If that anchor tag has "Hall Rankings" in the text, we click it to redirect to the halls ranking page.
            if "Hall Rankings" in child_link.text:
                child_link.click()
                break

    # Exclude private accommodations from datapool
    selenium_driver.find_element_by_class_name("js-hall-type-filter").click()
    time.sleep(0.5)

    # Gets all table items which *could* be halls accommodation.
    table_item = selenium_driver.find_elements_by_css_selector("a.js-hall-table-item")
    for possible_halls in table_item:
        # Checks if the "data-halls-type" is equal to "uni". If so, it is owned by the uni and is a hall.
        if possible_halls.get_attribute("data-hall-type") == "uni":
            # Redirect to the halls information page
            halls_url = possible_halls.get_attribute("href")
            accommodation_urls.append(halls_url)

    return accommodation_urls
