from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import Base
from app.users.invitations import InvitationModel
from app.users.models import UserModel


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, connection_record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    with Session(engine) as db:
        yield db

    engine.dispose()


def test_new_user_is_active_by_default(session):
    user = UserModel(clerk_user_id="user_test_1")
    session.add(user)
    session.commit()

    assert user.is_active is True


def test_user_can_be_deactivated_without_deletion(session):
    user = UserModel(clerk_user_id="user_test_2")
    session.add(user)
    session.commit()

    user_id = user.id
    user.is_active = False
    session.commit()

    saved_user = session.get(UserModel, user_id)

    assert saved_user is not None
    assert saved_user.is_active is False


def test_invitation_can_be_linked_to_user(session):
    user = UserModel(clerk_user_id="user_test_3")
    invitation = InvitationModel(email="tester@example.com")

    session.add_all([user, invitation])
    session.commit()

    invitation.redeemed_by_user_id = user.id
    invitation.redeemed_at = datetime.now(timezone.utc)
    session.commit()

    saved = session.scalar(
        select(InvitationModel).where(
            InvitationModel.email == "tester@example.com"
        )
    )

    assert saved.redeemed_by_user_id == user.id
    assert saved.redeemed_at is not None


def test_invitation_cannot_reference_unknown_user(session):
    invitation = InvitationModel(
        email="unknown@example.com",
        redeemed_by_user_id=uuid4(),
    )

    session.add(invitation)

    with pytest.raises(IntegrityError):
        session.commit()
