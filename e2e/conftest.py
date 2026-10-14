import os

import pytest
from pymongo import MongoClient

from test_data import DETAILS, JOBS

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
E2E_DB = "job_radar_e2e"  # the API on port 8001 must run with MONGO_DB=job_radar_e2e


@pytest.fixture(scope="session", autouse=True)
def seed_database():
    """Put the same known jobs in the e2e database before the tests run."""
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
    db = client[E2E_DB]
    db.jobs.delete_many({})
    db.job_details.delete_many({})
    db.jobs.insert_many([dict(job) for job in JOBS])
    db.job_details.insert_many([dict(details) for details in DETAILS])
    yield
    client.close()
