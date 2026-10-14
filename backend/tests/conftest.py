"""Shared fixtures. The API tests run against a real MongoDB, in a separate test database."""

import os

# Must be set before any `app` module is imported, so the app connects to the test database.
os.environ["MONGO_DB"] = "job_radar_test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from pymongo import MongoClient  # noqa: E402
from pymongo.errors import ServerSelectionTimeoutError  # noqa: E402

from app.db import MONGO_URL  # noqa: E402


@pytest.fixture(scope="session")
def mongo():
    """A plain (synchronous) client for preparing and checking data. Skips API tests if MongoDB isn't running."""
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command("ping")
    except ServerSelectionTimeoutError:
        pytest.skip("MongoDB is not running (start it with `docker compose up -d`)")
    yield client["job_radar_test"]
    client.drop_database("job_radar_test")
    client.close()


@pytest.fixture(scope="session")
def api(mongo):
    """One API client for the whole session; entering it runs the app's startup (indexes)."""
    from app.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture()
def db(mongo):
    """An empty test database for every test."""
    for name in ("jobs", "companies", "job_details", "hidden_jobs", "favorites"):
        mongo[name].delete_many({})
    return mongo


def make_job(job_id: str, title: str, published_at: str, **fields) -> dict:
    """A job document as the scanner stores it."""
    return {
        "_id": job_id,
        "id": job_id,
        "title": title,
        "company": fields.pop("company", "Acme"),
        "location": fields.pop("location", "Tel Aviv, Israel"),
        "url": f"https://example.com/{job_id}",
        "source": job_id.split(":", 1)[0],
        "published_at": published_at,
        "updated_at": published_at,
        "is_israel": True,
        "category": fields.pop("category", "software"),
        **fields,
    }
