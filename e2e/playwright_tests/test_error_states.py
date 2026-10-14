"""States that are hard to reach with a real server, so the API responses are mocked with page.route."""

import re

from playwright.sync_api import Page, Route, expect

from playwright_tests.jobs_page import JobsPage

JOBS_LIST = re.compile(r".*/jobs\?.*")
DETAILS = re.compile(r".*/jobs/.+/details$")


def test_server_error_shows_retry_and_recovers(page: Page):
    calls = {"count": 0}

    def fail_first_time(route: Route):
        calls["count"] += 1
        if calls["count"] == 1:
            route.fulfill(status=500, body="Internal Server Error")
        else:
            route.continue_()

    page.route(JOBS_LIST, fail_first_time)
    jobs = JobsPage(page).open()

    expect(jobs.error).to_contain_text("couldn't load jobs")
    expect(jobs.cards).to_have_count(0)

    jobs.retry_button.click()

    expect(jobs.error).to_be_hidden()
    expect(jobs.cards).to_have_count(6)


def test_closed_job_shows_link_to_company_site(page: Page):
    page.route(DETAILS, lambda route: route.fulfill(
        status=404,
        content_type="application/json",
        body='{"detail": "This job is no longer on the company\'s site"}',
    ))
    jobs = JobsPage(page).open()

    jobs.toggle_card("Backend Engineer")

    error = jobs.card("Backend Engineer").get_by_test_id("job-details-error")
    expect(error).to_contain_text("Couldn't load the details")
    expect(error.get_by_role("link")).to_have_attribute("href", "https://example.com/jobs/3")
