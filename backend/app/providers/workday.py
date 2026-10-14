"""Workday boards are paged (20 jobs per request) and only say "Posted 3 Days Ago".

Big employers (NVIDIA, Salesforce, Cisco) have more than the 2,000 jobs Workday lets you page through, so the
scan asks for jobs in Israel only, using the board's own location filter ("facet"). That also means most of the
~1,250 Workday companies, which have no jobs in Israel, cost one request instead of up to 100.
"""

import re
from datetime import UTC, datetime, timedelta

import httpx

from app.locations import is_israel
from app.models import Job, JobDetails
from app.providers.common import get_json, make_details, make_job

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


def israel_filter(facets: list[dict]) -> dict | None:
    """Find the board's filter for Israel in its facets.

    Returns {"<facetParameter>": [ids]} to send as appliedFacets, {} if the board has location filters but none
    for Israel (no Israeli jobs), or None if the board has no location filters at all (we can't tell).
    """
    country_match, site_matches, has_location_facets = None, {}, False

    def walk(items):
        nonlocal country_match, has_location_facets
        for facet in items:
            parameter = facet.get("facetParameter") or ""
            if "location" in parameter.lower() or "country" in parameter.lower():
                has_location_facets = True
            for value in facet.get("values") or []:
                if "values" in value:  # a group of facets, e.g. "Locations" holding countries and sites
                    walk([value])
                    continue
                descriptor = (value.get("descriptor") or "").strip()
                if descriptor.lower() == "israel" and country_match is None:
                    country_match = {parameter: [value["id"]]}
                elif is_israel(descriptor):
                    site_matches.setdefault(parameter, []).append(value["id"])

    walk(facets)
    if country_match:
        return country_match
    if site_matches:
        parameter, ids = max(site_matches.items(), key=lambda item: len(item[1]))
        return {parameter: ids}
    return {} if has_location_facets else None


def to_job(raw: dict, company: dict, in_israel: bool = False) -> Job:
    location = raw.get("locationsText") or ""
    if in_israel and not is_israel(location):
        # Filtered to Israel, but the text says e.g. "2 Locations"; say where the job is.
        location = f"{location}, Israel" if location else "Israel"
    return make_job(
        source="workday",
        company=company,
        native_id=raw["externalPath"],
        title=raw.get("title"),
        company_name=None,
        location=location,
        url=company["board_url"] + raw["externalPath"],
        published_at=posted_to_iso(raw.get("postedOn")),
        updated_at=None,
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    first = await get_json(client, company["api_url"], json=_body({}, 0))
    facets = israel_filter(first.get("facets") or [])
    if facets == {}:
        return []  # the board has location filters and Israel isn't one of them
    if facets is None:  # no location filters: read the whole board, like before
        return await _read_all(client, company, {}, first, in_israel=False)
    return await _read_all(client, company, facets, None, in_israel=True)


def _body(facets: dict, offset: int) -> dict:
    return {"appliedFacets": facets, "limit": PAGE_SIZE, "offset": offset, "searchText": ""}


async def _read_all(client, company, facets, first_page, in_israel: bool) -> list[Job]:
    postings, offset, total = [], 0, None
    page = first_page
    while True:
        if page is None:
            page = await get_json(client, company["api_url"], json=_body(facets, offset))
        if total is None:
            total = page.get("total") or 0  # only the first page reports the real total
        batch = page.get("jobPostings") or []
        postings += batch
        offset += PAGE_SIZE
        page = None
        if not batch or offset >= min(total, MAX_JOBS):
            break
    if total > MAX_JOBS:
        company["partial"] = True  # tells the scanner not to delete jobs it couldn't see
    return [to_job(raw, company, in_israel) for raw in postings if raw.get("externalPath")]


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    base = company["api_url"].rsplit("/jobs", 1)[0]
    info = (await get_json(client, base + native_id)).get("jobPostingInfo") or {}
    return make_details(
        info.get("jobDescription"),
        [],
        {"Time type": info.get("timeType"), "Requisition": info.get("jobReqId")},
    )
