import html
from datetime import UTC, datetime

import httpx

from app.models import Job, JobDetails
from app.providers.common import JobNotOnBoard, get_json, make_details, make_job, recent_board


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


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    board = await recent_board(company["api_url"], lambda: get_json(client, company["api_url"]))
    raw = next((j for j in board if j["id"] == native_id), None)
    if raw is None:
        raise JobNotOnBoard(native_id)
    lists = "".join(
        f"<h3>{html.escape(item.get('text', ''))}</h3><ul>{item.get('content', '')}</ul>"
        for item in raw.get("lists") or []
    )
    categories = raw.get("categories") or {}
    return make_details(
        (raw.get("description") or "") + lists + (raw.get("additional") or ""),
        [categories.get("team"), categories.get("department")],
        {"Commitment": categories.get("commitment"), "Workplace": raw.get("workplaceType")},
    )
