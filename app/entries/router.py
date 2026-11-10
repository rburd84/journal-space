from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.ownership import (
    require_owned_entry,
    require_owned_journal,
)
from app.users.models import UserModel
from .schemas import EntryCreate, EntryResponse, EntryUpdate
from .service import EntryService, EntryNotFoundError
from .sql_repository import SqlEntryRepository

router = APIRouter(
    prefix="/entries",
    tags=["entries"],
)


@router.post(
    "/",
    response_model=EntryResponse,
    status_code=201,
)
def create_entry(
        data: EntryCreate,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_journal(
        db,
        data.journal_id,
        current_user.id,
    )

    service = EntryService(SqlEntryRepository(db))

    entry = service.create_entry(
        journal_id=data.journal_id,
        title=data.title,
        content=data.content,
    )

    db.commit()
    return entry


@router.get(
    "/",
    response_model=list[EntryResponse],
)
def list_entries(
        journal_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_journal(
        db,
        journal_id,
        current_user.id,
    )

    service = EntryService(SqlEntryRepository(db))

    return service.list_entries_by_journal(journal_id)


@router.get(
    "/{entry_id}",
    response_model=EntryResponse,
)
def get_entry(
        entry_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_entry(
        db,
        entry_id,
        current_user.id,
    )

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
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_entry(
        db,
        entry_id,
        current_user.id,
    )

    service = EntryService(SqlEntryRepository(db))

    try:
        entry = service.publish_entry(entry_id)
    except EntryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    db.commit()
    return entry


@router.patch(
    "/{entry_id}",
    response_model=EntryResponse,
)
def update_entry(
        entry_id: UUID,
        data: EntryUpdate,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_entry(
        db,
        entry_id,
        current_user.id,
    )

    service = EntryService(SqlEntryRepository(db))

    try:
        entry = service.update_entry(
            entry_id=entry_id,
            title=data.title,
            content=data.content,
        )
    except EntryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    db.commit()
    return entry


@router.patch(
    "/{entry_id}/favorite",
    response_model=EntryResponse,
)
def toggle_entry_favorite(
        entry_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_entry(
        db,
        entry_id,
        current_user.id,
    )

    service = EntryService(SqlEntryRepository(db))

    try:
        entry = service.toggle_favorite(entry_id)
    except EntryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    db.commit()
    return entry


@router.delete(
    "/{entry_id}",
    status_code=204,
)
def delete_entry(
        entry_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_entry(
        db,
        entry_id,
        current_user.id,
    )

    service = EntryService(SqlEntryRepository(db))

    try:
        service.delete_entry(entry_id)
    except EntryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    db.commit()
