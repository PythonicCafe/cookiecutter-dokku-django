import datetime

from project.utils.date import parse_iso_date


def test_parse_iso_date_valid():
    assert parse_iso_date("2026-03-15") == datetime.date(2026, 3, 15)
