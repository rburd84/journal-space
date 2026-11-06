from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .schemas import (
    EntryCreate, EntryResponse, EntryUpdate)
from .service import EntryService, EntryNotFoundError
from .sql_repository import SqlEntryRepository
from ..core.dependencies import get_db

router = APIRouter(
    prefix="/entries",
    tags=["entries"],
)


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


@router.patch(
    "/{entry_id}/favorite",
    response_model=EntryResponse,
)
def toggle_entry_favorite(
        entry_id: UUID,
        db: Session = Depends(get_db),
):
    # Development only:
    # Authenticate and verify journal ownership
    # before enabling this endpoint in production.
    repository = SqlEntryRepository(db)
    service = EntryService(repository)

    try:
        entry = service.toggle_favorite(entry_id)
    except EntryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    db.commit()
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(
        entry_id: UUID,
        db: Session = Depends(get_db),
):
    # Development only:
    # Authenticate and verify journal ownership
    # before enabling this endpoint in production.
    repository = SqlEntryRepository(db)
    service = EntryService(repository)

    try:
        service.delete_entry(entry_id)
    except EntryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    db.commit()
