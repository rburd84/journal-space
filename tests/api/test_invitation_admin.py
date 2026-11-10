import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.users.admin import (
    invite,
    list_invitations,
    normalize_email,
    revoke,
)
from app.users.invitations import InvitationModel
from app.users.models import UserModel  # noqa: F401


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        yield db

    engine.dispose()


def test_email_normalization():
    assert (
            normalize_email("  Tester@Example.COM ")
            == "tester@example.com"
    )


@pytest.mark.parametrize(
    "email",
    [
        "",
        "not-an-email",
        "@example.com",
        "tester@",
        "tester@example",
        "two words@example.com",
    ],
)
def test_invalid_email_rejected(email):
    with pytest.raises(ValueError):
        normalize_email(email)


def test_invite_creates_pending_invitation(session):
    result = invite(session, "Tester@Example.com")

    assert result == "Invitation created: tester@example.com"
    assert list_invitations(session) == [
        "tester@example.com | pending"
    ]


def test_duplicate_invite_is_idempotent(session):
    invite(session, "tester@example.com")

    result = invite(session, "TESTER@example.com")

    assert result == "Invitation already exists"
    assert len(list_invitations(session)) == 1


def test_revoke_invitation(session):
    invite(session, "tester@example.com")

    result = revoke(session, "tester@example.com")

    assert result == "Invitation revoked: tester@example.com"
    assert list_invitations(session) == [
        "tester@example.com | revoked"
    ]


def test_reinvite_restores_revoked_invitation(session):
    invite(session, "tester@example.com")
    revoke(session, "tester@example.com")

    result = invite(session, "tester@example.com")

    assert result == "Invitation restored: tester@example.com"
    assert list_invitations(session) == [
        "tester@example.com | pending"
    ]


def test_redeemed_invitation_cannot_be_revoked(session):
    invite(session, "tester@example.com")

    invitation = session.query(InvitationModel).first()
    from datetime import datetime, timezone

    invitation.redeemed_at = datetime.now(timezone.utc)
    session.commit()

    result = revoke(session, "tester@example.com")

    assert "Disable the user account" in result
    assert list_invitations(session) == [
        "tester@example.com | redeemed"
    ]


def test_revoke_unknown_invitation(session):
    assert revoke(session, "missing@example.com") == (
        "Invitation not found"
    )
