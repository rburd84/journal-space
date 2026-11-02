from uuid import UUID
from .domain import JournalEntry
from .repository import EntryRepository


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
