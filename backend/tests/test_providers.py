"""Unit tests for the parts of each adapter that transform data (no network)."""

import xml.etree.ElementTree as ET
from datetime import UTC, datetime

import pytest

from app.providers import comeet, lever, personio, smartrecruiters, workable, workday
from app.providers.common import display_name

COMPANY = {"board": "acme", "name": "acme", "api_url": "https://acme.jobs.personio.de/xml", "board_url": ""}


def test_lever_converts_milliseconds_to_iso_date():
    assert lever.ms_to_iso(1_760_000_000_000) == "2025-10-09T08:53:20+00:00"
    assert lever.ms_to_iso(None) is None


def test_workable_joins_location_parts_and_skips_missing_ones():
    raw = {"city": "Tel Aviv", "region": None, "country": "Israel"}
    assert workable.format_location(raw) == "Tel Aviv, Israel"


@pytest.mark.parametrize(
    ("posted_on", "expected"),
    [
        ("Posted Today", "2026-10-14T12:00:00+00:00"),
        ("Posted Yesterday", "2026-10-13T12:00:00+00:00"),
        ("Posted 3 Days Ago", "2026-10-11T12:00:00+00:00"),
        ("Posted 30+ Days Ago", "2026-09-14T12:00:00+00:00"),
        (None, None),
    ],
)
def test_workday_turns_relative_posted_text_into_a_date(posted_on, expected):
    now = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)
    assert workday.posted_to_iso(posted_on, now) == expected


def test_comeet_spells_out_israel_instead_of_country_code():
    raw = {"location": {"city": "Ra'anana", "state": "Center District", "country": "IL"}}
    assert comeet.format_location(raw) == "Ra'anana, Center District, Israel"


def test_comeet_job_in_israel_is_detected():
    raw = {"uid": "31.648", "name": "Frontend Tech Lead", "location": {"city": "Tel Aviv", "country": "IL"}}
    job = comeet.to_job(raw, {"board": "acme/A1.001", "name": "Acme", "board_url": ""})
    assert job.is_israel is True


def test_comeet_reads_the_positions_embedded_in_the_page():
    page = 'var x = 1; COMPANY_POSITIONS_DATA = [{"uid": "1", "name": "QA"}]; var y = 2;'
    assert comeet.extract_embedded(page, "COMPANY_POSITIONS_DATA") == [{"uid": "1", "name": "QA"}]


def test_personio_builds_job_from_xml_position():
    position = ET.fromstring(
        "<position><id>42</id><name>QA Engineer</name><office>Haifa</office>"
        "<subcompany>Acme Ltd</subcompany><createdAt>2026-10-01T10:00:00+00:00</createdAt></position>"
    )
    job = personio.to_job(position, COMPANY)

    assert job.id == "personio:acme:42"
    assert job.url == "https://acme.jobs.personio.de/job/42"
    assert job.company == "Acme Ltd"
    assert job.is_israel is True


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("monday-com", "Monday Com"),
        ("abra Web & Mobile", "abra Web & Mobile"),
        ("Wix", "Wix"),
    ],
)
def test_display_name_only_prettifies_board_tokens(name, expected):
    assert display_name({"board": name, "name": name}) == expected


# ---------- SmartRecruiters ----------

def test_smartrecruiters_spells_out_israel():
    raw = {"id": "7440", "name": "QA Engineer", "company": {"name": "Wix"}, "releasedDate": "2026-10-14T08:51:31.421Z",
           "location": {"city": "Tel Aviv", "country": "il"}}

    job = smartrecruiters.to_job(raw, {"board": "Wix2", "name": "Wix2"})

    assert job.location == "Tel Aviv, Israel"
    assert job.is_israel is True
    assert job.company == "Wix"
    assert job.url == "https://jobs.smartrecruiters.com/Wix2/7440"
    assert job.published_at == "2026-10-14T08:51:31Z"


# ---------- Workday: finding the Israel filter ----------

NVIDIA_FACETS = [
    {"facetParameter": "jobFamilyGroup", "values": [{"descriptor": "Engineering", "id": "e1"}]},
    {"facetParameter": "locationMainGroup", "values": [
        {"facetParameter": "locationHierarchy1", "descriptor": "Locations", "values": [
            {"descriptor": "Germany", "id": "de"},
            {"descriptor": "Israel", "id": "il-country"},
        ]},
        {"facetParameter": "locations", "descriptor": "Sites", "values": [
            {"descriptor": "Israel, Yokneam", "id": "yokneam"},
        ]},
    ]},
]


def test_workday_prefers_the_country_filter():
    assert workday.israel_filter(NVIDIA_FACETS) == {"locationHierarchy1": ["il-country"]}


def test_workday_falls_back_to_israeli_sites():
    facets = [{"facetParameter": "locations", "values": [
        {"descriptor": "Tel Aviv, Israel", "id": "tlv"},
        {"descriptor": "Haifa", "id": "haifa"},
        {"descriptor": "Chicago, IL", "id": "chi"},
    ]}]
    assert workday.israel_filter(facets) == {"locations": ["tlv", "haifa"]}


def test_workday_board_without_israel_has_no_israeli_jobs():
    facets = [{"facetParameter": "locationCountry", "values": [{"descriptor": "Germany", "id": "de"}]}]
    assert workday.israel_filter(facets) == {}


def test_workday_board_without_location_filters_is_read_in_full():
    assert workday.israel_filter([{"facetParameter": "timeType", "values": [{"descriptor": "Full time", "id": "f"}]}]) is None


def test_workday_job_filtered_to_israel_keeps_its_place():
    raw = {"externalPath": "/job/x_R1", "title": "Engineer", "locationsText": "2 Locations", "postedOn": "Posted Today"}
    company = {"board": "wd5/nvidia/Site", "name": "nvidia", "board_url": "https://nvidia.wd5.myworkdayjobs.com/Site"}

    job = workday.to_job(raw, company, in_israel=True)

    assert job.location == "2 Locations, Israel"
    assert job.is_israel is True
