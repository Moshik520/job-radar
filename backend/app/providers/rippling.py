import httpx

from app.models import Job, JobDetails
from app.providers.common import get_json, make_details, make_job


def to_job(raw: dict, company: dict) -> Job:
    # Rippling's board API has no dates; the scanner's first-seen time stands in for them.
    return make_job(
        source="rippling",
        company=company,
        native_id=raw["uuid"],
        title=raw.get("name"),
        company_name=None,
        location=(raw.get("workLocation") or {}).get("label"),
        url=raw.get("url"),
        published_at=None,
        updated_at=None,
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    return [to_job(raw, company) for raw in await get_json(client, company["api_url"])]


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    raw = await get_json(client, f"{company['api_url']}/{native_id}")
    description = raw.get("description") or {}
    content = description if isinstance(description, str) else (
        (description.get("company") or "") + (description.get("role") or "")
    )
    employment = raw.get("employmentType")
    return make_details(
        content,
        [(raw.get("department") or {}).get("label")],
        {"Employment type": employment.get("label") if isinstance(employment, dict) else employment},
    )
