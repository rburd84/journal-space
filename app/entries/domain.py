from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


class EntryStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


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
