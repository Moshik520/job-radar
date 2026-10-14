"""Personio publishes an XML feed instead of JSON."""

import html
import xml.etree.ElementTree as ET

import httpx

from app.models import Job, JobDetails
from app.providers.common import JobNotOnBoard, make_details, make_job, recent_board, request


def to_job(position: ET.Element, company: dict) -> Job:
    native_id = position.findtext("id")
    base_url = company["api_url"].rsplit("/xml", 1)[0]
    return make_job(
        source="personio",
        company=company,
        native_id=native_id,
        title=position.findtext("name"),
        company_name=position.findtext("subcompany"),
        location=position.findtext("office"),
        url=f"{base_url}/job/{native_id}",
        published_at=position.findtext("createdAt"),
        updated_at=position.findtext("createdAt"),
    )


async def fetch_jobs(client: httpx.AsyncClient, company: dict) -> list[Job]:
    response = await request(client, company["api_url"])
    positions = ET.fromstring(response.content).findall("position")
    return [to_job(position, company) for position in positions]


async def fetch_details(client: httpx.AsyncClient, company: dict, native_id: str) -> JobDetails:
    async def fetch_board():
        return (await request(client, company["api_url"])).content

    positions = ET.fromstring(await recent_board(company["api_url"], fetch_board)).findall("position")
    position = next((p for p in positions if p.findtext("id") == native_id), None)
    if position is None:
        raise JobNotOnBoard(native_id)
    content = "".join(
        f"<h3>{html.escape(d.findtext('name') or '')}</h3>{d.findtext('value') or ''}"
        for d in position.findall("jobDescriptions/jobDescription")
    )
    return make_details(
        content,
        [position.findtext("department")],
        {"Schedule": position.findtext("schedule"), "Seniority": position.findtext("seniority")},
    )
