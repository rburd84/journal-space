from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_clerk_token
from app.users.models import UserModel
from app.users.service import resolve_current_user

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def get_clerk_user_id(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(bearer_scheme),
        ],
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = verify_clerk_token(credentials.credentials)
    return claims["sub"]


def get_current_user(
        clerk_user_id: Annotated[
            str,
            Depends(get_clerk_user_id),
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ],
) -> UserModel:
    return resolve_current_user(
        session=db,
        clerk_user_id=clerk_user_id,
    )
