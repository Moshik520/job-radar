import httpx

from app.models import Job, JobDetails
from app.providers.common import get_json, make_details, make_job

API_URL = "https://apply.workable.com/api/v1/widget/accounts/{board}"


def format_location(raw: dict) -> str:
    parts = (raw.get("city"), raw.get("region") or raw.get("state"), raw.get("country"))
    return ", ".join(part for part in parts if part)


def to_job(raw: dict, company: dict, company_name: str | None) -> Job:
    return make_job(
        source="workable",
        company=company,
        native_id=raw["shortcode"],
        title=raw.get("title"),
        company_name=company_name,
        location=format_location(raw),
        url=raw.get("url"),
        published_at=raw.get("published_on"),
        updated_at=raw.get("published_on"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    data = await get_json(client, API_URL.format(board=company["board"]))
    return [to_job(raw, company, data.get("name")) for raw in data.get("jobs", [])]


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    raw = await get_json(client, f"https://apply.workable.com/api/v2/accounts/{company['board']}/jobs/{native_id}")
    sections = [("", raw.get("description")), ("Requirements", raw.get("requirements")),
                ("Benefits", raw.get("benefits"))]
    content = "".join((f"<h3>{title}</h3>" if title else "") + body for title, body in sections if body)
    department = raw.get("department")
    return make_details(
        content,
        department if isinstance(department, list) else [department],
        {"Employment type": raw.get("type"), "Workplace": raw.get("workplace")},
    )
