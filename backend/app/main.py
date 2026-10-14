
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db import jobs_collection
from app.models import Job
from app.providers import greenhouse

app = FastAPI(title="Job Radar API")

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
            return await greenhouse.fetch_jobs(client, board)
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Company not found") from error
            raise


@app.post("/scan/greenhouse/{board}")
async def scan_greenhouse(board: str):
    jobs = await greenhouse_jobs(board)
    for job in jobs:
        await jobs_collection.update_one(
            {"_id": job.id},
            {"$set": job.model_dump()},
            upsert=True,
        )
    return {"saved": len(jobs)}


@app.get("/jobs")
async def list_jobs():
    cursor = jobs_collection.find()
    documents = await cursor.to_list()
    return [Job(**doc) for doc in documents]
