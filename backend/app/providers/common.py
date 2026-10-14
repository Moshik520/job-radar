"""Helpers shared by every provider: polite HTTP requests and building a Job."""

import asyncio
import random

import httpx

from app.classify import classify_category
from app.locations import is_israel
from app.models import Job, JobSource

# Requests per second for hosts that answer 429 (Too Many Requests) when pushed.
RATE_LIMITS = {
    "apply.workable.com": 3,
    "recruitee.com": 4,
    "myworkdayjobs.com": 5,
    "www.comeet.com": 4,
}
RETRY_STATUSES = {429, 502, 503, 504}
MAX_ATTEMPTS = 5

_next_slot: dict[str, float] = {}


def _rate_key(url: str) -> str | None:
    host = httpx.URL(url).host
    if host.endswith(".myworkdayjobs.com"):
        return host.split(".", 1)[1]  # one limit per Workday cluster, e.g. "wd5.myworkdayjobs.com"
    if host.endswith(".recruitee.com"):
        return "recruitee.com"
    return host if host in RATE_LIMITS else None


async def _throttle(url: str) -> None:
    """Space out requests to rate-limited hosts without holding up requests to other hosts."""
    key = _rate_key(url)
    if key is None:
        return
    rate = RATE_LIMITS.get(key) or RATE_LIMITS["myworkdayjobs.com"]
    loop = asyncio.get_running_loop()
    slot = max(loop.time(), _next_slot.get(key, 0.0))
    _next_slot[key] = slot + 1 / rate
    await asyncio.sleep(slot - loop.time())


async def request(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
    """GET (or POST when a json body is given), retrying rate limits and brief outages with backoff."""
    for attempt in range(MAX_ATTEMPTS):
        await _throttle(url)
        if "json" in kwargs:
            response = await client.post(url, **kwargs)
        else:
            response = await client.get(url, **kwargs)
        if response.status_code not in RETRY_STATUSES or attempt == MAX_ATTEMPTS - 1:
            break
        retry_after = response.headers.get("retry-after", "")
        delay = min(float(retry_after), 60) if retry_after.isdigit() else 2**attempt + random.random()
        await asyncio.sleep(delay)
    response.raise_for_status()
    return response


async def get_json(client: httpx.AsyncClient, url: str, **kwargs):
    return (await request(client, url, **kwargs)).json()


def display_name(company: dict) -> str:
    """A readable company name when the ATS doesn't send one: "monday-com" -> "Monday Com"."""
    name = company.get("name") or company["board"]
    if " " not in name and name == name.lower():  # a board token, not a real name
        return name.replace("-", " ").replace("_", " ").title()
    return name


def make_job(
    *,
    source: JobSource,
    company: dict,
    native_id: str,
    title: str | None,
    company_name: str | None,
    location: str | None,
    url: str | None,
    published_at: str | None,
    updated_at: str | None,
) -> Job:
    location = (location or "").strip()
    title = (title or "").strip()
    return Job(
        id=f"{source}:{company['board']}:{native_id}",
        title=title,
        company=(company_name or "").strip() or display_name(company),
        location=location,
        url=url or company.get("board_url") or "",
        source=source,
        published_at=published_at or updated_at,
        updated_at=updated_at or published_at,
        is_israel=is_israel(location),
        category=classify_category(title),
    )
