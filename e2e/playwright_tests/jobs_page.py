from playwright.sync_api import Page


class JobsPage:
    def __init__(self, page: Page):
        self.page = page
        self.error = page.get_by_test_id("jobs-error")
        self.retry_button = page.get_by_test_id("retry-button")
        self.cards = page.get_by_test_id("job-card")
        self.titles = page.get_by_test_id("job-card-link")

    def open(self):
        self.page.goto("/jobs")
        return self

    def card(self, title: str):
        return self.cards.filter(has=self.page.get_by_test_id("job-card-link").get_by_text(title, exact=True))

    def toggle_card(self, title: str):
        self.card(title).locator(".summary p").click()
