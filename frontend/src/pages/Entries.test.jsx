import {beforeEach, describe, expect, it, vi} from "vitest";
import {render, screen, within} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {MemoryRouter, Route, Routes} from "react-router";

import Entries from "@/pages/Entries.jsx";
import {getEntries, getJournal, getJournals} from "@/lib/api.js";

vi.mock("@/lib/api.js", () => ({
  getEntries: vi.fn(),
  getJournal: vi.fn(),
  getJournals: vi.fn(),
}));

// The page passes display data to EntryCard; test that contract without
// coupling these tests to EntryCard's internal markup.
vi.mock("@/components/EntryCard", () => ({
  default: ({id, title, status, isFavorite, journalName}) => (
    <article data-testid="entry-card" data-entry-id={id}>
      <span>{title}</span>
      <span>{status}</span>
      <span>{isFavorite ? "Favorite" : "Not favorite"}</span>
      {journalName && <span>{journalName}</span>}
    </article>
  ),
}));

const personal = {id: "j1", title: "Personal", is_archived: false};
const dreams = {id: "j2", title: "Dreams", is_archived: false};
const archived = {id: "j3", title: "Old Journal", is_archived: true};
const first = {
  id: "e1", journal_id: "j1", title: "First draft", status: "draft",
  is_favorite: false, created_at: "2026-01-01T12:00:00Z",
};
const second = {
  id: "e2", journal_id: "j1", title: "Favorite published", status: "published",
  is_favorite: true, created_at: "2026-01-03T12:00:00Z",
};
const third = {
  id: "e3", journal_id: "j2", title: "Dream draft", status: "draft",
  is_favorite: true, created_at: "2026-01-02T12:00:00Z",
};

function renderPage(path = "/journals/j1/entries") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/journals/:journalId/entries" element={<Entries/>}/>
        <Route path="/entries" element={<Entries/>}/>
      </Routes>
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.resetAllMocks();
  getJournal.mockResolvedValue(personal);
  getEntries.mockResolvedValue([first, second]);
  getJournals.mockResolvedValue([personal, dreams, archived]);
});

describe("Entries page", () => {
  it("shows loading while the journal request is pending", () => {
    getJournal.mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByText("Loading your entries...")).toBeInTheDocument();
  });

  it("loads a single journal and its entries", async () => {
    renderPage();
    expect(await screen.findByRole("heading", {name: "Personal"})).toBeInTheDocument();
    expect(getJournal).toHaveBeenCalledWith("j1");
    expect(getEntries).toHaveBeenCalledWith("j1");
    expect(getJournals).not.toHaveBeenCalled();
    expect(screen.getAllByTestId("entry-card")).toHaveLength(2);
    expect(screen.getByRole("link", {name: /new entry/i})).toHaveAttribute(
      "href", "/journals/j1/entries/new"
    );
  });

  it("loads entries from active journals only in All Entries view", async () => {
    getEntries.mockImplementation(async (id) => id === "j1" ? [first] : [third]);
    renderPage("/entries");
    expect(await screen.findByText("Dream draft")).toBeInTheDocument();
    expect(getJournals).toHaveBeenCalledWith();
    expect(getEntries).toHaveBeenCalledTimes(2);
    expect(getEntries).toHaveBeenCalledWith("j1");
    expect(getEntries).toHaveBeenCalledWith("j2");
    expect(getEntries).not.toHaveBeenCalledWith("j3");
    expect(screen.getByText("Personal")).toBeInTheDocument();
    expect(screen.getByText("Dreams")).toBeInTheDocument();
    expect(screen.getByRole("link", {name: /new entry/i})).toHaveAttribute(
      "href", "/entries/new"
    );
  });

  it("shows the empty state when a journal has no entries", async () => {
    getEntries.mockResolvedValue([]);
    renderPage();
    expect(await screen.findByText("No entries yet. Start writing your first entry.")).toBeInTheDocument();
  });

  it("shows an error when loading entries fails", async () => {
    getEntries.mockRejectedValue(new Error("Service unavailable"));
    renderPage();
    expect(await screen.findByText("Unable to load entries: Service unavailable")).toBeInTheDocument();
  });

  it("filters entries by draft and published status", async () => {
    const user = userEvent.setup();
    renderPage();
    expect(await screen.findByText("Favorite published")).toBeInTheDocument();
    await user.click(screen.getByRole("button", {name: "Drafts"}));
    expect(screen.getByText("First draft")).toBeInTheDocument();
    expect(screen.queryByText("Favorite published")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", {name: "Published"}));
    expect(screen.getByText("Favorite published")).toBeInTheDocument();
    expect(screen.queryByText("First draft")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", {name: "All"}));
    expect(screen.getAllByTestId("entry-card")).toHaveLength(2);
  });

  it("combines favorites and status filters and shows the no-match state", async () => {
    const user = userEvent.setup();
    renderPage();
    expect(await screen.findByText("Favorite published")).toBeInTheDocument();
    await user.click(screen.getByRole("checkbox", {name: "Favorites only"}));
    expect(screen.queryByText("First draft")).not.toBeInTheDocument();
    expect(screen.getByText("Favorite published")).toBeInTheDocument();
    await user.click(screen.getByRole("button", {name: "Drafts"}));
    expect(screen.getByText("No entries match your filters.")).toBeInTheDocument();
  });

  it("orders visible entries newest first", async () => {
    renderPage();
    await screen.findByText("Favorite published");
    const cards = within(screen.getByRole("region", {name: "Journal entries"})).getAllByTestId("entry-card");
    expect(cards.map(card => card.getAttribute("data-entry-id"))).toEqual(["e2", "e1"]);
  });
});
