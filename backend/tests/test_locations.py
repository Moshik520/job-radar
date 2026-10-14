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
        # Places found in real job data, written without "Israel"
        ("Ashkelon", True),
        ("Kiryat Gat, ISR", True),
        ("Yoqneam Ilit", True),
        ("Beit She'an Valley", True),
        ("Migdal HaEmek", True),
        ("Rishon LeTsiyon", True),
        ("Kefar Sava", True),
        ("Giv‘atayim", True),  # curly apostrophe
        ("Ra’anana", True),  # curly apostrophe
        ("ISR - Modi’in-Maccabim-Re’ut - Alpha Bio Tec Ltd.", True),
        ("Nof HaGalil", True),
        ("צפון", True),  # Hebrew
        # Outside Israel
        ("Lisbon", False),
        ("New York; Remote", False),
        ("Remote", False),
        ("Chicago, IL", False),  # IL is Illinois, not Israel
        ("Nazareth, PA", False),  # a town in Pennsylvania
        ("Dalton, GA", False),
        # Regression: a Boston hospital chain, not Israel
        ("Beth Israel Deaconess Medical Center, Boston", False),
        # Several locations, one of them in Israel
        ("Tel Aviv; London", True),
        ("London; Tel Aviv", True),
    ],
)
def test_is_israel(location, expected):
    assert is_israel(location) is expected
