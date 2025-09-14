from datetime import datetime

from fastapi import HTTPException, status


def parse_str_to_date(date: str) -> datetime:
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed parse a date",
        )


def parse_str_to_datetime(datetime: str) -> datetime:
    pass
