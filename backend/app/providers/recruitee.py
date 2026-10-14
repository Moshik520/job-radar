import httpx

from app.models import Job
from app.providers.common import get_json, make_job


def to_job(raw: dict, company: dict) -> Job:
    return make_job(
        source="recruitee",
        company=company,
        native_id=str(raw["id"]),
        title=raw.get("title"),
        company_name=raw.get("company_name"),
        location=raw.get("location"),
        url=raw.get("careers_url"),
        published_at=raw.get("published_at"),
        updated_at=raw.get("updated_at"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    data = await get_json(client, company["api_url"])
    return [to_job(raw, company) for raw in data.get("offers", [])]
