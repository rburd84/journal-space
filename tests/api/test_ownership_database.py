from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.ownership import require_owned_entry, require_owned_journal
from app.entries.models import EntryModel
from app.journals.models import JournalModel


@pytest.fixture
def ownership_db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create only the two tables needed for ownership checks.
    Base.metadata.create_all(
        bind=engine,
        tables=[JournalModel.__table__, EntryModel.__table__],
    )
    try:
        with Session(engine) as db:
            account_a, account_b = uuid4(), uuid4()
            journal_a = JournalModel(user_id=account_a, title="A private journal")
            journal_b = JournalModel(user_id=account_b, title="B private journal")
            db.add_all([journal_a, journal_b])
            db.flush()
            entry_a = EntryModel(
                journal_id=journal_a.id,
                title="A private entry",
                content="Private content belonging to A",
            )
            entry_b = EntryModel(
                journal_id=journal_b.id,
                title="B private entry",
                content="Private content belonging to B",
            )
            db.add_all([entry_a, entry_b])
            db.commit()
            yield db, account_a, account_b, journal_a, journal_b, entry_a, entry_b
    finally:
        engine.dispose()


def test_journal_owner_can_read(ownership_db):
    db, a, b, journal_a, journal_b, entry_a, entry_b = ownership_db
    assert require_owned_journal(db, journal_a.id, a).id == journal_a.id
    assert require_owned_journal(db, journal_b.id, b).id == journal_b.id


def test_other_account_cannot_read_journal(ownership_db):
    db, a, b, journal_a, journal_b, entry_a, entry_b = ownership_db
    with pytest.raises(HTTPException) as exc:
        require_owned_journal(db, journal_a.id, b)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Journal not found"
    assert db.scalar(select(JournalModel).where(JournalModel.id == journal_a.id)).title == "A private journal"


def test_missing_journal_returns_404(ownership_db):
    db, a, *_ = ownership_db
    with pytest.raises(HTTPException) as exc:
        require_owned_journal(db, uuid4(), a)
    assert exc.value.status_code == 404


def test_entry_owner_can_read(ownership_db):
    db, a, b, journal_a, journal_b, entry_a, entry_b = ownership_db
    assert require_owned_entry(db, entry_a.id, a).id == entry_a.id
    assert require_owned_entry(db, entry_b.id, b).id == entry_b.id


def test_other_account_cannot_read_entry(ownership_db):
    db, a, b, journal_a, journal_b, entry_a, entry_b = ownership_db
    with pytest.raises(HTTPException) as exc:
        require_owned_entry(db, entry_a.id, b)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Entry not found"
    assert db.scalar(select(EntryModel).where(EntryModel.id == entry_a.id)).content == "Private content belonging to A"


def test_missing_entry_returns_404(ownership_db):
    db, a, *_ = ownership_db
    with pytest.raises(HTTPException) as exc:
        require_owned_entry(db, uuid4(), a)
    assert exc.value.status_code == 404


def test_journal_and_entry_checks_reject_both_directions(ownership_db):
    db, a, b, journal_a, journal_b, entry_a, entry_b = ownership_db
    for journal, wrong_user in [(journal_a, b), (journal_b, a)]:
        with pytest.raises(HTTPException) as exc:
            require_owned_journal(db, journal.id, wrong_user)
        assert exc.value.status_code == 404
    for entry, wrong_user in [(entry_a, b), (entry_b, a)]:
        with pytest.raises(HTTPException) as exc:
            require_owned_entry(db, entry.id, wrong_user)
        assert exc.value.status_code == 404
