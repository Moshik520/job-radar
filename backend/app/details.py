"""Get a job's full details: from the MongoDB cache, or from the company's ATS (then cached)."""

from datetime import UTC, datetime

import httpx

from app.db import companies_collection, details_collection
from app.models import Job, JobDetails
from app.providers import DETAIL_FETCHERS

HTTP_HEADERS = {"Accept": "application/json"}


def split_job_id(job_id: str) -> tuple[str, str, str]:
    """"greenhouse:riskified:8768908002" -> ("greenhouse", "riskified", "8768908002")."""
    source, board, native_id = job_id.split(":", 2)
    return source, board, native_id


async def get_details(client: httpx.AsyncClient, job: Job) -> JobDetails:
    cached = await details_collection.find_one({"_id": job.id})
    # A job edited on the ATS since we cached it gets fetched again.
    if cached and cached.get("job_updated_at") == job.updated_at:
        return JobDetails(**cached["details"])

    source, board, native_id = split_job_id(job.id)
    company = await companies_collection.find_one({"_id": f"{source}:{board}"}) or {"board": board}
    details = await DETAIL_FETCHERS[source](client, company, native_id)
    await details_collection.update_one(
        {"_id": job.id},
        {"$set": {
            "details": details.model_dump(),
            "job_updated_at": job.updated_at,
            "fetched_at": datetime.now(UTC),
        }},
        upsert=True,
    )
    return details
