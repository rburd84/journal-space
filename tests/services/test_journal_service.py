from uuid import uuid4

import pytest

from app.journals.domain import Journal, JournalType
from app.journals.service import JournalNotFoundError, JournalService


class FakeJournalRepository:
    def __init__(self):
        self.journals = {}
        self.save_calls = 0

    def get(self, journal_id):
        return self.journals.get(journal_id)

    def save(self, journal):
        self.journals[journal.id] = journal
        self.save_calls += 1

    def list_by_user(self, user_id):
        return [journal for journal in self.journals.values() if journal.user_id == user_id]


def test_create_journal_trims_title_and_saves():
    repository = FakeJournalRepository()
    service = JournalService(repository)
    user_id = uuid4()

    journal = service.create_journal(user_id, "  Morning pages  ")

    assert journal.user_id == user_id
    assert journal.title == "Morning pages"
    assert journal.type == JournalType.PERSONAL
    assert repository.get(journal.id) is journal
    assert repository.save_calls == 1


def test_create_journal_with_explicit_type():
    service = JournalService(FakeJournalRepository())

    journal = service.create_journal(uuid4(), "Thanks", JournalType.GRATITUDE)

    assert journal.type == JournalType.GRATITUDE


@pytest.mark.parametrize("title", ["", "   ", "\n\t"])
def test_create_journal_rejects_blank_title_without_saving(title):
    repository = FakeJournalRepository()
    service = JournalService(repository)

    with pytest.raises(ValueError, match="Journal title is required"):
        service.create_journal(uuid4(), title)

    assert repository.journals == {}
    assert repository.save_calls == 0


def test_get_journal_returns_existing_journal():
    repository = FakeJournalRepository()
    journal = Journal(user_id=uuid4(), title="Notes")
    repository.save(journal)

    assert JournalService(repository).get_journal(journal.id) is journal


def test_get_journal_returns_none_when_missing():
    assert JournalService(FakeJournalRepository()).get_journal(uuid4()) is None


def test_list_journals_returns_only_requested_users_journals():
    repository = FakeJournalRepository()
    user_id = uuid4()
    own = Journal(user_id=user_id, title="Mine")
    archived = Journal(user_id=user_id, title="Archived", is_archived=True)
    other = Journal(user_id=uuid4(), title="Other")
    for journal in (own, archived, other):
        repository.save(journal)

    result = JournalService(repository).list_journals(user_id)

    assert {journal.id for journal in result} == {own.id, archived.id}


def test_rename_journal_trims_title_and_saves():
    repository = FakeJournalRepository()
    journal = Journal(user_id=uuid4(), title="Old")
    repository.save(journal)
    service = JournalService(repository)
    original_id, original_user_id = journal.id, journal.user_id

    renamed = service.rename_journal(journal.id, "  New  ")

    assert renamed is journal
    assert renamed.title == "New"
    assert renamed.id == original_id
    assert renamed.user_id == original_user_id
    assert repository.save_calls == 2


def test_rename_journal_rejects_blank_title_without_saving():
    repository = FakeJournalRepository()
    journal = Journal(user_id=uuid4(), title="Original")
    repository.save(journal)

    with pytest.raises(ValueError, match="Journal title is required"):
        JournalService(repository).rename_journal(journal.id, "  ")

    assert journal.title == "Original"
    assert repository.save_calls == 1


def test_archive_journal_saves_archived_state():
    repository = FakeJournalRepository()
    journal = Journal(user_id=uuid4(), title="Notes")
    repository.save(journal)

    result = JournalService(repository).archive_journal(journal.id)

    assert result is journal
    assert journal.is_archived is True
    assert repository.save_calls == 2


def test_restore_journal_saves_active_state():
    repository = FakeJournalRepository()
    journal = Journal(user_id=uuid4(), title="Notes", is_archived=True)
    repository.save(journal)

    result = JournalService(repository).restore_journal(journal.id)

    assert result is journal
    assert journal.is_archived is False
    assert repository.save_calls == 2


@pytest.mark.parametrize("operation", ["rename", "archive", "restore"])
def test_mutation_of_missing_journal_raises_without_saving(operation):
    repository = FakeJournalRepository()
    service = JournalService(repository)
    missing_id = uuid4()

    with pytest.raises(JournalNotFoundError):
        if operation == "rename":
            service.rename_journal(missing_id, "New")
        elif operation == "archive":
            service.archive_journal(missing_id)
        else:
            service.restore_journal(missing_id)

    assert repository.save_calls == 0
