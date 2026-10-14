"""Scan every company's job board and store the open jobs in MongoDB.

Run from the backend folder:  python -m app.scanner
"""

import asyncio
from datetime import UTC, datetime

import httpx
from pymongo import UpdateOne

from app.db import companies_collection, ensure_indexes, jobs_collection
from app.providers import FETCHERS

MAX_CONCURRENT_REQUESTS = 30


async def save_jobs(jobs) -> None:
    """Upsert all jobs of one company in a single round trip to MongoDB."""
    if jobs:
        await jobs_collection.bulk_write(
            [UpdateOne({"_id": job.id}, {"$set": job.model_dump()}, upsert=True) for job in jobs]
        )


async def scan_company(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, company: dict) -> int:
    """Scan one company. Returns how many jobs were saved."""
    async with semaphore:
        try:
            fetch_jobs = FETCHERS[company["ats"]]
            jobs = await fetch_jobs(client, company)
        except Exception as error:  # one broken board must never stop the whole scan
            await companies_collection.update_one(
                {"_id": company["_id"]},
                {"$set": {"last_error": str(error)}},
            )
            return 0
        await save_jobs(jobs)
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
