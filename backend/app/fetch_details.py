"""Fetch and cache the full details of every stored job that doesn't have them yet.

Run from the backend folder:  python -m app.fetch_details
"""

import asyncio

import httpx

from app.db import details_collection, jobs_collection
from app.details import HTTP_HEADERS, get_details
from app.models import Job

MAX_CONCURRENT_REQUESTS = 20


async def main() -> None:
    cached = {doc["_id"]: doc.get("job_updated_at") async for doc in details_collection.find({}, {"job_updated_at": 1})}
    jobs = [Job(**doc) async for doc in jobs_collection.find()]
    missing = [job for job in jobs if job.id not in cached or cached[job.id] != job.updated_at]
    print(f"{len(jobs)} jobs, {len(missing)} need details")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    failures = 0

    async def fetch(client: httpx.AsyncClient, job: Job) -> None:
        nonlocal failures
        async with semaphore:
            try:
                await get_details(client, job)
            except Exception as error:  # one job's failure must not stop the rest
                failures += 1
                print(f"  failed {job.id}: {type(error).__name__}: {str(error)[:100]}")

    async with httpx.AsyncClient(timeout=30, headers=HTTP_HEADERS, follow_redirects=True) as client:
        await asyncio.gather(*(fetch(client, job) for job in missing))
    print(f"Fetched {len(missing) - failures} job details, {failures} failed")


if __name__ == "__main__":
    asyncio.run(main())
