import pytest

from app.locations import is_israel


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        # Israeli cities
        ("Tel Aviv", True),
        ("Haifa", True),
        ("Herzliya", True),
        ("Yokneam", True),
        ("Be'er Sheva", True),
        # Spelling variants of Tel Aviv
        ("Tel-Aviv", True),
        ("TelAviv", True),
        ("TLV", True),
        ("Tel Aviv-Yafo, Israel", True),
        # Outside Israel
        ("Lisbon", False),
        ("New York; Remote", False),
        ("Remote", False),
        # Regression: a Boston hospital chain, not Israel
        ("Beth Israel Deaconess Medical Center, Boston", False),
        # Several locations, one of them in Israel
        ("Tel Aviv; London", True),
        ("London; Tel Aviv", True),
    ],
)
def test_is_israel(location, expected):
    assert is_israel(location) is expected
