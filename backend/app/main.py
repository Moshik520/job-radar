
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Job Radar API")


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
    return response.json()

