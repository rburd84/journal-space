from uuid import UUID

from pydantic import BaseModel

from .domain import JournalType


class JournalCreate(BaseModel):
    user_id: UUID
    title: str
    type: JournalType = JournalType.PERSONAL


class JournalResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    type: JournalType
    is_archived: bool
