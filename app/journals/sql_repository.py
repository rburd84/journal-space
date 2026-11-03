from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain import (
    EntryStatus, JournalEntry, Journal, JournalType)
from .models import EntryModel, JournalModel


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


class SqlJournalRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, journal_id: UUID) -> Journal | None:
        model = self.session.get(JournalModel, journal_id)

        if model is None:
            return None

        return self._to_domain(model)

    def save(self, journal: Journal) -> None:
        model = self.session.get(JournalModel, journal.id)

        if model is None:
            model = JournalModel(id=journal.id)
            self.session.add(model)

        model.user_id = journal.user_id
        model.title = journal.title
        model.type = journal.type.value
        model.is_archived = journal.is_archived

        self.session.flush()

    def list_by_user(self, user_id: UUID) -> list[Journal]:
        models = self.session.scalars(
            select(JournalModel)
            .where(JournalModel.user_id == user_id)
            .order_by(JournalModel.title)
        ).all()

        return [self._to_domain(model) for model in models]

    @staticmethod
    def _to_domain(model: JournalModel) -> Journal:
        return Journal(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            type=JournalType(model.type),
            is_archived=model.is_archived,
        )


























