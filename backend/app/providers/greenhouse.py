import html

import httpx

from app.classify import classify_category
from app.dates import to_utc_iso
from app.locations import is_israel
from app.models import Job, JobDetails
from app.providers.common import get_json, make_details

API_URL = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs"


def to_job(raw: dict, board: str) -> Job:
    # Real boards sometimes omit these: no location, or no first_published date.
    location = (raw.get("location") or {}).get("name") or ""
    published_at = raw.get("first_published") or raw["updated_at"]
    title = raw["title"].strip()
    return Job(
        id=f"greenhouse:{board}:{raw['id']}",
        title=title,
        company=raw["company_name"],
        location=location,
        url=raw["absolute_url"],
        source="greenhouse",
        published_at=to_utc_iso(published_at),
        updated_at=to_utc_iso(raw["updated_at"]),
        is_israel=is_israel(location),
        category=classify_category(title),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    """Fetch a company's open jobs. Raises httpx.HTTPStatusError on 404 and other HTTP errors."""
    board = company["board"]
    data = await get_json(client, API_URL.format(board=board))
    return [to_job(raw, board) for raw in data["jobs"]]


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    raw = await get_json(client, f"https://boards-api.greenhouse.io/v1/boards/{company['board']}/jobs/{native_id}")
    return make_details(
        html.unescape(raw.get("content") or ""),  # Greenhouse sends entity-escaped HTML
        [d.get("name") for d in raw.get("departments") or []],
        {m["name"]: m["value"] for m in raw.get("metadata") or [] if isinstance(m.get("value"), (str, int, float))},
    )
