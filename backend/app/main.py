
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.providers.greenhouse import to_job
from app.db import jobs_collection
from app.models import Job

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
async def greenhouse_jobs(board: str):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Company not found")
    jobs = response.json()["jobs"]
    return [to_job(raw, board) for raw in jobs]


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


