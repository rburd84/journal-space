from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_db
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
        return [j for j in self.journals.values() if j.user_id == user_id]


class FakeSession:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


@pytest.fixture
def api(monkeypatch):
    repository = FakeJournalRepository()
    session = FakeSession()
    # The router constructs a repository per request; return our isolated fake.
    monkeypatch.setattr(journal_router_module, "SqlJournalRepository", lambda db: repository)
    app = FastAPI()
    app.include_router(journal_router_module.router)
    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as client:
        yield client, repository, session
    app.dependency_overrides.clear()


def test_create_journal_returns_201_and_default_type(api):
    client, repo, session = api
    user_id = uuid4()
    response = client.post("/journals/", json={"user_id": str(user_id), "title": "  Notes  "})
    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == str(user_id)
    assert body["title"] == "Notes"
    assert body["type"] == "personal"
    assert body["is_archived"] is False
    assert repo.get(UUID(body["id"])) is not None
    assert session.commits == 1


def test_create_journal_accepts_explicit_type(api):
    client, _, _ = api
    response = client.post("/journals/", json={"user_id": str(uuid4()), "title": "Thanks", "type": "gratitude"})
    assert response.status_code == 201
    assert response.json()["type"] == "gratitude"


@pytest.mark.parametrize("title", ["", "   ", "\n\t"])
def test_create_journal_rejects_blank_title(api, title):
    client, repo, session = api
    response = client.post("/journals/", json={"user_id": str(uuid4()), "title": title})
    assert response.status_code == 422
    assert repo.journals == {}
    assert session.commits == 0


def test_create_journal_rejects_invalid_type(api):
    client, _, session = api
    response = client.post("/journals/", json={"user_id": str(uuid4()), "title": "Notes", "type": "unknown"})
    assert response.status_code == 422
    assert session.commits == 0


def test_create_journal_rejects_missing_user_id(api):
    client, _, _ = api
    assert client.post("/journals/", json={"title": "Notes"}).status_code == 422


def test_list_journals_filters_by_user_and_includes_archived(api):
    client, repo, _ = api
    user_id = uuid4()
    own = Journal(user_id=user_id, title="Own")
    archived = Journal(user_id=user_id, title="Archived", is_archived=True)
    other = Journal(user_id=uuid4(), title="Other")
    for journal in (own, archived, other):
        repo.save(journal)
    response = client.get("/journals/", params={"user_id": str(user_id)})
    assert response.status_code == 200
    assert {j["id"] for j in response.json()} == {str(own.id), str(archived.id)}


def test_list_journals_requires_user_id(api):
    client, _, _ = api
    assert client.get("/journals/").status_code == 422


def test_get_existing_journal(api):
    client, repo, _ = api
    journal = Journal(user_id=uuid4(), title="Notes")
    repo.save(journal)
    response = client.get(f"/journals/{journal.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(journal.id)
    assert response.json()["title"] == "Notes"


def test_get_missing_journal_returns_404(api):
    client, _, _ = api
    response = client.get(f"/journals/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Journal not found"


def test_get_malformed_journal_id_returns_422(api):
    client, _, _ = api
    assert client.get("/journals/not-a-uuid").status_code == 422


def test_rename_existing_journal(api):
    client, repo, session = api
    journal = Journal(user_id=uuid4(), title="Old")
    repo.save(journal)
    response = client.patch(f"/journals/{journal.id}/rename", json={"title": "  New  "})
    assert response.status_code == 200
    assert response.json()["title"] == "New"
    assert repo.get(journal.id).title == "New"
    assert session.commits == 1


def test_rename_missing_journal_returns_404(api):
    client, _, session = api
    assert client.patch(f"/journals/{uuid4()}/rename", json={"title": "New"}).status_code == 404
    assert session.commits == 0


@pytest.mark.parametrize("title", ["", " " * 3])
def test_rename_rejects_blank_title(api, title):
    client, repo, session = api
    journal = Journal(user_id=uuid4(), title="Original")
    repo.save(journal)
    response = client.patch(f"/journals/{journal.id}/rename", json={"title": title})
    assert response.status_code == 422
    assert repo.get(journal.id).title == "Original"
    assert session.commits == 0


def test_archive_existing_journal(api):
    client, repo, session = api
    journal = Journal(user_id=uuid4(), title="Notes")
    repo.save(journal)
    response = client.patch(f"/journals/{journal.id}/archive")
    assert response.status_code == 200
    assert response.json()["is_archived"] is True
    assert repo.get(journal.id).is_archived is True
    assert session.commits == 1


def test_archive_missing_journal_returns_404(api):
    client, _, session = api
    assert client.patch(f"/journals/{uuid4()}/archive").status_code == 404
    assert session.commits == 0


def test_restore_existing_journal(api):
    client, repo, session = api
    journal = Journal(user_id=uuid4(), title="Notes", is_archived=True)
    repo.save(journal)
    response = client.patch(f"/journals/{journal.id}/restore")
    assert response.status_code == 200
    assert response.json()["is_archived"] is False
    assert repo.get(journal.id).is_archived is False
    assert session.commits == 1


def test_restore_missing_journal_returns_404(api):
    client, _, session = api
    assert client.patch(f"/journals/{uuid4()}/restore").status_code == 404
    assert session.commits == 0
