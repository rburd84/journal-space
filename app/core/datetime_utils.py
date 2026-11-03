from datetime import datetime
from zoneinfo import ZoneInfo


def format_datetime(
        value: datetime,
        timezone: str = "America/New_York"
) -> str:
    local_date = value.astimezone(ZoneInfo(timezone))

    return local_date.strftime("%m/%d/%Y %I:%M:%S %p")
