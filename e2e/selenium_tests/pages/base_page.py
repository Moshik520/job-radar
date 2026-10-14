from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 10


def by_test_id(test_id: str) -> tuple[str, str]:
    return By.CSS_SELECTOR, f'[data-testid="{test_id}"]'


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUT)

    def open(self, path: str):
        self.driver.get(self.driver.base_url + path)
        return self

    def find(self, test_id: str):
        return self.wait.until(EC.visibility_of_element_located(by_test_id(test_id)))

    def find_all(self, test_id: str):
        return self.driver.find_elements(*by_test_id(test_id))

    def click(self, test_id: str):
        self.wait.until(EC.element_to_be_clickable(by_test_id(test_id))).click()
