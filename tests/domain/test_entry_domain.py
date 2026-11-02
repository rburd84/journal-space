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


def test_update_title():
    entry = JournalEntry(
        journal_id=uuid4(),
        title="Original title",
        content="Original content",
    )

    original_updated_at = entry.updated_at

    entry.update_title("Updated title")

    assert entry.title == "Updated title"
    assert entry.content == "Original content"
    assert entry.updated_at >= original_updated_at


def test_update_content():
    entry = JournalEntry(
        journal_id=uuid4(),
        title="My day",
        content="Original content",
    )

    original_updated_at = entry.updated_at

    entry.update_content("Updated content")

    assert entry.content == "Updated content"
    assert entry.title == "My day"
    assert entry.updated_at >= original_updated_at


def test_publish_updates_timestamp():
    entry = JournalEntry(
        journal_id=uuid4(),
        title="Reflection",
        content="A meaningful reflection.",
    )

    original_updated_at = entry.updated_at
    entry.publish()

    assert entry.status == EntryStatus.PUBLISHED
    assert entry.updated_at >= original_updated_at


def test_toggle_favorite_twice():
    entry = JournalEntry(
        journal_id=uuid4(),
        title="Memory",
        content="A wonderful moment.",
    )

    entry.toggle_favorite()
    assert entry.is_favorite is True

    entry.toggle_favorite()
    assert entry.is_favorite is False
