import {afterEach, beforeEach, describe, expect, it, vi} from "vitest";
import {render, screen, waitFor} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {MemoryRouter, Route, Routes} from "react-router";

import Editor from "@/pages/Editor.jsx";
import {getJournal, getJournals} from "@/lib/api.js";

vi.mock("@/lib/api.js", () => ({
  getJournal: vi.fn(),
  getJournals: vi.fn(),
  apiFetch: vi.fn((path, options) => fetch(`/api${path}`, options)),
}));

const journal = {id: "j1", title: "Personal", is_archived: false};
const archived = {id: "j2", title: "Old", is_archived: true};
const draft = {
  id: "e1", journal_id: "j1", title: "Morning Notes", content: "A quiet start",
  status: "draft", is_favorite: false, created_at: "2026-01-01T12:00:00Z",
};
const published = {...draft, status: "published"};

function response(body, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(body),
    text: vi.fn().mockResolvedValue(typeof body === "string" ? body : JSON.stringify(body)),
  };
}

function renderPage(path = "/journals/j1/entries/new") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/journals/:journalId/entries/new" element={<Editor/>}/>
        <Route path="/entries/new" element={<Editor/>}/>
        <Route path="/entries/:entryId" element={<Editor/>}/>
      </Routes>
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.resetAllMocks();
  getJournal.mockResolvedValue(journal);
  getJournals.mockResolvedValue([journal, archived]);
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => vi.unstubAllGlobals());

describe("Editor page", () => {
  it("disables saving and publishing until a new entry has a title", async () => {
    renderPage();
    expect(screen.getByRole("button", {name: "Save Draft"})).toBeDisabled();
    expect(screen.getByRole("button", {name: "Publish"})).toBeDisabled();
    await userEvent.setup().type(screen.getByRole("textbox", {name: "Entry title"}), "   ");
    expect(screen.getByRole("button", {name: "Save Draft"})).toBeDisabled();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("creates a draft with a trimmed title and the journal ID", async () => {
    fetch.mockResolvedValue(response(draft));
    renderPage();
    const user = userEvent.setup();
    await user.type(screen.getByRole("textbox", {name: "Entry title"}), "  Morning Notes  ");
    await user.type(screen.getByRole("textbox", {name: "Entry content"}), "A quiet start");
    await user.click(screen.getByRole("button", {name: "Save Draft"}));
    await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/entries/", expect.objectContaining({
      method: "POST",
      body: JSON.stringify({journal_id: "j1", title: "Morning Notes", content: "A quiet start"}),
    })));
    expect(await screen.findByText("Entry saved successfully.")).toBeInTheDocument();
    expect(screen.getByRole("link", {name: "View Entry"})).toHaveAttribute("href", "/entries/e1");
  });

  it("requires selecting an active journal when creating from All Entries", async () => {
    fetch.mockResolvedValue(response(draft));
    renderPage("/entries/new");
    expect(await screen.findByRole("option", {name: "Personal"})).toBeInTheDocument();
    expect(screen.queryByRole("option", {name: "Old"})).not.toBeInTheDocument();
    expect(getJournals).toHaveBeenCalledWith();
    const user = userEvent.setup();
    await user.type(screen.getByRole("textbox", {name: "Entry title"}), "Morning Notes");
    expect(screen.getByRole("button", {name: "Save Draft"})).toBeDisabled();
    await user.selectOptions(screen.getByLabelText("Write in journal"), "j1");
    await user.click(screen.getByRole("button", {name: "Save Draft"}));
    await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/entries/", expect.objectContaining({method: "POST"})));
  });

  it("loads an existing entry and saves edits using PATCH", async () => {
    fetch.mockResolvedValueOnce(response(draft)).mockResolvedValueOnce(response({...draft, title: "Revised"}));
    renderPage("/entries/e1");
    expect(screen.getByText("Loading entry...")).toBeInTheDocument();
    const input = await screen.findByRole("textbox", {name: "Entry title"});
    expect(input).toHaveValue("Morning Notes");
    const user = userEvent.setup();
    await user.clear(input);
    await user.type(input, "  Revised  ");
    await user.click(screen.getByRole("button", {name: "Save Changes"}));
    await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/entries/e1", expect.objectContaining({
      method: "PATCH", body: JSON.stringify({title: "Revised", content: "A quiet start"}),
    })));
    expect(await screen.findByText("Entry saved successfully.")).toBeInTheDocument();
  });

  it("shows an error when an existing entry cannot be loaded", async () => {
    fetch.mockResolvedValue(response("Missing", 404));
    renderPage("/entries/e1");
    expect(await screen.findByRole("alert")).toHaveTextContent("Failed to load entry (HTTP 404)");
  });

  it("shows a save error without claiming the entry was saved", async () => {
    fetch.mockResolvedValue(response("Unavailable", 503));
    renderPage();
    const user = userEvent.setup();
    await user.type(screen.getByRole("textbox", {name: "Entry title"}), "A draft");
    await user.click(screen.getByRole("button", {name: "Save Draft"}));
    expect(await screen.findByRole("alert")).toHaveTextContent("Failed to save entry (HTTP 503)");
    expect(screen.queryByText("Entry saved successfully.")).not.toBeInTheDocument();
  });

  it("publishes a saved draft and disables publishing again", async () => {
    fetch.mockResolvedValueOnce(response(draft)).mockResolvedValueOnce(response(published));
    renderPage("/entries/e1");
    const user = userEvent.setup();
    await screen.findByRole("textbox", {name: "Entry title"});
    await user.click(screen.getByRole("button", {name: "Publish"}));
    await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/entries/e1/publish", {method: "PATCH"}));
    expect(await screen.findByText("Entry published successfully.")).toBeInTheDocument();
    expect(screen.getByRole("button", {name: "Published"})).toBeDisabled();
  });

  it("shows a publish error and keeps the draft publishable", async () => {
    fetch.mockResolvedValueOnce(response(draft)).mockResolvedValueOnce(response("Failure", 500));
    renderPage("/entries/e1");
    await screen.findByRole("textbox", {name: "Entry title"});
    await userEvent.setup().click(screen.getByRole("button", {name: "Publish"}));
    expect(await screen.findByRole("alert")).toHaveTextContent("Failed to publish entry (HTTP 500)");
    expect(screen.getByRole("button", {name: "Publish"})).toBeEnabled();
  });

  it("toggles favorite on an existing entry", async () => {
    fetch.mockResolvedValueOnce(response(draft)).mockResolvedValueOnce(response({...draft, is_favorite: true}));
    renderPage("/entries/e1");
    await screen.findByRole("textbox", {name: "Entry title"});
    await userEvent.setup().click(screen.getByRole("button", {name: "Favorite"}));
    await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/entries/e1/favorite", {method: "PATCH"}));
    expect(await screen.findByRole("button", {name: "Favorited"})).toHaveAttribute("aria-pressed", "true");
  });

  it("shows a favorite error without changing the favorite state", async () => {
    fetch.mockResolvedValueOnce(response(draft)).mockResolvedValueOnce(response("Failure", 500));
    renderPage("/entries/e1");
    await screen.findByRole("textbox", {name: "Entry title"});
    await userEvent.setup().click(screen.getByRole("button", {name: "Favorite"}));
    expect(await screen.findByRole("alert")).toHaveTextContent("Failed to update favorite (HTTP 500)");
    expect(screen.getByRole("button", {name: "Favorite"})).toHaveAttribute("aria-pressed", "false");
  });
});
