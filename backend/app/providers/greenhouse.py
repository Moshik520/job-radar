from app.locations import is_israel
from app.models import Job


def to_job(raw: dict, board: str) -> Job:
    return Job(
        id=f"greenhouse:{board}:{raw['id']}",
        title=raw["title"].strip(),
        company=raw["company_name"],
        location=raw["location"]["name"],
        url=raw["absolute_url"],
        source="greenhouse",
        published_at=raw["first_published"],
        updated_at=raw["updated_at"],
        is_israel=is_israel(raw["location"]["name"]),
    )
