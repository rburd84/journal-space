from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.entries.domain import JournalEntry
from app.entries.sql_repository import SqlEntryRepository
from app.journals.models import JournalModel

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

Base.metadata.create_all(engine)

# Create a journal record
with Session(engine) as session:
    journal = JournalModel(
        id=uuid4(),
        user_id=uuid4(),
        title="Database Test Journal",
        type="personal",
        is_archived=False,
    )

    session.add(journal)
    session.commit()

    journal_id = journal.id

    print("Journal saved:", journal_id)

# Create and save a journal entry
with Session(engine) as session:
    repository = SqlEntryRepository(session)

    entry = JournalEntry(
        journal_id=journal_id,
        title="My First Database Entry",
        content="Testing SQLAlchemy persistence.",
    )

    repository.save(entry)
    session.commit()

    entry_id = entry.id

    print("Entry saved:", entry_id)

# Retrieve the entry in a new session
with Session(engine) as session:
    repository = SqlEntryRepository(session)

    saved_entry = repository.get(entry_id)

    assert saved_entry is not None

    print("Retrieved title:", saved_entry.title)
    print("Retrieved content:", saved_entry.content)
    print("Retrieved status:", saved_entry.status)

# Update the entry
with Session(engine) as session:
    repository = SqlEntryRepository(session)

    entry = repository.get(entry_id)
    assert entry is not None

    entry.update_content("This entry has been updated.")
    entry.publish()

    repository.save(entry)
    session.commit()

    print("Entry updated and published.")

# Verify the changes were saved
with Session(engine) as session:
    repository = SqlEntryRepository(session)

    entry = repository.get(entry_id)
    assert entry is not None

    print("Updated content:", entry.content)
    print("Updated status:", entry.status)

# List all entries in the journal
with Session(engine) as session:
    repository = SqlEntryRepository(session)

    entries = repository.list_by_journal(journal_id)

    print("Number of entries:", len(entries))

    for entry in entries:
        print("Entry:", entry.title)

print("\nDatabase testing is complete.")
