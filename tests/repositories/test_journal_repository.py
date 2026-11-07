from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.journals.domain import Journal, JournalType
from app.journals.models import JournalModel
from app.journals.sql_repository import SqlJournalRepository


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create only the table under test, not the application's other tables.
    JournalModel.__table__.create(engine)
    try:
        with Session(engine) as db:
            yield db
    finally:
        engine.dispose()


@pytest.fixture
def repository(session):
    return SqlJournalRepository(session)


def test_save_and_get_journal(repository):
    journal = Journal(user_id=uuid4(), title="Daily Notes")
    repository.save(journal)

    loaded = repository.get(journal.id)
    assert loaded is not None
    assert loaded.id == journal.id
    assert loaded.user_id == journal.user_id
    assert loaded.title == "Daily Notes"
    assert loaded.type == JournalType.PERSONAL
    assert loaded.is_archived is False


def test_get_missing_journal_returns_none(repository):
    assert repository.get(uuid4()) is None


def test_save_preserves_nondefault_type(repository):
    journal = Journal(user_id=uuid4(), title="Thanks", type=JournalType.GRATITUDE)
    repository.save(journal)
    assert repository.get(journal.id).type == JournalType.GRATITUDE


def test_save_updates_existing_journal_without_duplicate(repository, session):
    journal = Journal(user_id=uuid4(), title="Old")
    repository.save(journal)
    journal.rename("New")
    repository.save(journal)

    assert repository.get(journal.id).title == "New"
    assert session.query(JournalModel).count() == 1


def test_archive_state_persists(repository):
    journal = Journal(user_id=uuid4(), title="Notes")
    repository.save(journal)
    journal.archive()
    repository.save(journal)
    assert repository.get(journal.id).is_archived is True


def test_restore_state_persists(repository):
    journal = Journal(user_id=uuid4(), title="Notes", is_archived=True)
    repository.save(journal)
    journal.restore()
    repository.save(journal)
    assert repository.get(journal.id).is_archived is False


def test_list_by_user_only_returns_that_users_journals(repository):
    owner = uuid4()
    other = uuid4()
    own = Journal(user_id=owner, title="Mine")
    repository.save(own)
    repository.save(Journal(user_id=other, title="Someone Else"))

    result = repository.list_by_user(owner)
    assert [journal.id for journal in result] == [own.id]


def test_list_by_user_returns_empty_for_unknown_user(repository):
    repository.save(Journal(user_id=uuid4(), title="Existing"))
    assert repository.list_by_user(uuid4()) == []


def test_list_by_user_orders_by_title(repository):
    owner = uuid4()
    for title in ("Zebra", "Apple", "Middle"):
        repository.save(Journal(user_id=owner, title=title))
    assert [journal.title for journal in repository.list_by_user(owner)] == [
        "Apple", "Middle", "Zebra"
    ]


def test_list_by_user_includes_archived_journals(repository):
    owner = uuid4()
    repository.save(Journal(user_id=owner, title="Archived", is_archived=True))
    result = repository.list_by_user(owner)
    assert len(result) == 1
    assert result[0].is_archived is True


def test_saved_journal_survives_new_session_on_same_engine(session):
    repository = SqlJournalRepository(session)
    journal = Journal(user_id=uuid4(), title="Persistent")
    repository.save(journal)
    session.commit()

    with Session(session.get_bind()) as second_session:
        loaded = SqlJournalRepository(second_session).get(journal.id)
        assert loaded is not None
        assert loaded.title == "Persistent"
