"""SmartRecruiters (Check Point, Wix, ...). Its API can filter by country, so only Israeli jobs are fetched."""

import httpx

from app.models import Job, JobDetails
from app.providers.common import get_json, make_details, make_job

API_URL = "https://api.smartrecruiters.com/v1/companies/{board}/postings"
PAGE_SIZE = 100


def format_location(raw: dict) -> str:
    location = raw.get("location") or {}
    # Country comes as a code; spell out Israel so location matching works ("il" alone is ambiguous).
    country = "Israel" if location.get("country") == "il" else (location.get("country") or "").upper()
    parts = [location.get("city"), location.get("region"), country]
    return ", ".join(part for part in parts if part)


def to_job(raw: dict, company: dict) -> Job:
    return make_job(
        source="smartrecruiters",
        company=company,
        native_id=raw["id"],
        title=raw.get("name"),
        company_name=(raw.get("company") or {}).get("name"),
        location=format_location(raw),
        url=f"https://jobs.smartrecruiters.com/{company['board']}/{raw['id']}",
        published_at=raw.get("releasedDate"),
        updated_at=raw.get("releasedDate"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    url = API_URL.format(board=company["board"])
    postings, offset = [], 0
    while True:
        page = await get_json(client, url, params={"country": "il", "limit": PAGE_SIZE, "offset": offset})
        batch = page.get("content", [])
        postings += batch
        offset += PAGE_SIZE
        if not batch or offset >= page.get("totalFound", 0):
            break
    return [to_job(raw, company) for raw in postings]


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    raw = await get_json(client, f"{API_URL.format(board=company['board'])}/{native_id}")
    sections = (raw.get("jobAd") or {}).get("sections") or {}
    content = "".join(
        f"<h3>{section.get('title', '')}</h3>{section.get('text', '')}"
        for key in ("companyDescription", "jobDescription", "qualifications", "additionalInformation")
        if (section := sections.get(key)) and section.get("text")
    )
    return make_details(
        content,
        [(raw.get("department") or {}).get("label")],
        {
            "Employment type": (raw.get("typeOfEmployment") or {}).get("label"),
            "Experience": (raw.get("experienceLevel") or {}).get("label"),
        },
    )
