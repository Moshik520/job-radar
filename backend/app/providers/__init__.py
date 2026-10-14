"""One adapter per applicant-tracking system. Each turns that ATS's job board into our Job model."""

from app.providers import (
    ashby,
    comeet,
    greenhouse,
    lever,
    personio,
    recruitee,
    rippling,
    smartrecruiters,
    workable,
    workday,
)

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
    "smartrecruiters": smartrecruiters.fetch_jobs,
}

DETAIL_FETCHERS = {
    "greenhouse": greenhouse.fetch_details,
    "ashby": ashby.fetch_details,
    "lever": lever.fetch_details,
    "workable": workable.fetch_details,
    "recruitee": recruitee.fetch_details,
    "personio": personio.fetch_details,
    "rippling": rippling.fetch_details,
    "workday": workday.fetch_details,
    "comeet": comeet.fetch_details,
    "smartrecruiters": smartrecruiters.fetch_details,
}
