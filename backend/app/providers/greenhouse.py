import httpx

from app.classify import classify_category
from app.locations import is_israel
from app.models import Job
from app.providers.common import get_json

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
        published_at=published_at,
        updated_at=raw["updated_at"],
        is_israel=is_israel(location),
        category=classify_category(title),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    """Fetch a company's open jobs. Raises httpx.HTTPStatusError on 404 and other HTTP errors."""
    board = company["board"]
    data = await get_json(client, API_URL.format(board=board))
    return [to_job(raw, board) for raw in data["jobs"]]
