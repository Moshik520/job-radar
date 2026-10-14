import httpx

from app.models import Job, JobDetails
from app.providers.common import JobNotOnBoard, get_json, make_details, make_job, recent_board

API_URL = "https://api.ashbyhq.com/posting-api/job-board/{board}"


def to_job(raw: dict, company: dict) -> Job:
    return make_job(
        source="ashby",
        company=company,
        native_id=raw["id"],
        title=raw.get("title"),
        company_name=None,
        location=raw.get("location"),
        url=raw.get("jobUrl"),
        published_at=raw.get("publishedAt"),
        updated_at=raw.get("publishedAt"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    data = await get_json(client, API_URL.format(board=company["board"]))
    return [to_job(raw, company) for raw in data.get("jobs", []) if raw.get("isListed", True)]


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    url = API_URL.format(board=company["board"])
    board = await recent_board(url, lambda: get_json(client, url))
    raw = next((j for j in board.get("jobs", []) if j["id"] == native_id), None)
    if raw is None:
        raise JobNotOnBoard(native_id)
    return make_details(
        raw.get("descriptionHtml"),
        [raw.get("department"), raw.get("team")],
        {"Employment type": raw.get("employmentType"), "Workplace": raw.get("workplaceType")},
    )
