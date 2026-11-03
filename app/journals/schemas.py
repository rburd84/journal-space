from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from .domain import EntryStatus, JournalType


class EntryCreate(BaseModel):
    journal_id: UUID
    title: str = Field(min_length=1, max_length=200)
    content: str = ""


class EntryUpdate(BaseModel):
    title: str
    content: str


class EntryResponse(BaseModel):
    id: UUID
    journal_id: UUID
    title: str
    content: str
    status: EntryStatus
    is_favorite: bool
    created_at: datetime
    updated_at: datetime


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