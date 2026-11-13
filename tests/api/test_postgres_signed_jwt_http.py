"""Opt-in PostgreSQL HTTP security checks.

Run with TEST_DATABASE_URL pointing to the disposable stillspace_test database.
Creates and drops only a random, test-owned schema. Never run against production.
"""
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import jwt
import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.entries.models import EntryModel
from app.journals.models import JournalModel
from app.main import app
from app.users.invitations import InvitationModel
from app.users.models import UserModel

ISSUER = "https://test-clerk.example"
PARTY = "http://localhost:5173"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def postgres_engine():
    url = os.getenv("TEST_DATABASE_URL", "").strip()
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL HTTP tests")

    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or parsed.database != "stillspace_test":
        pytest.fail("TEST_DATABASE_URL must point to PostgreSQL database stillspace_test")
    if parsed.host not in ("localhost", "127.0.0.1", "::1"):
        pytest.fail("PostgreSQL integration tests require a local database")
    if os.getenv("STILLSPACE_ENV", "").lower() == "production":
        pytest.fail("PostgreSQL integration tests are forbidden in production mode")

    schema = "stillspace_http_test_" + uuid4().hex
    admin_engine = create_engine(url)
    schema_created = False
    try:
        with admin_engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            schema_created = True

        # PGOPTIONS applies to new PostgreSQL connections opened by Alembic and SQLAlchemy.
        # Using an isolated search_path prevents migration writes to existing public tables.
        with patch.dict(os.environ, {"DATABASE_URL": url, "PGOPTIONS": f"-csearch_path={schema}"}):
            config = Config(str(ROOT / "alembic.ini"))
            command.upgrade(config, "head")
            engine = create_engine(url)
            try:
                with engine.connect() as conn:
                    assert conn.scalar(text("SELECT current_schema()")) == schema
                    assert conn.scalar(text("SELECT count(*) FROM alembic_version")) == 1
                yield engine
            finally:
                engine.dispose()
    finally:
        if schema_created:
            with admin_engine.begin() as conn:
                conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin_engine.dispose()


@pytest.fixture
def pg_client(postgres_engine):
    engine = postgres_engine
    with Session(engine) as session:
        session.execute(text("TRUNCATE TABLE journal_entries, journals, invitations, users RESTART IDENTITY CASCADE"))
        a = UserModel(clerk_user_id="pg_account_a")
        b = UserModel(clerk_user_id="pg_account_b")
        disabled = UserModel(clerk_user_id="pg_disabled", is_active=False)
        session.add_all([a, b, disabled])
        session.flush()
        journal_a = JournalModel(user_id=a.id, title="A private journal")
        journal_b = JournalModel(user_id=b.id, title="B private journal")
        session.add_all([journal_a, journal_b])
        session.flush()
        entry_a = EntryModel(journal_id=journal_a.id, title="A secret", content="A private content")
        entry_b = EntryModel(journal_id=journal_b.id, title="B secret", content="B private content")
        session.add_all([entry_a, entry_b, InvitationModel(email="invited@example.test")])
        session.commit()
        ids = {"journal_a": str(journal_a.id), "journal_b": str(journal_b.id),
               "entry_a": str(entry_a.id), "entry_b": str(entry_b.id)}

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def auth(subject="pg_account_a", *, signing_key=None, issuer=ISSUER, party=PARTY, expired=False):
        now = datetime.now(timezone.utc)
        token = jwt.encode({
            "sub": subject, "iss": issuer, "azp": party,
            "iat": now - timedelta(minutes=10) if expired else now,
            "exp": now - timedelta(minutes=5) if expired else now + timedelta(minutes=5),
        }, signing_key or key, algorithm="RS256")
        return {"Authorization": f"Bearer {token}"}

    def db_override():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db] = db_override
    try:
        with (
            patch("app.core.security.get_clerk_signing_key", return_value=key.public_key()),
            patch("app.core.security.get_clerk_issuer", return_value=ISSUER),
            patch("app.core.security.get_clerk_authorized_parties", return_value=[PARTY]),
            patch("app.users.service.get_verified_clerk_email", return_value="invited@example.test"),
            TestClient(app) as client,
        ):
            yield client, auth, ids, wrong_key
    finally:
        app.dependency_overrides.clear()


def test_postgres_signed_auth_and_invitation(pg_client, postgres_engine):
    client, auth, _, wrong_key = pg_client
    assert client.get("/api/journals/").status_code == 401
    for headers in (
        {"Authorization": "Bearer invalid"},
        auth(signing_key=wrong_key), auth(expired=True),
        auth(issuer="https://wrong.example"), auth(party="https://wrong.example"),
    ):
        assert client.get("/api/journals/", headers=headers).status_code == 401
    assert client.get("/api/journals/", headers=auth("pg_disabled")).status_code == 403
    # An invited first-login user is created and the invitation redeemed atomically.
    assert client.get("/api/journals/", headers=auth("pg_new_invited")).status_code == 200
    with Session(postgres_engine) as session:
        invitation = session.scalar(select(InvitationModel).where(InvitationModel.email == "invited@example.test"))
        assert invitation.redeemed_at is not None
        assert invitation.redeemed_by_user_id is not None


def test_postgres_cross_account_isolation_and_persistence(pg_client, postgres_engine):
    client, auth, ids, _ = pg_client
    a, b = auth("pg_account_a"), auth("pg_account_b")
    assert [j["title"] for j in client.get("/api/journals/", headers=a).json()] == ["A private journal"]
    assert [j["title"] for j in client.get("/api/journals/", headers=b).json()] == ["B private journal"]
    for viewer, foreign_journal, foreign_entry in (
        (a, ids["journal_b"], ids["entry_b"]),
        (b, ids["journal_a"], ids["entry_a"]),
    ):
        responses = [
            client.get(f"/api/journals/{foreign_journal}", headers=viewer),
            client.patch(f"/api/journals/{foreign_journal}/rename", json={"title": "stolen"}, headers=viewer),
            client.patch(f"/api/journals/{foreign_journal}/archive", headers=viewer),
            client.patch(f"/api/journals/{foreign_journal}/restore", headers=viewer),
            client.get(f"/api/entries/?journal_id={foreign_journal}", headers=viewer),
            client.post("/api/entries/", json={"journal_id": foreign_journal, "title": "stolen", "content": "x"}, headers=viewer),
            client.get(f"/api/entries/{foreign_entry}", headers=viewer),
            client.patch(f"/api/entries/{foreign_entry}", json={"title": "stolen", "content": "x"}, headers=viewer),
            client.patch(f"/api/entries/{foreign_entry}/publish", headers=viewer),
            client.patch(f"/api/entries/{foreign_entry}/favorite", headers=viewer),
            client.delete(f"/api/entries/{foreign_entry}", headers=viewer),
        ]
        assert [r.status_code for r in responses] == [404] * len(responses)

    # New sessions see the original rows, with no unauthorized modifications.
    with Session(postgres_engine) as session:
        assert session.get(JournalModel, ids["journal_a"]).title == "A private journal"
        assert session.get(JournalModel, ids["journal_b"]).title == "B private journal"
        assert session.get(EntryModel, ids["entry_a"]).content == "A private content"
        assert session.get(EntryModel, ids["entry_b"]).content == "B private content"
