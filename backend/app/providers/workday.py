"""Workday boards are paged (20 jobs per request) and only say "Posted 3 Days Ago"."""

import re
from datetime import UTC, datetime, timedelta

import httpx

from app.models import Job
from app.providers.common import get_json, make_job

PAGE_SIZE = 20  # Workday's maximum
MAX_JOBS = 2000  # Workday never pages past 2,000 results


def posted_to_iso(text: str | None, now: datetime | None = None) -> str | None:
    """'Posted Today' / 'Posted Yesterday' / 'Posted 3 Days Ago' / 'Posted 30+ Days Ago' -> approximate date."""
    text = (text or "").lower()
    if "today" in text:
        days = 0
    elif "yesterday" in text:
        days = 1
    elif match := re.search(r"(\d+)", text):
        days = int(match.group(1))
    else:
        return None
    now = now or datetime.now(UTC)
    return (now - timedelta(days=days)).isoformat(timespec="seconds")


def to_job(raw: dict, company: dict) -> Job:
    return make_job(
        source="workday",
        company=company,
        native_id=raw["externalPath"],
        title=raw.get("title"),
        company_name=None,
        location=raw.get("locationsText"),
        url=company["board_url"] + raw["externalPath"],
        published_at=posted_to_iso(raw.get("postedOn")),
        updated_at=None,
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    postings, offset, total = [], 0, None
    while True:
        body = {"appliedFacets": {}, "limit": PAGE_SIZE, "offset": offset, "searchText": ""}
        page = await get_json(client, company["api_url"], json=body)
        if total is None:
            total = page.get("total") or 0  # only the first page reports the real total
        batch = page.get("jobPostings") or []
        postings += batch
        offset += PAGE_SIZE
        if not batch or offset >= min(total, MAX_JOBS):
            break
    return [to_job(raw, company) for raw in postings if raw.get("externalPath")]
