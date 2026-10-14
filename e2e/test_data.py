"""The jobs the browser tests run against, so every run sees the same data."""


def job(job_id, title, category, published_at, company="Acme"):
    return {
        "_id": job_id,
        "id": job_id,
        "title": title,
        "company": company,
        "location": "Tel Aviv, Israel",
        "url": f"https://example.com/jobs/{job_id.rsplit(':', 1)[-1]}",
        "source": "greenhouse",
        "published_at": published_at,
        "updated_at": published_at,
        "is_israel": True,
        "category": category,
    }


JOBS = [
    job("greenhouse:acme:1", "QA Automation Engineer", "qa", "2026-10-12T09:00:00Z"),
    job("greenhouse:acme:2", "Senior Full Stack Developer", "fullstack", "2026-10-11T09:00:00Z"),
    job("greenhouse:acme:3", "Backend Engineer", "backend", "2026-10-10T09:00:00Z", company="Beta"),
    job("greenhouse:acme:4", "QA Engineer - Mobile", "qa", "2026-10-09T09:00:00Z", company="Beta"),
    job("greenhouse:acme:5", "Data Analyst", "data", "2026-10-08T09:00:00Z"),
    job("greenhouse:acme:6", "Account Executive", "sales", "2026-10-07T09:00:00Z"),
]

# Cached descriptions, so opening a card never calls a real company site.
DETAILS = [
    {
        "_id": j["_id"],
        "job_updated_at": j["updated_at"],
        "details": {
            "content": f"<p>About the {j['title']} role.</p><ul><li>Write tests</li></ul>",
            "departments": ["R&D"],
            "fields": [{"name": "Workplace", "value": "Hybrid"}],
        },
    }
    for j in JOBS
]
