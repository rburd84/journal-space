from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime, ForeignKey, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class JournalModel(Base):
    __tablename__ = 'journals'

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200)
    )

    type: Mapped[str] = mapped_column(
        String(30), default="personal"
    )

    is_archived: Mapped[bool] = mapped_column(
        default=False
    )

class EntryModel(Base):
    __tablename__ = 'journal_entries'

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )

    journal_id: Mapped[UUID] = mapped_column(
        ForeignKey("journals.id"),
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200)
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    status: Mapped[str] = mapped_column(
        String(20), default="draft"
    )

    is_favorite: Mapped[bool] = mapped_column(
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
