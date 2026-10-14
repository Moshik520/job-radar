from selenium.webdriver.common.by import By

from selenium_tests.pages.base_page import BasePage, by_test_id


class JobsPage(BasePage):
    def open(self):
        super().open("/jobs")
        self.find("results-count")
        return self

    # --- reading the page ---

    def results_count(self) -> str:
        return self.find("results-count").text

    def job_titles(self) -> list[str]:
        return [link.text for link in self.find_all("job-card-link")]

    def wait_for_titles(self, expected: list[str]) -> list[str]:
        """The list updates after a short debounce; wait until it shows the expected jobs."""
        self.wait.until(lambda _: self.job_titles() == expected)
        return self.job_titles()

    def card(self, title: str):
        for card in self.find_all("job-card"):
            if card.find_element(*by_test_id("job-card-link")).text == title:
                return card
        raise AssertionError(f"No job card titled {title!r}")

    def description(self, title: str) -> str:
        """The description inside an open card; it loads from the API after the card opens."""
        card = self.card(title)
        self.wait.until(lambda _: card.find_elements(*by_test_id("job-description")))
        return card.find_element(*by_test_id("job-description")).text

    def open_cards_count(self) -> int:
        return len([card for card in self.find_all("job-card") if card.get_attribute("aria-expanded") == "true"])

    # --- actions ---

    def search(self, text: str):
        box = self.find("search-input")
        box.clear()
        box.send_keys(text)
        return self

    def select_categories(self, *categories: str):
        self.click("category-filter-button")
        for category in categories:
            self.find(f"category-option-{category}").find_element(By.TAG_NAME, "input").click()
        self.click("category-filter-button")  # close the dropdown
        return self

    def toggle_card(self, title: str):
        """Click the card (not its title link, which opens the job page)."""
        self.card(title).find_element(By.CSS_SELECTOR, ".summary p").click()
        return self

    def collapse_all(self):
        self.click("collapse-all")
        return self
