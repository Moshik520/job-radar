import pytest

from app.dates import to_utc_iso


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-09-10T11:35:28-04:00", "2026-09-10T15:35:28Z"),  # Greenhouse, with offset
        ("2026-10-11T18:17:41.139+00:00", "2026-10-11T18:17:41Z"),  # Ashby, milliseconds
        ("2026-10-11 07:09:39 UTC", "2026-10-11T07:09:39Z"),  # Recruitee
        ("2026-08-24", "2026-08-24T00:00:00Z"),  # Workable, date only
        ("2026-10-08T08:35:19Z", "2026-10-08T08:35:19Z"),  # Comeet
        (None, None),
        ("", None),
        ("Posted 3 Days Ago", None),
    ],
)
def test_to_utc_iso(value, expected):
    assert to_utc_iso(value) == expected


def test_normalized_dates_sort_in_time_order():
    # 11:35 in New York is 15:35 UTC, so it is newer than 14:00 UTC.
    new_york = to_utc_iso("2026-09-10T11:35:28-04:00")
    london = to_utc_iso("2026-09-10T14:00:00+00:00")
    assert sorted([london, new_york], reverse=True) == [new_york, london]
