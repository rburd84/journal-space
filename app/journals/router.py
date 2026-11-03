from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from .schemas import (
    EntryCreate, EntryResponse, EntryUpdate,
    JournalCreate, JournalResponse)
from .service import EntryService, JournalService
from .sql_repository import SqlEntryRepository, SqlJournalRepository
from uuid import UUID

router = APIRouter(prefix="/entries", tags=["entries"])

journals_router = APIRouter(
    prefix="/journals",
    tags=["journals"],
)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


@router.post("/", response_model=EntryResponse, status_code=201, )
def create_entry(
        data: EntryCreate,
        db: Session = Depends(get_db),
):
    # Development example only:
    # Authenticate and verify journal ownership
    # before allowing this operation.
    repository = SqlEntryRepository(db)
    service = EntryService(repository)

    entry = service.create_entry(
        journal_id=data.journal_id,
        title=data.title,
        content=data.content,
    )

    db.commit()
    return entry


@router.get("/", response_model=list[EntryResponse])
def list_entries(
        journal_id: UUID,
        db: Session = Depends(get_db),
):
    # Development only:
    # Verify the requesting user's ownership of this journal
    # before exposing entries in production.
    repository = SqlEntryRepository(db)
    service = EntryService(repository)

    return service.list_entries_by_journal(journal_id)


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry(
        entry_id: UUID,
        db: Session = Depends(get_db),
):
    repository = SqlEntryRepository(db)

    entry = repository.get(entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return entry


@router.patch(
    "/{entry_id}/publish",
    response_model=EntryResponse,
)
def publish_entry(
        entry_id: UUID,
        db: Session = Depends(get_db),
):
    # Development only:
    # Authenticate the user and verify journal ownership
    # before allowing publication in production.
    repository = SqlEntryRepository(db)
    service = EntryService(repository)

    entry = repository.get(entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    published_entry = service.publish_entry(entry_id)

    db.commit()
    return published_entry


@router.patch("/{entry_id}", response_model=EntryResponse)
def update_entry(
        entry_id: UUID,
        data: EntryUpdate,
        db: Session = Depends(get_db),
):
    # Development only:
    # Authenticate and verify journal ownership
    # before allowing updates in production.
    repository = SqlEntryRepository(db)
    service = EntryService(repository)

    entry = repository.get(entry_id)
    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    updated_entry = service.update_entry(
        entry_id=entry_id,
        title=data.title,
        content=data.content,
    )
    db.commit()
    return updated_entry


@journals_router.post(
    "/",
    response_model=JournalResponse,
    status_code=201,
)
def create_journal(
        data: JournalCreate,
        db: Session = Depends(get_db),
):
    service = JournalService(SqlJournalRepository(db))

    try:
        journal = service.create_journal(
            user_id=data.user_id,
            title=data.title,
            journal_type=data.type,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    db.commit()
    return journal


@journals_router.get(
    "/",
    response_model=list[JournalResponse],
)
def list_journals(
        user_id: UUID,
        db: Session = Depends(get_db),
):
    service = JournalService(SqlJournalRepository(db))
    return service.list_journals(user_id)


@journals_router.get(
    "/{journal_id}",
    response_model=JournalResponse,
)
def get_journal(
        journal_id: UUID,
        db: Session = Depends(get_db),
):
    service = JournalService(SqlJournalRepository(db))
    journal = service.get_journal(journal_id)

    if journal is None:
        raise HTTPException(
            status_code=404,
            detail="Journal not found",
        )

    return journal
