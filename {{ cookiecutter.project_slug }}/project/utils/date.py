import datetime


def parse_iso_date(value: str) -> datetime.date:
    """Parse ISO formatted date string (YYYY-MM-DD) into datetime.date object."""
    return datetime.datetime.strptime(value, "%Y-%m-%d").date()
