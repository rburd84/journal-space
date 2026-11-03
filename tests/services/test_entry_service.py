from uuid import uuid4
import pytest
from app.journals.domain import JournalEntry
from app.journals.service import EntryService, EntryNotFoundError


class FakeEntryRepository:
    def __init__(self):
        self.entries = {}

    def get(self, entry_id):
        return self.entries.get(entry_id)

    def save(self, entry):
        self.entries[entry.id] = entry

    def list_by_journal(self, journal_id):
        return [
            entry
            for entry in self.entries.values()
            if entry.journal_id == journal_id
        ]


def test_update_existing_entry():
    repository = FakeEntryRepository()
    service = EntryService(repository)

    entry = JournalEntry(
        journal_id=uuid4(),
        title="Original title",
        content="Original content",
    )

    repository.save(entry)
    original_id = entry.id

    updated_entry = service.update_entry(
        entry_id=entry.id,
        title="Updated title",
        content="Updated content",
    )

    assert updated_entry.id == original_id
    assert updated_entry.title == "Updated title"
    assert updated_entry.content == "Updated content"
    assert len(repository.entries) == 1


def test_update_nonexistent_entry():
    repository = FakeEntryRepository()
    service = EntryService(repository)

    missing_id = uuid4()

    with pytest.raises(EntryNotFoundError):
        service.update_entry(
            entry_id=missing_id,
            title="New title",
            content="New content",
        )
