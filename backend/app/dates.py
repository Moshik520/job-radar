"""Every ATS writes dates differently; store them all as UTC "2026-10-11T07:09:39Z".

One format matters because jobs are sorted by these strings: "2026-09-10T11:35:28-04:00" and
"2026-09-10T14:00:00+00:00" would otherwise sort in the wrong order.
"""

from datetime import UTC, datetime


def to_utc_iso(value: str | None) -> str | None:
    """'2026-09-10T11:35:28-04:00', '2026-10-11 07:09:39 UTC', '2026-08-24', '...Z' -> '2026-09-10T15:35:28Z'."""
    if not value:
        return None
    text = value.strip().removesuffix(" UTC").replace(" ", "T", 1)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:  # date-only or naive times are treated as UTC
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
