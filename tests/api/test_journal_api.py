from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user, get_db
from app.journals import router as journal_router_module
from app.journals.domain import Journal


class FakeJournalRepository:
    def __init__(self):
        self.journals = {}

    def save(self, journal):
        self.journals[journal.id] = journal

    def get(self, journal_id):
        return self.journals.get(journal_id)

    def list_by_user(self, user_id):
        return [
            journal
            for journal in self.journals.values()
            if journal.user_id == user_id
        ]


class FakeSession:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


@pytest.fixture
def api(monkeypatch):
    repository = FakeJournalRepository()
    session = FakeSession()
    user = SimpleNamespace(id=uuid4(), is_active=True)

    monkeypatch.setattr(
        journal_router_module,
        "SqlJournalRepository",
        lambda db: repository,
    )

    def fake_require_owned_journal(db, journal_id, user_id):
        journal = repository.get(journal_id)

        if journal is None or journal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Journal not found",
            )

        return journal

    monkeypatch.setattr(
        journal_router_module,
        "require_owned_journal",
        fake_require_owned_journal,
    )

    app = FastAPI()
    app.include_router(journal_router_module.router)

    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        yield client, repository, session, user

    app.dependency_overrides.clear()


def test_create_journal_returns_201_and_default_type(api):
    client, repo, session, user = api

    response = client.post(
        "/journals/",
        json={
            "title": "  Notes  ",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["user_id"] == str(user.id)
    assert body["title"] == "Notes"
    assert body["type"] == "personal"
    assert body["is_archived"] is False
    assert repo.get(UUID(body["id"])) is not None
    assert session.commits == 1


def test_create_journal_accepts_explicit_type(api):
    client, _, _, user = api

    response = client.post(
        "/journals/",
        json={
            "title": "Thanks",
            "type": "gratitude",
        },
    )

    assert response.status_code == 201
    assert response.json()["type"] == "gratitude"


@pytest.mark.parametrize("title", ["", "   ", "\n\t"])
def test_create_journal_rejects_blank_title(api, title):
    client, repo, session, user = api

    response = client.post(
        "/journals/",
        json={
            "title": title,
        },
    )

    assert response.status_code == 422
    assert repo.journals == {}
    assert session.commits == 0


def test_create_journal_rejects_invalid_type(api):
    client, _, session, user = api

    response = client.post(
        "/journals/",
        json={
            "title": "Notes",
            "type": "unknown",
        },
    )

    assert response.status_code == 422
    assert session.commits == 0


def test_create_journal_does_not_require_user_id(api):
    client, _, _, _ = api

    response = client.post(
        "/journals/",
        json={"title": "Notes"},
    )

    assert response.status_code == 201


def test_create_journal_rejects_another_user_id(api):
    client, repo, session, _ = api

    response = client.post(
        "/journals/",
        json={
            "user_id": str(uuid4()),
            "title": "Not Mine",
        },
    )

    assert response.status_code == 422
    assert repo.journals == {}
    assert session.commits == 0


def test_list_journals_filters_by_authenticated_user(api):
    client, repo, _, user = api

    own = Journal(
        user_id=user.id,
        title="Own",
    )

    archived = Journal(
        user_id=user.id,
        title="Archived",
        is_archived=True,
    )

    other = Journal(
        user_id=uuid4(),
        title="Other",
    )

    for journal in (own, archived, other):
        repo.save(journal)

    response = client.get("/journals/")

    assert response.status_code == 200

    returned_ids = {
        journal["id"]
        for journal in response.json()
    }

    assert returned_ids == {
        str(own.id),
        str(archived.id),
    }


def test_list_journals_does_not_require_user_id(api):
    client, _, _, _ = api

    response = client.get("/journals/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_existing_journal(api):
    client, repo, _, user = api

    journal = Journal(
        user_id=user.id,
        title="Notes",
    )

    repo.save(journal)

    response = client.get(
        f"/journals/{journal.id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(journal.id)
    assert response.json()["title"] == "Notes"


def test_get_missing_journal_returns_404(api):
    client, _, _, _ = api

    response = client.get(
        f"/journals/{uuid4()}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Journal not found"


def test_get_other_users_journal_returns_404(api):
    client, repo, _, _ = api

    journal = Journal(
        user_id=uuid4(),
        title="Private",
    )

    repo.save(journal)

    response = client.get(
        f"/journals/{journal.id}"
    )

    assert response.status_code == 404


def test_get_malformed_journal_id_returns_422(api):
    client, _, _, _ = api

    response = client.get(
        "/journals/not-a-uuid"
    )

    assert response.status_code == 422


def test_rename_existing_journal(api):
    client, repo, session, user = api

    journal = Journal(
        user_id=user.id,
        title="Old",
    )

    repo.save(journal)

    response = client.patch(
        f"/journals/{journal.id}/rename",
        json={"title": "  New  "},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New"
    assert repo.get(journal.id).title == "New"
    assert session.commits == 1


def test_rename_missing_journal_returns_404(api):
    client, _, session, _ = api

    response = client.patch(
        f"/journals/{uuid4()}/rename",
        json={"title": "New"},
    )

    assert response.status_code == 404
    assert session.commits == 0


@pytest.mark.parametrize("title", ["", "   "])
def test_rename_rejects_blank_title(api, title):
    client, repo, session, user = api

    journal = Journal(
        user_id=user.id,
        title="Original",
    )

    repo.save(journal)

    response = client.patch(
        f"/journals/{journal.id}/rename",
        json={"title": title},
    )

    assert response.status_code == 422
    assert repo.get(journal.id).title == "Original"
    assert session.commits == 0


def test_archive_existing_journal(api):
    client, repo, session, user = api

    journal = Journal(
        user_id=user.id,
        title="Notes",
    )

    repo.save(journal)

    response = client.patch(
        f"/journals/{journal.id}/archive"
    )

    assert response.status_code == 200
    assert response.json()["is_archived"] is True
    assert repo.get(journal.id).is_archived is True
    assert session.commits == 1


def test_archive_missing_journal_returns_404(api):
    client, _, session, _ = api

    response = client.patch(
        f"/journals/{uuid4()}/archive"
    )

    assert response.status_code == 404
    assert session.commits == 0


def test_restore_existing_journal(api):
    client, repo, session, user = api

    journal = Journal(
        user_id=user.id,
        title="Notes",
        is_archived=True,
    )

    repo.save(journal)

    response = client.patch(
        f"/journals/{journal.id}/restore"
    )

    assert response.status_code == 200
    assert response.json()["is_archived"] is False
    assert repo.get(journal.id).is_archived is False
    assert session.commits == 1


def test_restore_missing_journal_returns_404(api):
    client, _, session, _ = api

    response = client.patch(
        f"/journals/{uuid4()}/restore"
    )

    assert response.status_code == 404
    assert session.commits == 0


# Phase 46M.3: Account B must not access or modify Account A's journals.
# These are router-level tests: the ownership guard is mocked by the api fixture.
@pytest.mark.parametrize(
    ("method", "suffix", "payload"),
    [
        ("get", "", None),
        ("patch", "/rename", {"title": "Intruder rename"}),
        ("patch", "/archive", None),
        ("patch", "/restore", None),
    ],
)
def test_other_account_cannot_access_or_change_journal(api, method, suffix, payload):
    client, repo, session, account_a = api
    account_b = SimpleNamespace(id=uuid4(), is_active=True)
    journal_a = Journal(user_id=account_a.id, title="Account A private journal")
    repo.save(journal_a)

    # Change the authenticated identity without changing the underlying data.
    client.app.dependency_overrides[get_current_user] = lambda: account_b

    request = getattr(client, method)
    url = f"/journals/{journal_a.id}{suffix}"
    response = request(url, json=payload) if payload is not None else request(url)

    assert response.status_code == 404
    assert response.json()["detail"] == "Journal not found"
    assert repo.get(journal_a.id).title == "Account A private journal"
    assert repo.get(journal_a.id).is_archived is False
    assert repo.get(journal_a.id).user_id == account_a.id
    assert session.commits == 0


@pytest.mark.parametrize("archived", [False, True])
def test_other_account_cannot_change_journal_archive_state(api, archived):
    client, repo, session, account_a = api
    account_b = SimpleNamespace(id=uuid4(), is_active=True)
    journal_a = Journal(
        user_id=account_a.id,
        title="Account A private journal",
        is_archived=archived,
    )
    repo.save(journal_a)
    client.app.dependency_overrides[get_current_user] = lambda: account_b

    operation = "restore" if archived else "archive"
    response = client.patch(f"/journals/{journal_a.id}/{operation}")

    assert response.status_code == 404
    assert repo.get(journal_a.id).is_archived is archived
    assert session.commits == 0


def test_switching_accounts_keeps_journal_lists_separate(api):
    client, repo, _, account_a = api
    account_b = SimpleNamespace(id=uuid4(), is_active=True)
    journal_a = Journal(user_id=account_a.id, title="Account A private journal")
    journal_b = Journal(user_id=account_b.id, title="Account B private journal")
    repo.save(journal_a)
    repo.save(journal_b)

    response_a = client.get("/journals/")
    assert response_a.status_code == 200
    assert {item["id"] for item in response_a.json()} == {str(journal_a.id)}

    client.app.dependency_overrides[get_current_user] = lambda: account_b
    response_b = client.get("/journals/")
    assert response_b.status_code == 200
    assert {item["id"] for item in response_b.json()} == {str(journal_b.id)}

    # Account B still has access to its own journal by ID.
    own_response = client.get(f"/journals/{journal_b.id}")
    assert own_response.status_code == 200
    assert own_response.json()["id"] == str(journal_b.id)
