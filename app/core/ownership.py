from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entries.models import EntryModel
from app.journals.models import JournalModel


def require_owned_journal(
        db: Session,
        journal_id: UUID,
        user_id: UUID,
) -> JournalModel:
    journal = db.scalar(
        select(JournalModel).where(
            JournalModel.id == journal_id,
            JournalModel.user_id == user_id,
        )
    )

    if journal is None:
        raise HTTPException(
            status_code=404,
            detail="Journal not found",
        )

    return journal


def require_owned_entry(
        db: Session,
        entry_id: UUID,
        user_id: UUID,
) -> EntryModel:
    entry = db.scalar(
        select(EntryModel)
        .join(
            JournalModel,
            EntryModel.journal_id == JournalModel.id,
        )
        .where(
            EntryModel.id == entry_id,
            JournalModel.user_id == user_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return entry
