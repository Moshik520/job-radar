from app.providers.greenhouse import to_job

RAW_JOB = {
    "id": 8768908002,
    "title": "Data Scientist ",
    "company_name": "Riskified",
    "location": {"name": "Tel Aviv"},
    "absolute_url": "https://example.com/jobs/8768908002",
    "first_published": "2026-09-10T11:35:28-04:00",
    "updated_at": "2026-09-12T08:00:00-04:00",
}


def test_maps_greenhouse_fields_to_job():
    job = to_job(RAW_JOB, "riskified")

    assert job.id == "greenhouse:riskified:8768908002"
    assert job.title == "Data Scientist"
    assert job.company == "Riskified"
    assert job.location == "Tel Aviv"
    assert job.source == "greenhouse"
    assert job.is_israel is True


def test_missing_first_published_falls_back_to_updated_at():
    job = to_job({**RAW_JOB, "first_published": None}, "riskified")

    assert job.published_at == "2026-09-12T08:00:00-04:00"


def test_missing_location_becomes_empty_string():
    job = to_job({**RAW_JOB, "location": None}, "riskified")

    assert job.location == ""
    assert job.is_israel is False
