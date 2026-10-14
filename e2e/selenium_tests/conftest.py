import os

import pytest
from selenium import webdriver


@pytest.fixture
def driver(base_url):
    options = webdriver.ChromeOptions()
    if os.getenv("HEADED") != "1":  # HEADED=1 pytest ... to watch the browser
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    browser = webdriver.Chrome(options=options)  # Selenium Manager finds the matching driver
    browser.base_url = base_url
    yield browser
    browser.quit()
