"""Comeet has no open board API, but each company's public jobs page embeds the full position list."""

import html
import json
import re

import httpx

from app.models import Job, JobDetails
from app.providers.common import get_json, make_details, make_job, recent_board, request


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


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    # The public jobs page also embeds the token for Comeet's careers API.
    async def fetch_page():
        headers = {"Accept": "text/html,application/xhtml+xml"}
        return (await request(client, company["api_url"], headers=headers)).text

    page = await recent_board(company["api_url"], fetch_page)
    token = re.search(r'"token"\s*:\s*"([0-9A-Fa-f]+)"', page)
    if not token:
        raise ValueError("Comeet API token not found on the jobs page")
    company_uid = company["board"].rsplit("/", 1)[-1]
    raw = await get_json(
        client,
        f"https://www.comeet.co/careers-api/2.0/company/{company_uid}/positions/{native_id}",
        params={"token": token.group(1), "details": "true"},
    )
    content = "".join(
        f"<h3>{html.escape(d.get('name') or '')}</h3>{d.get('value') or ''}" for d in raw.get("details") or []
    )
    return make_details(
        content,
        [raw.get("department")],
        {"Employment type": raw.get("employment_type"), "Experience": raw.get("experience_level"),
         "Workplace": raw.get("workplace_type")},
    )
