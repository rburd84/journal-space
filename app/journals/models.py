from uuid import UUID, uuid4

from sqlalchemy import (
    String, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class JournalModel(Base):
    __tablename__ = 'journals'

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
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
