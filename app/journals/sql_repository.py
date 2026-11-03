from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain import Journal, JournalType
from .models import JournalModel


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
