from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_db
from app.entries import router as entry_router_module
from app.entries.domain import JournalEntry, EntryStatus


class FakeEntryRepository:
    def __init__(self):
        self.entries = {}

    def save(self, entry):
        self.entries[entry.id] = entry

    def get(self, entry_id):
        return self.entries.get(entry_id)

    def delete(self, entry_id):
        return self.entries.pop(entry_id, None) is not None

    def list_by_journal(self, journal_id):
        return [entry for entry in self.entries.values()
                if entry.journal_id == journal_id]


class FakeSession:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


@pytest.fixture
def api(monkeypatch):
    repository = FakeEntryRepository()
    session = FakeSession()
    monkeypatch.setattr(entry_router_module, "SqlEntryRepository", lambda db: repository)
    app = FastAPI()
    app.include_router(entry_router_module.router)
    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as client:
        yield client, repository, session
    app.dependency_overrides.clear()


def seeded(repo, journal_id=None, title="Morning", content="Hello"):
    entry = JournalEntry(journal_id=journal_id or uuid4(), title=title, content=content)
    repo.save(entry)
    return entry


def test_create_returns_201_and_draft_defaults(api):
    client, repo, session = api
    journal_id = uuid4()
    response = client.post("/entries/", json={
        "journal_id": str(journal_id), "title": "Morning", "content": "Hello"
    })
    assert response.status_code == 201
    body = response.json()
    assert body["journal_id"] == str(journal_id)
    assert body["title"] == "Morning"
    assert body["content"] == "Hello"
    assert body["status"] == "draft"
    assert body["is_favorite"] is False
    assert UUID(body["id"]) in repo.entries
    assert body["created_at"] and body["updated_at"]
    assert session.commits == 1


def test_create_defaults_content_to_empty(api):
    client, _, _ = api
    response = client.post("/entries/", json={"journal_id": str(uuid4()), "title": "Draft"})
    assert response.status_code == 201
    assert response.json()["content"] == ""


@pytest.mark.parametrize("title", ["", "x" * 201])
def test_create_rejects_invalid_title_length(api, title):
    client, repo, session = api
    response = client.post("/entries/", json={
        "journal_id": str(uuid4()), "title": title
    })
    assert response.status_code == 422
    assert repo.entries == {}
    assert session.commits == 0


def test_create_rejects_invalid_journal_id(api):
    client, repo, _ = api
    response = client.post("/entries/", json={"journal_id": "bad-id", "title": "Draft"})
    assert response.status_code == 422
    assert not repo.entries


def test_create_requires_title(api):
    client, _, _ = api
    response = client.post("/entries/", json={"journal_id": str(uuid4())})
    assert response.status_code == 422


def test_list_entries_filters_by_journal(api):
    client, repo, _ = api
    target = uuid4()
    included = seeded(repo, journal_id=target)
    seeded(repo, journal_id=uuid4())
    response = client.get("/entries/", params={"journal_id": str(target)})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(included.id)]


def test_list_entries_empty_journal(api):
    client, _, _ = api
    response = client.get("/entries/", params={"journal_id": str(uuid4())})
    assert response.status_code == 200
    assert response.json() == []


def test_list_requires_valid_journal_id(api):
    client, _, _ = api
    assert client.get("/entries/").status_code == 422
    assert client.get("/entries/", params={"journal_id": "invalid"}).status_code == 422


def test_get_existing_entry(api):
    client, repo, _ = api
    entry = seeded(repo)
    response = client.get(f"/entries/{entry.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(entry.id)


def test_get_missing_entry_returns_404(api):
    client, _, _ = api
    response = client.get(f"/entries/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"


def test_update_changes_title_and_content(api):
    client, repo, session = api
    entry = seeded(repo)
    response = client.patch(f"/entries/{entry.id}", json={
        "title": "Evening", "content": "Updated"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Evening"
    assert response.json()["content"] == "Updated"
    assert repo.get(entry.id).title == "Evening"
    assert session.commits == 1


def test_update_missing_entry_returns_404_without_commit(api):
    client, _, session = api
    response = client.patch(f"/entries/{uuid4()}", json={
        "title": "Evening", "content": "Updated"
    })
    assert response.status_code == 404
    assert session.commits == 0


def test_update_requires_both_fields(api):
    client, repo, session = api
    entry = seeded(repo)
    response = client.patch(f"/entries/{entry.id}", json={"title": "Only"})
    assert response.status_code == 422
    assert repo.get(entry.id).title == "Morning"
    assert session.commits == 0


def test_publish_entry_with_content(api):
    client, repo, session = api
    entry = seeded(repo)
    response = client.patch(f"/entries/{entry.id}/publish")
    assert response.status_code == 200
    assert response.json()["status"] == "published"
    assert repo.get(entry.id).status == EntryStatus.PUBLISHED
    assert session.commits == 1


def test_publish_missing_entry_returns_404(api):
    client, _, session = api
    response = client.patch(f"/entries/{uuid4()}/publish")
    assert response.status_code == 404
    assert session.commits == 0


def test_toggle_favorite_on_and_off(api):
    client, repo, session = api
    entry = seeded(repo)
    first = client.patch(f"/entries/{entry.id}/favorite")
    second = client.patch(f"/entries/{entry.id}/favorite")
    assert first.status_code == second.status_code == 200
    assert first.json()["is_favorite"] is True
    assert second.json()["is_favorite"] is False
    assert repo.get(entry.id).is_favorite is False
    assert session.commits == 2


def test_favorite_missing_entry_returns_404(api):
    client, _, session = api
    response = client.patch(f"/entries/{uuid4()}/favorite")
    assert response.status_code == 404
    assert session.commits == 0


def test_delete_existing_entry_returns_204(api):
    client, repo, session = api
    entry = seeded(repo)
    response = client.delete(f"/entries/{entry.id}")
    assert response.status_code == 204
    assert response.content == b""
    assert repo.get(entry.id) is None
    assert session.commits == 1


def test_delete_missing_entry_returns_404(api):
    client, _, session = api
    response = client.delete(f"/entries/{uuid4()}")
    assert response.status_code == 404
    assert session.commits == 0


def test_malformed_entry_id_returns_422(api):
    client, _, _ = api
    assert client.get("/entries/not-a-uuid").status_code == 422
