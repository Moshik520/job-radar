
import os
import re
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.db import ensure_indexes, jobs_collection
from app.details import HTTP_HEADERS, get_details
from app.models import Category, CategoryCount, Job, JobDetails, JobSource, JobsPage
from app.providers import greenhouse
from app.scanner import remove_closed_jobs, save_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes()
    yield


app = FastAPI(title="Job Radar API", lifespan=lifespan)

# Allow the Angular app (a different origin) to call this API from the browser.
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/greenhouse/{board}")
async def greenhouse_jobs(board: str) -> list[Job]:
    async with httpx.AsyncClient() as client:
        try:
            return await greenhouse.fetch_jobs(client, {"board": board})
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Company not found") from error
            raise


@app.post("/scan/greenhouse/{board}")
async def scan_greenhouse(board: str):
    jobs = [job for job in await greenhouse_jobs(board) if job.is_israel]
    await save_jobs(jobs)
    removed = await remove_closed_jobs(f"greenhouse:{board}", [job.id for job in jobs])
    return {"saved": len(jobs), "removed": removed}


def build_query(search: str, source: JobSource | None, categories: list[Category]) -> dict:
    """The MongoDB filter shared by the job list and the category counts."""
    query = {}
    if search:
        query["title"] = {"$regex": re.escape(search), "$options": "i"}
    if source:
        query["source"] = source
    if categories:
        query["category"] = {"$in": categories}
    return query


@app.get("/jobs")
async def list_jobs(
    search: str = "",
    source: JobSource | None = None,
    category: list[Category] = Query(default=[]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> JobsPage:
    query = build_query(search, source, category)
    total = await jobs_collection.count_documents(query)
    cursor = (
        jobs_collection.find(query)
        .sort([("published_at", -1), ("_id", 1)])
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    documents = await cursor.to_list()
    return JobsPage(
        items=[Job(**doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


@app.get("/jobs/categories")
async def job_categories(search: str = "", source: JobSource | None = None) -> list[CategoryCount]:
    """How many jobs each category has for the current search (the category filter itself is ignored)."""
    pipeline = [
        {"$match": build_query(search, source, [])},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    rows = await (await jobs_collection.aggregate(pipeline)).to_list()
    return [CategoryCount(category=row["_id"] or "other", count=row["count"]) for row in rows]


@app.get("/jobs/{job_id:path}/details")
async def job_details(job_id: str) -> JobDetails:
    """The full description of one job, fetched from the company's ATS the first time and then cached."""
    document = await jobs_collection.find_one({"_id": job_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Job not found")
    async with httpx.AsyncClient(timeout=20, headers=HTTP_HEADERS, follow_redirects=True) as client:
        try:
            return await get_details(client, Job(**document))
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                raise HTTPException(status_code=404, detail="This job is no longer on the company's site") from error
            raise HTTPException(status_code=502, detail="The company's job site did not answer") from error
        except LookupError as error:
            raise HTTPException(status_code=404, detail="This job is no longer on the company's site") from error
        except httpx.HTTPError as error:
            raise HTTPException(status_code=502, detail="The company's job site did not answer") from error


@app.get("/jobs/{job_id:path}")  # Workday and Comeet ids contain "/"
async def get_job(job_id: str) -> Job:
    document = await jobs_collection.find_one({"_id": job_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(**document)
