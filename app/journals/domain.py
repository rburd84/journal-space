from dataclasses import dataclass, field

from enum import StrEnum
from uuid import UUID, uuid4


class JournalType(StrEnum):
    PERSONAL = "personal"
    GRATITUDE = "gratitude"
    DREAM = "dream"
    REFLECTION = "reflection"
    PRODUCTIVITY = "productivity"
    CUSTOM = "custom"


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

    def restore(self) -> None:
        self.is_archived = False
