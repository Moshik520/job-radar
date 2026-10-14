"""Personio publishes an XML feed instead of JSON."""

import xml.etree.ElementTree as ET

import httpx

from app.models import Job
from app.providers.common import make_job, request


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
