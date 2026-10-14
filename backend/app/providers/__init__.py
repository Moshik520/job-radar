"""One adapter per applicant-tracking system. Each turns that ATS's job board into our Job model."""

from app.providers import ashby, comeet, greenhouse, lever, personio, recruitee, rippling, workable, workday

FETCHERS = {
    "greenhouse": greenhouse.fetch_jobs,
    "ashby": ashby.fetch_jobs,
    "lever": lever.fetch_jobs,
    "workable": workable.fetch_jobs,
    "recruitee": recruitee.fetch_jobs,
    "personio": personio.fetch_jobs,
    "rippling": rippling.fetch_jobs,
    "workday": workday.fetch_jobs,
    "comeet": comeet.fetch_jobs,
}
