from uuid import UUID

from .domain import Journal, JournalType
from .repository import JournalRepository


class JournalService:
    def __init__(self, repository: JournalRepository):
        self.repository = repository

    def create_journal(
            self,
            user_id: UUID,
            title: str,
            journal_type: JournalType = JournalType.PERSONAL,
    ) -> Journal:
        title = title.strip()

        if not title:
            raise ValueError("Journal title is required")

        journal = Journal(
            user_id=user_id,
            title=title,
            type=journal_type,
        )

        self.repository.save(journal)
        return journal

    def get_journal(self, journal_id: UUID) -> Journal | None:
        return self.repository.get(journal_id)

    def list_journals(self, user_id: UUID) -> list[Journal]:
        return self.repository.list_by_user(user_id)
