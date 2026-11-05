from uuid import UUID

from .domain import Journal, JournalType
from .repository import JournalRepository


class JournalNotFoundError(Exception):
    pass


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

    def rename_journal(
            self,
            journal_id: UUID,
            title: str,
    ) -> Journal:
        journal = self.repository.get(journal_id)

        if journal is None:
            raise JournalNotFoundError(journal_id)

        journal.rename(title)
        self.repository.save(journal)
        return journal

    def archive_journal(self, journal_id: UUID) -> Journal:
        journal = self.repository.get(journal_id)

        if journal is None:
            raise JournalNotFoundError(journal_id)

        journal.archive()
        self.repository.save(journal)
        return journal
