from typing import Protocol
from uuid import UUID

from .domain import JournalEntry


class EntryRepository(Protocol):
    def get(self, entry_id: UUID) -> JournalEntry | None:
        pass

    def save(self, entry: JournalEntry) -> None:
        pass

    def delete(self, entry_id: UUID) -> bool:
        pass

    def list_by_journal(self, journal_id: UUID) -> list[JournalEntry] | None:
        pass
