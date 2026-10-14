import os

from pymongo import AsyncMongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "job_radar")  # the API tests use their own database

client = AsyncMongoClient(MONGO_URL)
db = client[MONGO_DB]
jobs_collection = db["jobs"]
companies_collection = db["companies"]
details_collection = db["job_details"]  # full descriptions, keyed by job id
favorites_collection = db["favorites"]  # starred jobs, with a copy of each job
hidden_collection = db["hidden_jobs"]  # jobs the user removed; the scanner never stores them again


async def ensure_indexes() -> None:
    """Indexes for the filters and sort order used by GET /jobs."""
    await jobs_collection.create_index([("published_at", -1)])
    await jobs_collection.create_index([("source", 1), ("published_at", -1)])
    await jobs_collection.create_index([("category", 1), ("published_at", -1)])
