from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import StrEnum
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel


def utc_now() -> datetime:
    return datetime.now(UTC)

def format_datetime(
        value: datetime,
        timezone: str = "America/New_York"
) -> str:
    local_date = value.astimezone(ZoneInfo(timezone))

    return local_date.strftime("%m/%d/%Y %I:%M:%S %p")

class JournalType(StrEnum):
    PERSONAL = "personal"
    GRATITUDE = "gratitude"
    DREAM = "dream"
    REFLECTION = "reflection"
    PRODUCTIVITY = "productivity"
    CUSTOM = "custom"


class EntryStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


@dataclass
class Journal:
    user_id: UUID
    title: str
    type: JournalType = JournalType.PERSONAL
    id: UUID = field(default_factory=uuid4)
    is_archived: bool = False

    def rename(self, title: str) -> None:
        title = title.strip()
        if not title:
            raise ValueError("Journal title is required")
        self.title = title

    def archive(self) -> None:
        self.is_archived = True


@dataclass
class JournalEntry:
    journal_id: UUID
    title: str
    content: str
    id: UUID = field(default_factory=uuid4)
    status: EntryStatus = EntryStatus.DRAFT
    is_favorite: bool = False
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def update_title(self, title: str) -> None:
        self.title = title
        self.updated_at = utc_now()

    def update_content(self, content: str) -> None:
        self.content = content
        self.updated_at = utc_now()

    def publish(self) -> None:
        if not self.content.strip():
            raise ValueError(
                "Cannot publish an empty journal entry"
            )
        self.status = EntryStatus.PUBLISHED
        self.updated_at = utc_now()

    def toggle_favorite(self) -> None:
        self.is_favorite = not self.is_favorite
        self.updated_at = utc_now()