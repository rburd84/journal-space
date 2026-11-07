from uuid import UUID, uuid4

import pytest

from app.journals.domain import Journal, JournalType


def test_new_journal_has_expected_defaults():
    user_id = uuid4()
    journal = Journal(user_id=user_id, title="Daily reflections")

    assert isinstance(journal.id, UUID)
    assert journal.user_id == user_id
    assert journal.title == "Daily reflections"
    assert journal.type == JournalType.PERSONAL
    assert journal.is_archived is False


def test_new_journals_receive_distinct_ids():
    user_id = uuid4()
    first = Journal(user_id=user_id, title="First")
    second = Journal(user_id=user_id, title="Second")

    assert first.id != second.id


def test_journal_accepts_explicit_type():
    journal = Journal(user_id=uuid4(), title="Grateful moments", type=JournalType.GRATITUDE)

    assert journal.type == JournalType.GRATITUDE


def test_rename_trims_surrounding_whitespace():
    journal = Journal(user_id=uuid4(), title="Original")

    journal.rename("  Updated title  ")

    assert journal.title == "Updated title"


@pytest.mark.parametrize("invalid_title", ["", " ", "\t\n"])
def test_rename_rejects_blank_titles_without_changing_existing_title(invalid_title):
    journal = Journal(user_id=uuid4(), title="Original")

    with pytest.raises(ValueError, match="Journal title is required"):
        journal.rename(invalid_title)

    assert journal.title == "Original"


def test_archive_marks_journal_archived():
    journal = Journal(user_id=uuid4(), title="Reflections")

    journal.archive()

    assert journal.is_archived is True


def test_restore_marks_journal_active():
    journal = Journal(user_id=uuid4(), title="Reflections")
    journal.archive()

    journal.restore()

    assert journal.is_archived is False


def test_archiving_and_restoring_preserve_journal_identity_and_content():
    journal = Journal(user_id=uuid4(), title="Dreams", type=JournalType.DREAM)
    original = (journal.id, journal.user_id, journal.title, journal.type)

    journal.archive()
    journal.restore()

    assert (journal.id, journal.user_id, journal.title, journal.type) == original
