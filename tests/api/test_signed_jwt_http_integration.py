"""HTTP-level security tests with real RS256 verification and real SQLite ownership.

The signing key and users are test-only; no Clerk service or real user database is used.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.dependencies import get_db
from app.entries.models import EntryModel
from app.journals.models import JournalModel
from app.main import app
from app.users.invitations import InvitationModel
from app.users.models import UserModel

ISSUER = "https://test-clerk.example"
PARTY = "http://localhost:5173"


@pytest.fixture
def secure_client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        a = UserModel(clerk_user_id="clerk_account_a")
        b = UserModel(clerk_user_id="clerk_account_b")
        disabled = UserModel(clerk_user_id="clerk_disabled", is_active=False)
        session.add_all([a, b, disabled])
        session.flush()
        journal_a = JournalModel(user_id=a.id, title="A secret journal")
        journal_b = JournalModel(user_id=b.id, title="B secret journal")
        session.add_all([journal_a, journal_b])
        session.flush()
        entry_a = EntryModel(journal_id=journal_a.id, title="A secret", content="A private content")
        entry_b = EntryModel(journal_id=journal_b.id, title="B secret", content="B private content")
        session.add_all([entry_a, entry_b])
        session.commit()
        ids = {"journal_a": str(journal_a.id), "journal_b": str(journal_b.id),
               "entry_a": str(entry_a.id), "entry_b": str(entry_b.id)}

    def isolated_db():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def token(subject="clerk_account_a", *, key=None, issuer=ISSUER,
              party=PARTY, expired=False):
        now = datetime.now(timezone.utc)
        return jwt.encode({
            "sub": subject,
            "iss": issuer,
            "azp": party,
            "iat": now - timedelta(minutes=10) if expired else now,
            "exp": now - timedelta(minutes=5) if expired else now + timedelta(minutes=5),
        }, key or private_key, algorithm="RS256")

    def auth(subject="clerk_account_a", **kwargs):
        return {"Authorization": f"Bearer {token(subject, **kwargs)}"}

    app.dependency_overrides[get_db] = isolated_db
    try:
        with (
            patch("app.core.security.get_clerk_signing_key", return_value=private_key.public_key()),
            patch("app.core.security.get_clerk_issuer", return_value=ISSUER),
            patch("app.core.security.get_clerk_authorized_parties", return_value=[PARTY]),
            patch("app.users.service.get_verified_clerk_email", return_value="uninvited@example.test"),
            TestClient(app) as client,
        ):
            yield client, auth, ids, other_key
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_missing_and_invalid_jwt_rejected(secure_client):
    client, auth, _, other_key = secure_client
    assert client.get("/journals/").status_code == 401
    assert client.get("/journals/", headers={"Authorization": "Bearer not-a-jwt"}).status_code == 401
    for headers in (
        auth(key=other_key), auth(expired=True),
        auth(issuer="https://wrong.example"), auth(party="https://wrong.example"),
    ):
        assert client.get("/journals/", headers=headers).status_code == 401


def test_invitation_and_disabled_account_enforced_over_http(secure_client):
    client, auth, _, _ = secure_client
    assert client.get("/journals/", headers=auth("clerk_uninvited")).status_code == 403
    assert client.get("/journals/", headers=auth("clerk_disabled")).status_code == 403


def test_cross_account_read_write_and_delete_blocked(secure_client):
    client, auth, ids, _ = secure_client
    a, b = auth("clerk_account_a"), auth("clerk_account_b")
    assert client.get("/journals/", headers=a).status_code == 200
    assert client.get("/journals/", headers=b).status_code == 200
    assert [x["title"] for x in client.get("/journals/", headers=a).json()] == ["A secret journal"]
    assert [x["title"] for x in client.get("/journals/", headers=b).json()] == ["B secret journal"]

    for viewer, foreign_journal, foreign_entry in (
        (a, ids["journal_b"], ids["entry_b"]),
        (b, ids["journal_a"], ids["entry_a"]),
    ):
        requests = [
            client.get(f"/journals/{foreign_journal}", headers=viewer),
            client.patch(f"/journals/{foreign_journal}/rename", json={"title": "stolen"}, headers=viewer),
            client.patch(f"/journals/{foreign_journal}/archive", headers=viewer),
            client.patch(f"/journals/{foreign_journal}/restore", headers=viewer),
            client.get(f"/entries/?journal_id={foreign_journal}", headers=viewer),
            client.post("/entries/", json={"journal_id": foreign_journal, "title": "stolen", "content": "x"}, headers=viewer),
            client.get(f"/entries/{foreign_entry}", headers=viewer),
            client.patch(f"/entries/{foreign_entry}", json={"title": "stolen", "content": "x"}, headers=viewer),
            client.patch(f"/entries/{foreign_entry}/publish", headers=viewer),
            client.patch(f"/entries/{foreign_entry}/favorite", headers=viewer),
            client.delete(f"/entries/{foreign_entry}", headers=viewer),
        ]
        assert [response.status_code for response in requests] == [404] * len(requests)

    assert client.get(f"/entries/{ids['entry_a']}", headers=a).json()["content"] == "A private content"
    assert client.get(f"/entries/{ids['entry_b']}", headers=b).json()["content"] == "B private content"
    assert client.get(f"/journals/{ids['journal_a']}", headers=a).json()["title"] == "A secret journal"
    assert client.get(f"/journals/{ids['journal_b']}", headers=b).json()["title"] == "B secret journal"
