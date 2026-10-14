
import re
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.db import ensure_indexes, jobs_collection
from app.models import Job, JobSource, JobsPage
from app.providers import greenhouse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes()
    yield


app = FastAPI(title="Job Radar API", lifespan=lifespan)

# Allow the Angular dev server (a different origin) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
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
    for job in jobs:
        await jobs_collection.update_one(
            {"_id": job.id},
            {"$set": job.model_dump()},
            upsert=True,
        )
    return {"saved": len(jobs)}


@app.get("/jobs")
async def list_jobs(
    search: str = "",
    source: JobSource | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> JobsPage:
    query = {}
    if search:
        query["title"] = {"$regex": re.escape(search), "$options": "i"}
    if source:
        query["source"] = source

    total = await jobs_collection.count_documents(query)
    cursor = (
        jobs_collection.find(query)
        .sort("published_at", -1)
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


@app.get("/jobs/{job_id:path}")  # Workday and Comeet ids contain "/"
async def get_job(job_id: str) -> Job:
    document = await jobs_collection.find_one({"_id": job_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(**document)
