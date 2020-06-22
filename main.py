#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import config as cfg
import os
import sys
import subprocess
import time
import random

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# By 'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 'PARTIAL_LINK_TEXT', 'TAG_NAME', 'XPATH'


class TenBis(object):
    def __init__(self, driver):
        self.driver = driver
        self.tenbis_address = "https://10bis.co.il"
        # Get 10bis username and password and chosen restaurant
        self.tenbis_username = cfg.tenbis["username"]
        self.tenbis_password_id = cfg.tenbis["passwordId"]
        self.tenbis_password = subprocess.check_output(
            ["/usr/local/bin/lpass", "show", self.tenbis_password_id, "--password"]).strip().decode('UTF-8')
        self.chosen_restaurant = cfg.tenbis["restaurantsDetails"][cfg.tenbis["chosenRestaurant"]]
        self.chosen_restaurant_url = self.chosen_restaurant["url"]

        # select random dish or the first of the favorite if random is turned off
        if self.chosen_restaurant["randomizeDish"]:
            self.selectedDish = random.choice(
                self.chosen_restaurant["favoriteDishes"])
        else:
            self.selectedDish = self.chosen_restaurant["favoriteDish"][0]

        self.address_substring = cfg.tenbis["addressSubstring"]

        # Define screenshots dir and create it
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.screenshot_path = os.path.join(
            os.path.sep, ROOT_DIR, 'Screenshots')
        if not os.path.exists(self.screenshot_path):
            os.mkdir(self.screenshot_path)

    def _wait_for_loader_to_disappear(self):
        WebDriverWait(self.driver, 20).until(EC.invisibility_of_element(
            (By.XPATH, "//div[contains(@class, 'CentralLoading')]")))

    def _normalize_file_name(self, file_name):
        if file_name.endswith(".jpg") or file_name.endswith(".png"):
            file_name = file_name[0:-4]

        return f"{file_name}.png"

    def take_screenshot(self, file_name):
        normalized_file_name = self._normalize_file_name(file_name)
        print(
            f"Taking screenshot and saving in {self.screenshot_path}/{normalized_file_name}")
        self.driver.get_screenshot_as_file(self.screenshot_path + file_name)

    def order_from_10bis(self):
        # Go to the website
        self.driver.get(self.tenbis_address)

        # Login
        self.driver.find_element_by_css_selector(
            "[data-test='homeHeader-openLogin']").click()
        self.driver.find_element_by_id("email").send_keys(self.tenbis_username)
        self.driver.find_element_by_id(
            "password").send_keys(self.tenbis_password)
        self.driver.find_element_by_css_selector("[type='submit']").click()

        # Change address
        self._wait_for_loader_to_disappear()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class, 'AddressDropdown')]"))).click()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(text(), '{self.address_substring}')]"))).click()

        # Choose restaurant
        try:
            self._wait_for_loader_to_disappear()
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-test="restaurant-item"]')))
            self.driver.get(self.chosen_restaurant_url)
        except Exception as err:
            print(f"Could not choose restaurant {self.chosen_restaurant}")
            print(err)
            raise

        # Choose dish
        self._wait_for_loader_to_disappear()
        try:
            self.driver.find_element_by_xpath(
                f"//span[contains(text(), '{self.selectedDish}')]").click()
            self.driver.find_element_by_xpath(
                "//button[contains(@class, 'CartButton')]").click()
            time.sleep(10)
        except Exception as err:
            print(f"Could not select dish {self.selectedDish}")
            print(err)
            raise

        # Payment
        self._wait_for_loader_to_disappear()
        final_price = driver.find_element_by_xpath(
            "//div[contains(text(), 'סך כל ההזמנה')]//div[not(@class)]").get_attribute("innerHTML")
        print(f"Final Price: {final_price}")
        self.take_screenshot("final_stage.png")
        print("Payment is done here")
        # self.driver.find_element_by_xpath(
        #     "//button[contains(@class, 'PaymentActionButton')]").click()


if __name__ == "__main__":
    # Initialization
    driver = webdriver.Firefox()
    # firefox_options = webdriver.FirefoxOptions()
    # driver = webdriver.Remote(
    #     command_executor='http://localhost:4444/wd/hub',
    #     options=firefox_options
    # )
    tenbis = TenBis(driver)
    try:
        tenbis.order_from_10bis()
        tenbis.take_screenshot("final_stage.png")
        time.sleep(50)
    finally:
        driver.quit()
