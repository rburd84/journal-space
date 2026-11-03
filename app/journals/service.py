from uuid import UUID

from app.journals.domain import JournalEntry
from .domain import Journal, JournalEntry, JournalType
from .repository import EntryRepository, JournalRepository


class EntryNotFoundError(Exception):
    pass


class EntryService:
    def __init__(self, repository: EntryRepository):
        self.repository = repository

    def create_entry(
            self,
            journal_id: UUID,
            title: str,
            content: str = "",
    ) -> JournalEntry:
        entry = JournalEntry(
            journal_id=journal_id,
            title=title,
            content=content,
        )

        self.repository.save(entry)
        return entry

    def publish_entry(self, entry_id: UUID) -> JournalEntry:
        entry = self.repository.get(entry_id)

        if entry is None:
            raise EntryNotFoundError(entry_id)

        entry.publish()
        self.repository.save(entry)

        return entry

    def update_entry(
            self,
            entry_id: UUID,
            title: str,
            content: str,
    ) -> JournalEntry:
        entry = self.repository.get(entry_id)

        if entry is None:
            raise EntryNotFoundError(entry_id)

        entry.update_title(title)
        entry.update_content(content)

        self.repository.save(entry)
        return entry

    def list_entries_by_journal(
            self,
            journal_id: UUID,
    ) -> list[JournalEntry]:
        return self.repository.list_by_journal(journal_id)


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
















