from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from .schemas import EntryCreate, EntryResponse
from .service import EntryService
from .sql_repository import SqlEntryRepository
from uuid import UUID

router = APIRouter(prefix="/entries", tags=["entries"])


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
