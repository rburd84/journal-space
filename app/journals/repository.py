from typing import Protocol
from uuid import UUID

from .domain import Journal


class JournalRepository(Protocol):
    def get(self, journal_id: UUID) -> Journal | None:
        pass

    def save(self, journal: Journal) -> None:
        pass

    def list_by_user(self, user_id: UUID) -> list[Journal]:
        pass
