"""Comeet has no open board API, but each company's public jobs page embeds the full position list."""

import json
import re

import httpx

from app.models import Job
from app.providers.common import make_job, request


def extract_embedded(page: str, marker: str):
    """Parse the JSON value assigned to `marker` inside the page's script."""
    match = re.search(re.escape(marker) + r"\s*=\s*", page)
    if not match:
        raise ValueError(f"{marker} not found on the Comeet page")
    value, _ = json.JSONDecoder().raw_decode(page, match.end())
    return value


def format_location(raw: dict) -> str:
    location = raw.get("location") or {}
    # Comeet sends country codes. Spell out Israel: a bare "IL" can't be matched safely ("Chicago, IL").
    country = "Israel" if location.get("country") == "IL" else location.get("country")
    parts: list[str] = []
    for part in (location.get("city"), location.get("state"), country):
        for piece in (part or "").split(","):
            piece = piece.strip()
            if piece and piece.lower() not in (p.lower() for p in parts):
                parts.append(piece)
    return ", ".join(parts) or location.get("name") or ""


def to_job(raw: dict, company: dict) -> Job:
    return make_job(
        source="comeet",
        company=company,
        native_id=raw["uid"],
        title=raw.get("name"),
        company_name=raw.get("company_name"),
        location=format_location(raw),
        url=raw.get("url_active_page") or raw.get("url_comeet_hosted_page"),
        published_at=None,
        updated_at=raw.get("time_updated"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    # The page answers 406 to the default "Accept: application/json".
    response = await request(client, company["api_url"], headers={"Accept": "text/html,application/xhtml+xml"})
    positions = extract_embedded(response.text, "COMPANY_POSITIONS_DATA")
    return [to_job(raw, company) for raw in positions if not raw.get("is_internal")]
