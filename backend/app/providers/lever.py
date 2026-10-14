from datetime import UTC, datetime

import httpx

from app.models import Job
from app.providers.common import get_json, make_job


def ms_to_iso(ms: int | None) -> str | None:
    """Lever sends timestamps as milliseconds since 1970."""
    return datetime.fromtimestamp(ms / 1000, UTC).isoformat(timespec="seconds") if ms else None


def to_job(raw: dict, company: dict) -> Job:
    created = ms_to_iso(raw.get("createdAt"))
    return make_job(
        source="lever",
        company=company,
        native_id=raw["id"],
        title=raw.get("text"),
        company_name=None,
        location=(raw.get("categories") or {}).get("location"),
        url=raw.get("hostedUrl"),
        published_at=created,
        updated_at=created,
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    return [to_job(raw, company) for raw in await get_json(client, company["api_url"])]
