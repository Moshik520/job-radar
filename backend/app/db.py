import os

from pymongo import AsyncMongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = AsyncMongoClient(MONGO_URL)
db = client["job_radar"]
jobs_collection = db["jobs"]
companies_collection = db["companies"]
