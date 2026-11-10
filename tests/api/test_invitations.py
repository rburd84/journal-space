import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import Base
from app.users.invitations import InvitationModel
from app.users.models import UserModel  # noqa: F401


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


def test_invitation_can_be_created(db_session):
    invitation = InvitationModel(email="tester@example.com")

    db_session.add(invitation)
    db_session.commit()

    saved = db_session.scalar(
        select(InvitationModel).where(
            InvitationModel.email == "tester@example.com"
        )
    )

    assert saved is not None
    assert saved.id is not None
    assert saved.redeemed_at is None
    assert saved.created_at is not None


def test_duplicate_invitation_email_is_rejected(db_session):
    db_session.add(InvitationModel(email="tester@example.com"))
    db_session.commit()

    db_session.add(InvitationModel(email="tester@example.com"))

    with pytest.raises(IntegrityError):
        db_session.commit()
