import httpx

from app.models import Job, JobDetails
from app.providers.common import JobNotOnBoard, get_json, make_details, make_job, recent_board


def to_job(raw: dict, company: dict) -> Job:
    return make_job(
        source="recruitee",
        company=company,
        native_id=str(raw["id"]),
        title=raw.get("title"),
        company_name=raw.get("company_name"),
        location=raw.get("location"),
        url=raw.get("careers_url"),
        published_at=raw.get("published_at"),
        updated_at=raw.get("updated_at"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    data = await get_json(client, company["api_url"])
    return [to_job(raw, company) for raw in data.get("offers", [])]


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    board = await recent_board(company["api_url"], lambda: get_json(client, company["api_url"]))
    raw = next((j for j in board.get("offers", []) if str(j["id"]) == native_id), None)
    if raw is None:
        raise JobNotOnBoard(native_id)
    requirements = f"<h3>Requirements</h3>{raw['requirements']}" if raw.get("requirements") else ""
    return make_details(
        (raw.get("description") or "") + requirements,
        [raw.get("department")],
        {"Employment type": raw.get("employment_type_code")},
    )
