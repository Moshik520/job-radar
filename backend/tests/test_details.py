import pytest

from app.details import split_job_id
from app.providers.common import make_details


@pytest.mark.parametrize(
    ("job_id", "expected"),
    [
        ("greenhouse:riskified:8768908002", ("greenhouse", "riskified", "8768908002")),
        ("comeet:abra-web-mobile/D3.004:31.648", ("comeet", "abra-web-mobile/D3.004", "31.648")),
        (
            "workday:wd1/aba/ABA:/job/US-DC-Main-Office/Intern--Copywriting_R621",
            ("workday", "wd1/aba/ABA", "/job/US-DC-Main-Office/Intern--Copywriting_R621"),
        ),
    ],
)
def test_split_job_id_keeps_slashes_in_board_and_native_id(job_id, expected):
    assert split_job_id(job_id) == expected


def test_make_details_drops_empty_departments_and_fields():
    details = make_details("<p>Hi</p>", ["R&D", None, ""], {"Workplace": "Hybrid", "Seniority": None, "Type": ""})

    assert details.departments == ["R&D"]
    assert [(f.name, f.value) for f in details.fields] == [("Workplace", "Hybrid")]
