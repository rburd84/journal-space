from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .schemas import JournalCreate, JournalResponse, JournalRename
from .service import JournalService, JournalNotFoundError
from .sql_repository import SqlJournalRepository
from ..core.dependencies import get_db, get_current_user
from app.core.ownership import require_owned_journal
from app.users.models import UserModel

router = APIRouter(
    prefix="/journals",
    tags=["journals"],
)


@router.post(
    "/",
    response_model=JournalResponse,
    status_code=201,
)
def create_journal(
        data: JournalCreate,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    if data.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create a journal for another user",
        )

    service = JournalService(SqlJournalRepository(db))

    try:
        journal = service.create_journal(
            user_id=current_user.id,
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


@router.get(
    "/",
    response_model=list[JournalResponse],
)
def list_journals(
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    service = JournalService(SqlJournalRepository(db))
    return service.list_journals(current_user.id)


@router.get(
    "/{journal_id}",
    response_model=JournalResponse,
)
def get_journal(
        journal_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_journal(db, journal_id, current_user.id)

    service = JournalService(SqlJournalRepository(db))
    journal = service.get_journal(journal_id)

    if journal is None:
        raise HTTPException(
            status_code=404,
            detail="Journal not found",
        )

    return journal


@router.patch(
    "/{journal_id}/rename",
    response_model=JournalResponse,
)
def rename_journal(
        journal_id: UUID,
        data: JournalRename,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_journal(db, journal_id, current_user.id)

    service = JournalService(SqlJournalRepository(db))

    try:
        journal = service.rename_journal(
            journal_id,
            data.title,
        )
    except JournalNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Journal not found",
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    db.commit()
    return journal


@router.patch(
    "/{journal_id}/archive",
    response_model=JournalResponse,
)
def archive_journal(
        journal_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_journal(db, journal_id, current_user.id)

    service = JournalService(SqlJournalRepository(db))

    try:
        journal = service.archive_journal(journal_id)
    except JournalNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Journal not found",
        )

    db.commit()
    return journal


@router.patch(
    "/{journal_id}/restore",
    response_model=JournalResponse,
)
def restore_journal(
        journal_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    require_owned_journal(db, journal_id, current_user.id)

    service = JournalService(SqlJournalRepository(db))

    try:
        journal = service.restore_journal(journal_id)
    except JournalNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Journal not found",
        )

    db.commit()
    return journal
