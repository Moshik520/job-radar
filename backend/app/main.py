
import os
import re
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.db import details_collection, ensure_indexes, favorites_collection, hidden_collection, jobs_collection
from app.details import HTTP_HEADERS, get_details
from app.models import Category, CategoryCount, Job, JobDetails, JobSource, JobsPage
from app.providers import greenhouse
from app.scanner import hidden_job_ids, remove_closed_jobs, save_jobs


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
    hidden = await hidden_job_ids(f"greenhouse:{board}")
    jobs = [job for job in await greenhouse_jobs(board) if job.is_israel and job.id not in hidden]
    await save_jobs(jobs)
    removed = await remove_closed_jobs(f"greenhouse:{board}", [job.id for job in jobs])
    return {"saved": len(jobs), "removed": removed}


async def favorite_ids() -> list[str]:
    return [doc["_id"] async for doc in favorites_collection.find({}, {"_id": 1})]


async def build_query(
    search: str, source: JobSource | None, categories: list[Category], hide_favorites: bool = False
) -> dict:
    """The MongoDB filter shared by the job list and the category counts."""
    query = {}
    if hide_favorites:
        query["_id"] = {"$nin": await favorite_ids()}
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
    hide_favorites: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> JobsPage:
    query = await build_query(search, source, category, hide_favorites)
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
async def job_categories(
    search: str = "", source: JobSource | None = None, hide_favorites: bool = False
) -> list[CategoryCount]:
    """How many jobs each category has for the current search (the category filter itself is ignored)."""
    pipeline = [
        {"$match": await build_query(search, source, [], hide_favorites)},
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


@app.delete("/jobs/{job_id:path}", status_code=204)
async def remove_job(job_id: str) -> None:
    """Remove a job from the site for good: future scans skip it. A copy is kept so it can be restored."""
    document = await jobs_collection.find_one({"_id": job_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Job not found")
    await hidden_collection.update_one(
        {"_id": job_id},
        {"$set": {"job": document, "hidden_at": datetime.now(UTC)}},
        upsert=True,
    )
    await jobs_collection.delete_one({"_id": job_id})
    await details_collection.delete_one({"_id": job_id})


@app.post("/jobs/{job_id:path}/restore")
async def restore_job(job_id: str) -> Job:
    """Undo a removal."""
    hidden = await hidden_collection.find_one({"_id": job_id})
    if hidden is None:
        raise HTTPException(status_code=404, detail="This job was not removed")
    await jobs_collection.replace_one({"_id": job_id}, hidden["job"], upsert=True)
    await hidden_collection.delete_one({"_id": job_id})
    return Job(**hidden["job"])


@app.get("/favorites")
async def list_favorites() -> list[Job]:
    """Starred jobs, most recently starred first. Copies are kept, so closed jobs stay in the list."""
    cursor = favorites_collection.find().sort("starred_at", -1)
    return [Job(**doc["job"]) async for doc in cursor]


@app.put("/favorites/{job_id:path}")
async def add_favorite(job_id: str, job: Job) -> Job:
    if job.id != job_id:
        raise HTTPException(status_code=422, detail="The job in the body doesn't match the URL")
    await favorites_collection.update_one(
        {"_id": job_id},
        {"$set": {"job": job.model_dump()}, "$setOnInsert": {"starred_at": datetime.now(UTC)}},
        upsert=True,
    )
    return job


@app.delete("/favorites/{job_id:path}", status_code=204)
async def remove_favorite(job_id: str) -> None:
    await favorites_collection.delete_one({"_id": job_id})

