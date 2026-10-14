import httpx

from app.models import Job
from app.providers.common import get_json, make_job


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
