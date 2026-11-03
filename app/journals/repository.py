from typing import Protocol
from uuid import UUID

from .domain import Journal, JournalEntry


class JournalRepository(Protocol):
    def get(self, journal_id: UUID) -> Journal | None:
        pass

    def save(self, journal: Journal) -> None:
        pass

    def list_by_user(self, user_id: UUID) -> list[JournalEntry] | None:
        pass


class EntryRepository(Protocol):
    def get(self, entry_id: UUID) -> JournalEntry | None:
        pass

    def save(self, entry: JournalEntry) -> None:
        pass

    def list_by_journal(self, journal_id: UUID) -> list[JournalEntry] | None:
        pass
