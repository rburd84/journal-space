from uuid import uuid4

import pytest

from app.journals.domain import (
    EntryStatus,
    JournalEntry,
)


def test_new_entry_is_draft():
    entry = JournalEntry(
        journal_id=uuid4(),
        title="My day",
        content="Today was great!",
    )

    assert entry.status == EntryStatus.DRAFT


def test_entry_can_be_published():
    entry = JournalEntry(
        journal_id=uuid4(),
        title="My day",
        content="I learned something new.",
    )

    entry.publish()

    assert entry.status == EntryStatus.PUBLISHED


def test_empty_entry_cannot_be_published():
    entry = JournalEntry(
        journal_id=uuid4(),
        title="Empty",
        content="",
    )

    with pytest.raises(ValueError):
        entry.publish()


def test_entry_can_be_favorited():
    entry = JournalEntry(
        journal_id=uuid4(),
        title="Memory",
        content="A wonderful moment.",
    )

    entry.toggle_favorite()

    assert entry.is_favorite is True
