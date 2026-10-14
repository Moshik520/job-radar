"""Scan every company's job board and store its open jobs in Israel in MongoDB.

Run from the backend folder:  python -m app.scanner
"""

import asyncio
import re
from datetime import UTC, datetime

import httpx
from pymongo import UpdateOne

from app.db import companies_collection, details_collection, ensure_indexes, hidden_collection, jobs_collection
from app.providers import FETCHERS

MAX_CONCURRENT_REQUESTS = 30


async def save_jobs(jobs) -> None:
    """Upsert all jobs of one company in a single round trip to MongoDB."""
    if not jobs:
        return
    first_seen = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    operations = []
    for job in jobs:
        fields = job.model_dump()
        update = {"$set": fields}
        if fields["published_at"] is None:  # no date from the ATS: keep the time we first saw the job
            del fields["published_at"]
            update["$setOnInsert"] = {"published_at": first_seen}
        operations.append(UpdateOne({"_id": job.id}, update, upsert=True))
    await jobs_collection.bulk_write(operations)


async def hidden_job_ids(company_id: str) -> set[str]:
    """Jobs of this company that the user removed from the site."""
    query = {"_id": {"$regex": f"^{re.escape(company_id)}:"}}
    return {doc["_id"] async for doc in hidden_collection.find(query, {"_id": 1})}


async def remove_closed_jobs(company_id: str, open_job_ids: list[str]) -> int:
    """Delete the company's stored jobs that are no longer on its board. Returns how many were deleted."""
    query = {
        "_id": {"$regex": f"^{re.escape(company_id)}:", "$nin": open_job_ids},  # job ids start with the company id
    }
    closed_ids = [doc["_id"] async for doc in jobs_collection.find(query, {"_id": 1})]
    if closed_ids:
        await jobs_collection.delete_many({"_id": {"$in": closed_ids}})
        await details_collection.delete_many({"_id": {"$in": closed_ids}})
    return len(closed_ids)


async def scan_company(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, company: dict) -> int:
    """Scan one company. Returns how many jobs were saved."""
    async with semaphore:
        try:
            fetch_jobs = FETCHERS[company["ats"]]
            all_jobs = await fetch_jobs(client, company)
        except Exception as error:  # one broken board must never stop the whole scan
            await companies_collection.update_one(
                {"_id": company["_id"]},
                {"$set": {"last_error": str(error)}},
            )
            return 0
        # The site is for job seekers in Israel; jobs elsewhere are never stored.
        hidden = await hidden_job_ids(company["_id"])
        jobs = [job for job in all_jobs if job.is_israel and job.id not in hidden]
        await save_jobs(jobs)
        if not company.get("partial"):
            await remove_closed_jobs(company["_id"], [job.id for job in jobs])
        await companies_collection.update_one(
            {"_id": company["_id"]},
            {"$set": {
                "last_error": None,
                "open_jobs": len(jobs),
                "last_scanned": datetime.now(UTC),
            }},
        )
        return len(jobs)


async def scan_all() -> None:
    await ensure_indexes()
    companies = await companies_collection.find({"ats": {"$in": list(FETCHERS)}}).to_list()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    started = datetime.now(UTC)

    async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}, follow_redirects=True) as client:
        results = await asyncio.gather(
            *(scan_company(client, semaphore, company) for company in companies)
        )

    seconds = (datetime.now(UTC) - started).total_seconds()
    print(f"Scanned {len(companies)} companies, saved {sum(results)} jobs in {seconds:.0f}s")


if __name__ == "__main__":
    asyncio.run(scan_all())
