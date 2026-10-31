from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain import EntryStatus, JournalEntry
from .models import EntryModel


class SqlEntryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, entry_id: UUID) -> JournalEntry | None:
        model = self.session.get(EntryModel, entry_id)

        if model is None:
            return None

        return JournalEntry(
            id=model.id,
            journal_id=model.journal_id,
            title=model.title,
            content=model.content,
            status=EntryStatus(model.status),
            is_favorite=model.is_favorite,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, entry: JournalEntry) -> None:
        model = self.session.get(EntryModel, entry.id)

        if model is None:
            model = EntryModel(id=entry.id)
            self.session.add(model)

        model.journal_id = entry.journal_id
        model.title = entry.title
        model.content = entry.content
        model.status = entry.status.value
        model.is_favorite = entry.is_favorite
        model.created_at = entry.created_at
        model.updated_at = entry.updated_at

        self.session.flush()

    def list_by_journal(self, journal_id: UUID) -> list[JournalEntry]:
        models = self.session.scalars(
            select(EntryModel)
            .where(EntryModel.journal_id == journal_id)
        ).all()

        return [
            JournalEntry(
                id=m.id,
                journal_id=m.journal_id,
                title=m.title,
                content=m.content,
                status=EntryStatus(m.status),
                is_favorite=m.is_favorite,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]

