import pytest
from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.dependencies import get_current_user, get_db
from app.entries.models import EntryModel
from app.entries.router import router as entries_router
from app.journals.models import JournalModel
from app.journals.router import router as journals_router
from app.users.invitations import InvitationModel  # noqa: F401
from app.users.models import UserModel


@pytest.fixture
def environment():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, connection_record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    with Session(engine) as db:
        alice = UserModel(clerk_user_id="user_alice")
        bob = UserModel(clerk_user_id="user_bob")
        db.add_all([alice, bob])
        db.flush()

        alice_id = alice.id
        bob_id = bob.id

        alice_journal = JournalModel(
            user_id=alice_id,
            title="Alice's Journal",
            type="personal",
            is_archived=False,
        )
        bob_journal = JournalModel(
            user_id=bob_id,
            title="Bob's Journal",
            type="personal",
            is_archived=False,
        )

        db.add_all([alice_journal, bob_journal])
        db.flush()

        alice_journal_id = alice_journal.id
        bob_journal_id = bob_journal.id

        bob_entry = EntryModel(
            journal_id=bob_journal_id,
            title="Private entry",
            content="Bob's private thoughts",
            status="draft",
            is_favorite=False,
        )

        db.add(bob_entry)
        db.flush()

        bob_entry_id = bob_entry.id
        db.commit()

    app = FastAPI()
    app.include_router(journals_router)
    app.include_router(entries_router)

    def override_db():
        with Session(engine) as db:
            yield db

    def override_current_user(
            x_test_user: str | None = Header(default=None),
    ):
        if x_test_user not in {"alice", "bob"}:
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
            )

        user_id = alice_id if x_test_user == "alice" else bob_id

        with Session(engine) as db:
            user = db.get(UserModel, user_id)
            if user is None:
                raise HTTPException(status_code=401)
            return user

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as client:
        yield {
            "client": client,
            "engine": engine,
            "alice_id": alice_id,
            "bob_id": bob_id,
            "alice_journal_id": alice_journal_id,
            "bob_journal_id": bob_journal_id,
            "bob_entry_id": bob_entry_id,
        }

    engine.dispose()


def as_alice(environment):
    return {"X-Test-User": "alice"}


def as_bob(environment):
    return {"X-Test-User": "bob"}


def test_unauthenticated_requests_are_rejected(environment):
    client = environment["client"]

    assert client.get("/journals/").status_code == 401
    assert client.get("/entries/").status_code == 401


def test_journal_list_is_isolated(environment):
    client = environment["client"]

    response = client.get(
        "/journals/",
        headers=as_alice(environment),
    )

    assert response.status_code == 200

    ids = {item["id"] for item in response.json()}

    assert str(environment["alice_journal_id"]) in ids
    assert str(environment["bob_journal_id"]) not in ids


def test_other_users_journal_is_hidden(environment):
    client = environment["client"]
    journal_id = environment["bob_journal_id"]
    headers = as_alice(environment)

    requests = [
        client.get(
            f"/journals/{journal_id}",
            headers=headers,
        ),
        client.patch(
            f"/journals/{journal_id}/rename",
            json={"title": "Stolen"},
            headers=headers,
        ),
        client.patch(
            f"/journals/{journal_id}/archive",
            headers=headers,
        ),
        client.patch(
            f"/journals/{journal_id}/restore",
            headers=headers,
        ),
    ]

    assert all(response.status_code == 404 for response in requests)


def test_other_users_entries_cannot_be_listed_or_created(environment):
    client = environment["client"]
    journal_id = environment["bob_journal_id"]
    headers = as_alice(environment)

    listing = client.get(
        "/entries/",
        params={"journal_id": str(journal_id)},
        headers=headers,
    )

    creation = client.post(
        "/entries/",
        json={
            "journal_id": str(journal_id),
            "title": "Unauthorized",
            "content": "Should not be saved",
        },
        headers=headers,
    )

    assert listing.status_code == 404
    assert creation.status_code == 404


def test_other_users_entry_is_hidden_from_all_operations(environment):
    client = environment["client"]
    entry_id = environment["bob_entry_id"]
    headers = as_alice(environment)

    responses = [
        client.get(
            f"/entries/{entry_id}",
            headers=headers,
        ),
        client.patch(
            f"/entries/{entry_id}/publish",
            headers=headers,
        ),
        client.patch(
            f"/entries/{entry_id}",
            json={
                "title": "Unauthorized edit",
                "content": "Unauthorized content",
            },
            headers=headers,
        ),
        client.patch(
            f"/entries/{entry_id}/favorite",
            headers=headers,
        ),
        client.delete(
            f"/entries/{entry_id}",
            headers=headers,
        ),
    ]

    assert all(response.status_code == 404 for response in responses)


def test_unauthorized_attempts_do_not_modify_data(environment):
    client = environment["client"]
    journal_id = environment["bob_journal_id"]
    entry_id = environment["bob_entry_id"]

    client.patch(
        f"/journals/{journal_id}/archive",
        headers=as_alice(environment),
    )
    client.delete(
        f"/entries/{entry_id}",
        headers=as_alice(environment),
    )

    with Session(environment["engine"]) as db:
        journal = db.get(JournalModel, journal_id)
        entry = db.get(EntryModel, entry_id)

        assert journal is not None
        assert journal.is_archived is False
        assert entry is not None
        assert entry.content == "Bob's private thoughts"


def test_owner_can_still_access_their_resources(environment):
    client = environment["client"]

    journal_response = client.get(
        f"/journals/{environment['bob_journal_id']}",
        headers=as_bob(environment),
    )

    entry_response = client.get(
        f"/entries/{environment['bob_entry_id']}",
        headers=as_bob(environment),
    )

    print("Journal status:", journal_response.status_code)
    print("Journal response:", journal_response.json())
    print("Entry status:", entry_response.status_code)
    print("Entry response:", entry_response.json())

    assert journal_response.status_code == 200
    assert entry_response.status_code == 200
