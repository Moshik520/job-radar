from selenium_tests.pages.jobs_page import JobsPage


def test_jobs_are_listed_newest_first(driver):
    page = JobsPage(driver).open()

    assert page.job_titles() == [
        "QA Automation Engineer",
        "Senior Full Stack Developer",
        "Backend Engineer",
        "QA Engineer - Mobile",
        "Data Analyst",
        "Account Executive",
    ]
    assert "Showing 1–6 of 6 jobs" in page.results_count()


def test_search_by_title(driver):
    page = JobsPage(driver).open()

    page.search("qa")

    assert page.wait_for_titles(["QA Automation Engineer", "QA Engineer - Mobile"])
    assert "of 2 jobs" in page.results_count()


def test_filter_by_two_categories(driver):
    page = JobsPage(driver).open()

    page.select_categories("qa", "fullstack")

    assert page.wait_for_titles(["QA Automation Engineer", "Senior Full Stack Developer", "QA Engineer - Mobile"])
    assert page.find("category-filter-button").text.startswith("2 categories")


def test_open_a_card_then_collapse_all(driver):
    page = JobsPage(driver).open()

    page.toggle_card("QA Automation Engineer")
    assert "About the QA Automation Engineer role." in page.description("QA Automation Engineer")

    page.toggle_card("Backend Engineer")
    assert page.open_cards_count() == 2

    page.collapse_all()
    assert page.open_cards_count() == 0
