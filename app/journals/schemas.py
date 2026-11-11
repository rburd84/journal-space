from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from .domain import JournalType

class JournalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    type: JournalType = JournalType.PERSONAL

class JournalResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    type: JournalType
    is_archived: bool

class JournalRename(BaseModel):
    title: str = Field(min_length=1, max_length=200)
