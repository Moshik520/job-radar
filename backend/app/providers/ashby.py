import httpx

from app.models import Job
from app.providers.common import get_json, make_job

API_URL = "https://api.ashbyhq.com/posting-api/job-board/{board}"


def to_job(raw: dict, company: dict) -> Job:
    return make_job(
        source="ashby",
        company=company,
        native_id=raw["id"],
        title=raw.get("title"),
        company_name=None,
        location=raw.get("location"),
        url=raw.get("jobUrl"),
        published_at=raw.get("publishedAt"),
        updated_at=raw.get("publishedAt"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    data = await get_json(client, API_URL.format(board=company["board"]))
    return [to_job(raw, company) for raw in data.get("jobs", []) if raw.get("isListed", True)]
