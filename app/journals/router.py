from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from .schemas import EntryCreate, EntryResponse
from .service import EntryService
from .sql_repository import SqlEntryRepository


router = APIRouter(prefix="/entries", tags=["entries"])


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


@router.post("/", response_model=EntryResponse, status_code=201,)
def create_entry(
        data: EntryCreate,
        db: Session = Depends(get_db),
):
    # Development example only:
    # Authenticate and verify journal ownership
    # before allowing this operation.
    repository = SqlEntryRepository(db)
    service = EntryService(repository)

    entry = service.create_entry(
        journal_id=data.journal_id,
        title=data.title,
        content=data.content,
    )

    db.commit()
    return entry
