"""Unit tests for the parts of each adapter that transform data (no network)."""

import xml.etree.ElementTree as ET
from datetime import UTC, datetime

import pytest

from app.providers import comeet, lever, personio, workable, workday
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
