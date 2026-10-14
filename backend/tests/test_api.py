"""API tests: every endpoint through HTTP, against a real MongoDB test database."""

from urllib.parse import quote

import httpx
import pytest

from app.models import Job
from app.providers import DETAIL_FETCHERS, greenhouse
from tests.conftest import make_job

QA = make_job("greenhouse:acme:1", "QA Automation Engineer", "2026-10-10T09:00:00Z", category="qa")
BACKEND = make_job("greenhouse:acme:2", "Senior Backend Engineer", "2026-10-12T09:00:00Z", category="backend")
FULLSTACK = make_job("comeet:beta/A1.001:7", "Full Stack Developer", "2026-10-11T09:00:00Z", category="fullstack")
CPP = make_job("lever:gamma:3", "C++ Developer (Senior)", "2026-10-01T09:00:00Z", category="software")
WORKDAY = make_job(
    "workday:wd1/delta/Careers:/job/Haifa/QA-Lead_R123", "QA Lead", "2026-09-01T09:00:00Z", category="qa"
)
ALL_JOBS = [QA, BACKEND, FULLSTACK, CPP, WORKDAY]


@pytest.fixture()
def jobs(db):
    db.jobs.insert_many([dict(job) for job in ALL_JOBS])
    return db


def titles(response) -> list[str]:
    return [item["title"] for item in response.json()["items"]]


# ---------- health ----------

def test_health(api):
    response = api.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------- GET /jobs ----------

def test_jobs_are_newest_first(api, jobs):
    response = api.get("/jobs")

    assert response.status_code == 200
    assert titles(response) == [
        "Senior Backend Engineer",  # Oct 12
        "Full Stack Developer",  # Oct 11
        "QA Automation Engineer",  # Oct 10
        "C++ Developer (Senior)",  # Oct 1
        "QA Lead",  # Sep 1
    ]


def test_jobs_response_uses_camel_case(api, jobs):
    item = api.get("/jobs").json()["items"][0]

    assert {"publishedAt", "updatedAt", "isIsrael", "category"} <= item.keys()
    assert "published_at" not in item
    assert "_id" not in item


def test_jobs_pagination(api, jobs):
    first = api.get("/jobs", params={"page": 1, "page_size": 2}).json()
    third = api.get("/jobs", params={"page": 3, "page_size": 2}).json()

    assert first["total"] == 5
    assert (first["page"], first["pageSize"]) == (1, 2)
    assert [i["title"] for i in first["items"]] == ["Senior Backend Engineer", "Full Stack Developer"]
    assert [i["title"] for i in third["items"]] == ["QA Lead"]


def test_page_past_the_end_is_empty(api, jobs):
    body = api.get("/jobs", params={"page": 99}).json()

    assert body["items"] == []
    assert body["total"] == 5


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page": -1},
        {"page_size": 0},
        {"page_size": 101},  # nobody may download the whole database in one request
        {"page": "abc"},
        {"category": "not-a-category"},
    ],
)
def test_invalid_query_parameters_return_422(api, jobs, params):
    assert api.get("/jobs", params=params).status_code == 422


@pytest.mark.parametrize(
    ("search", "expected"),
    [
        ("qa", ["QA Automation Engineer", "QA Lead"]),
        ("ENGINEER", ["Senior Backend Engineer", "QA Automation Engineer"]),  # case-insensitive
        ("senior", ["Senior Backend Engineer", "C++ Developer (Senior)"]),
        ("C++", ["C++ Developer (Senior)"]),  # regex characters are matched literally
        ("(Senior)", ["C++ Developer (Senior)"]),
        ("no such job", []),
    ],
)
def test_search_by_title(api, jobs, search, expected):
    response = api.get("/jobs", params={"search": search})

    assert response.status_code == 200
    assert titles(response) == expected
    assert response.json()["total"] == len(expected)


def test_filter_by_one_category(api, jobs):
    response = api.get("/jobs", params={"category": "qa"})

    assert titles(response) == ["QA Automation Engineer", "QA Lead"]


def test_filter_by_several_categories(api, jobs):
    response = api.get("/jobs", params=[("category", "qa"), ("category", "fullstack")])

    assert titles(response) == ["Full Stack Developer", "QA Automation Engineer", "QA Lead"]


def test_search_and_category_combine(api, jobs):
    response = api.get("/jobs", params={"search": "lead", "category": "qa"})

    assert titles(response) == ["QA Lead"]


# ---------- GET /jobs/categories ----------

def test_category_counts(api, jobs):
    counts = {row["category"]: row["count"] for row in api.get("/jobs/categories").json()}

    assert counts == {"qa": 2, "backend": 1, "fullstack": 1, "software": 1}


def test_category_counts_follow_the_search(api, jobs):
    counts = {row["category"]: row["count"] for row in api.get("/jobs/categories", params={"search": "senior"}).json()}

    assert counts == {"backend": 1, "software": 1}


def test_category_counts_are_sorted_by_size(api, jobs):
    rows = api.get("/jobs/categories").json()

    assert rows[0] == {"category": "qa", "count": 2}


# ---------- GET /jobs/{id} ----------

def test_get_one_job(api, jobs):
    response = api.get(f"/jobs/{QA['_id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "QA Automation Engineer"


def test_get_job_whose_id_contains_slashes(api, jobs):
    response = api.get(f"/jobs/{quote(WORKDAY['_id'], safe='')}")

    assert response.status_code == 200
    assert response.json()["title"] == "QA Lead"


def test_unknown_job_is_404(api, jobs):
    response = api.get("/jobs/greenhouse:acme:999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


# ---------- GET /jobs/{id}/details ----------

def test_details_come_from_the_cache(api, jobs):
    jobs.job_details.insert_one({
        "_id": QA["_id"],
        "job_updated_at": QA["updated_at"],
        "details": {
            "content": "<p>Write Playwright tests</p>",
            "departments": ["R&D"],
            "fields": [{"name": "Workplace", "value": "Hybrid"}],
        },
    })

    response = api.get(f"/jobs/{QA['_id']}/details")

    assert response.status_code == 200
    assert response.json() == {
        "content": "<p>Write Playwright tests</p>",
        "departments": ["R&D"],
        "fields": [{"name": "Workplace", "value": "Hybrid"}],
    }


def test_details_of_unknown_job_is_404(api, jobs):
    assert api.get("/jobs/greenhouse:acme:999/details").status_code == 404


def test_details_of_a_closed_posting_is_404(api, jobs, monkeypatch):
    async def closed(*args):
        request = httpx.Request("GET", "https://boards-api.greenhouse.io")
        raise httpx.HTTPStatusError("gone", request=request, response=httpx.Response(404, request=request))

    monkeypatch.setitem(DETAIL_FETCHERS, "greenhouse", closed)

    response = api.get(f"/jobs/{QA['_id']}/details")

    assert response.status_code == 404
    assert response.json()["detail"] == "This job is no longer on the company's site"


# ---------- POST /scan/greenhouse/{board} ----------

def scanned_job(native_id: str, title: str, location: str) -> Job:
    return greenhouse.to_job(
        {
            "id": native_id,
            "title": title,
            "company_name": "Acme",
            "location": {"name": location},
            "absolute_url": f"https://example.com/{native_id}",
            "first_published": "2026-10-13T09:00:00Z",
            "updated_at": "2026-10-13T09:00:00Z",
        },
        "acme",
    )


def test_scan_saves_israeli_jobs_and_deletes_closed_ones(api, jobs, monkeypatch):
    # acme's board now has job 2 (still open), a new job 10 in Haifa and a job in London; job 1 was closed.
    board = [
        scanned_job("2", "Senior Backend Engineer", "Tel Aviv"),
        scanned_job("10", "QA Engineer", "Haifa"),
        scanned_job("11", "Account Executive", "London"),
    ]

    async def fake_fetch_jobs(client, company):
        return board

    monkeypatch.setattr(greenhouse, "fetch_jobs", fake_fetch_jobs)

    response = api.post("/scan/greenhouse/acme")

    assert response.status_code == 200
    assert response.json() == {"saved": 2, "removed": 1}
    stored = {doc["_id"] for doc in jobs.jobs.find({"_id": {"$regex": "^greenhouse:acme:"}})}
    assert stored == {"greenhouse:acme:2", "greenhouse:acme:10"}  # London never stored, job 1 deleted
    # Other companies' jobs are untouched.
    assert jobs.jobs.count_documents({}) == 5


def test_scan_of_unknown_company_is_404(api, jobs, monkeypatch):
    async def not_found(client, company):
        request = httpx.Request("GET", "https://boards-api.greenhouse.io")
        raise httpx.HTTPStatusError("missing", request=request, response=httpx.Response(404, request=request))

    monkeypatch.setattr(greenhouse, "fetch_jobs", not_found)

    response = api.post("/scan/greenhouse/no-such-company")

    assert response.status_code == 404
    assert response.json() == {"detail": "Company not found"}
    assert jobs.jobs.count_documents({}) == 5  # nothing deleted


# ---------- DELETE /jobs/{id} and restore ----------

def test_removed_job_disappears_from_the_list(api, jobs):
    response = api.delete(f"/jobs/{QA['_id']}")

    assert response.status_code == 204
    assert "QA Automation Engineer" not in titles(api.get("/jobs"))
    assert api.get(f"/jobs/{QA['_id']}").status_code == 404


def test_removing_an_unknown_job_is_404(api, jobs):
    assert api.delete("/jobs/greenhouse:acme:999").status_code == 404


def test_a_removed_job_can_be_restored(api, jobs):
    api.delete(f"/jobs/{QA['_id']}")

    response = api.post(f"/jobs/{QA['_id']}/restore")

    assert response.status_code == 200
    assert "QA Automation Engineer" in titles(api.get("/jobs"))


def test_scan_does_not_bring_back_a_removed_job(api, jobs, monkeypatch):
    api.delete("/jobs/greenhouse:acme:2")
    board = [scanned_job("2", "Senior Backend Engineer", "Tel Aviv"), scanned_job("10", "QA Engineer", "Haifa")]

    async def fake_fetch_jobs(client, company):
        return board

    monkeypatch.setattr(greenhouse, "fetch_jobs", fake_fetch_jobs)

    response = api.post("/scan/greenhouse/acme")

    assert response.json()["saved"] == 1
    assert jobs.jobs.count_documents({"_id": "greenhouse:acme:2"}) == 0


# ---------- favorites ----------

def api_job_fields(document: dict) -> dict:
    return {
        "id": document["_id"], "title": document["title"], "company": document["company"],
        "location": document["location"], "url": document["url"], "source": document["source"],
        "publishedAt": document["published_at"], "updatedAt": document["updated_at"],
        "isIsrael": document["is_israel"], "category": document["category"],
    }


def star(api, document):
    return api.put(f"/favorites/{quote(document['_id'], safe='')}", json=api_job_fields(document))


def test_starred_jobs_are_listed_newest_star_first(api, jobs):
    star(api, QA)
    star(api, BACKEND)

    favorites = api.get("/favorites").json()

    assert [job["title"] for job in favorites] == ["Senior Backend Engineer", "QA Automation Engineer"]


def test_unstarring_removes_from_favorites(api, jobs):
    star(api, QA)

    assert api.delete(f"/favorites/{QA['_id']}").status_code == 204
    assert api.get("/favorites").json() == []


def test_star_body_must_match_the_url(api, jobs):
    response = api.put(f"/favorites/{QA['_id']}", json=api_job_fields(BACKEND))

    assert response.status_code == 422


def test_hide_favorites_leaves_starred_jobs_out_of_the_list_and_counts(api, jobs):
    star(api, QA)
    star(api, WORKDAY)

    shown = api.get("/jobs").json()
    hidden = api.get("/jobs", params={"hide_favorites": True}).json()
    counts = {r["category"]: r["count"] for r in api.get("/jobs/categories", params={"hide_favorites": True}).json()}

    assert shown["total"] == 5
    assert [item["title"] for item in hidden["items"]] == [
        "Senior Backend Engineer", "Full Stack Developer", "C++ Developer (Senior)",
    ]
    assert hidden["total"] == 3
    assert "qa" not in counts

