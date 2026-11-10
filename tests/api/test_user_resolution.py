from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.users.invitations import InvitationModel
from app.users.models import UserModel
from app.users.service import resolve_current_user


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


def test_existing_active_user_is_allowed(session):
    user = UserModel(
        clerk_user_id="user_existing",
    )

    session.add(user)
    session.commit()

    with patch(
            "app.users.service.get_verified_clerk_email"
    ) as lookup:
        resolved = resolve_current_user(
            session,
            "user_existing",
        )

    assert resolved.id == user.id
    lookup.assert_not_called()


def test_disabled_user_is_rejected(session):
    user = UserModel(
        clerk_user_id="user_disabled",
        is_active=False,
    )

    session.add(user)
    session.commit()

    with pytest.raises(HTTPException) as exc:
        resolve_current_user(
            session,
            "user_disabled",
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Account disabled"


def test_invited_user_is_provisioned(session):
    invitation = InvitationModel(
        email="tester@example.com",
    )

    session.add(invitation)
    session.commit()

    with patch(
            "app.users.service.get_verified_clerk_email",
            return_value="tester@example.com",
    ):
        user = resolve_current_user(
            session,
            "user_invited",
        )

    assert user.clerk_user_id == "user_invited"
    assert user.is_active is True

    saved_invitation = session.scalar(
        select(InvitationModel).where(
            InvitationModel.email == "tester@example.com"
        )
    )

    assert saved_invitation.redeemed_by_user_id == user.id
    assert saved_invitation.redeemed_at is not None


def test_uninvited_user_is_rejected(session):
    with patch(
            "app.users.service.get_verified_clerk_email",
            return_value="unknown@example.com",
    ):
        with pytest.raises(HTTPException) as exc:
            resolve_current_user(
                session,
                "user_unknown",
            )

    assert exc.value.status_code == 403


def test_revoked_invitation_is_rejected(session):
    invitation = InvitationModel(
        email="revoked@example.com",
        revoked_at=datetime.now(timezone.utc),
    )

    session.add(invitation)
    session.commit()

    with patch(
            "app.users.service.get_verified_clerk_email",
            return_value="revoked@example.com",
    ):
        with pytest.raises(HTTPException) as exc:
            resolve_current_user(
                session,
                "user_revoked",
            )

    assert exc.value.status_code == 403


def test_redeemed_invitation_cannot_be_reused(session):
    existing_user = UserModel(
        clerk_user_id="user_original",
    )

    session.add(existing_user)
    session.flush()

    invitation = InvitationModel(
        email="used@example.com",
        redeemed_at=datetime.now(timezone.utc),
        redeemed_by_user_id=existing_user.id,
    )

    session.add(invitation)
    session.commit()

    with patch(
            "app.users.service.get_verified_clerk_email",
            return_value="used@example.com",
    ):
        with pytest.raises(HTTPException) as exc:
            resolve_current_user(
                session,
                "user_different",
            )

    assert exc.value.status_code == 403


def test_existing_user_does_not_redeem_another_invitation(session):
    user = UserModel(
        clerk_user_id="user_existing",
    )

    invitation = InvitationModel(
        email="another@example.com",
    )

    session.add_all([user, invitation])
    session.commit()

    with patch(
            "app.users.service.get_verified_clerk_email"
    ) as lookup:
        resolved = resolve_current_user(
            session,
            "user_existing",
        )

    assert resolved.id == user.id
    lookup.assert_not_called()

    saved_invitation = session.scalar(
        select(InvitationModel).where(
            InvitationModel.email == "another@example.com"
        )
    )

    assert saved_invitation.redeemed_at is None
    assert saved_invitation.redeemed_by_user_id is None
