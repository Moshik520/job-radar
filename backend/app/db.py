import os

from pymongo import AsyncMongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = AsyncMongoClient(MONGO_URL)
db = client["job_radar"]
jobs_collection = db["jobs"]
companies_collection = db["companies"]


async def ensure_indexes() -> None:
    """Indexes for the filters and sort order used by GET /jobs."""
    await jobs_collection.create_index([("published_at", -1)])
    await jobs_collection.create_index([("source", 1), ("published_at", -1)])
