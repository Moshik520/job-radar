import httpx

from app.models import Job
from app.providers.common import get_json, make_job

API_URL = "https://apply.workable.com/api/v1/widget/accounts/{board}"


def format_location(raw: dict) -> str:
    parts = (raw.get("city"), raw.get("region") or raw.get("state"), raw.get("country"))
    return ", ".join(part for part in parts if part)


def to_job(raw: dict, company: dict, company_name: str | None) -> Job:
    return make_job(
        source="workable",
        company=company,
        native_id=raw["shortcode"],
        title=raw.get("title"),
        company_name=company_name,
        location=format_location(raw),
        url=raw.get("url"),
        published_at=raw.get("published_on"),
        updated_at=raw.get("published_on"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    data = await get_json(client, API_URL.format(board=company["board"]))
    return [to_job(raw, company, data.get("name")) for raw in data.get("jobs", [])]
