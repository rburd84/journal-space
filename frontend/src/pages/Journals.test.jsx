import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import Journals from "@/pages/Journals.jsx";
import { getJournals, renameJournal, archiveJournal, restoreJournal } from "@/lib/api.js";

vi.mock("@/lib/api.js", () => ({
  getJournals: vi.fn(),
  renameJournal: vi.fn(),
  archiveJournal: vi.fn(),
  restoreJournal: vi.fn(),
}));

// Creation has its own seven component tests; here we test its page callback.
vi.mock("@/components/CreateJournalDialog.jsx", () => ({
  default: ({ onCreated }) => (
    <button onClick={() => onCreated({ id: "created", title: "Created Journal", type: "personal", is_archived: false })}>
      Simulate journal creation
    </button>
  ),
}));

const active = { id: "a", title: "Active Notes", type: "personal", is_archived: false };
const archived = { id: "b", title: "Old Notes", type: "dream", is_archived: true };

function setup(journals = [active, archived]) {
  getJournals.mockResolvedValue(journals);
  const user = userEvent.setup();
  render(<MemoryRouter><Journals /></MemoryRouter>);
  return user;
}

async function manage(user, title) {
  await user.click(screen.getByRole("button", { name: `Manage ${title}` }));
}

beforeEach(() => vi.resetAllMocks());
afterEach(() => vi.unstubAllGlobals());

describe("Journals page", () => {
  it("loads journals for the development user", async () => {
    setup();
    expect(screen.getByText("Loading journals...")).toBeInTheDocument();
    expect(await screen.findByText("Active Notes")).toBeInTheDocument();
    expect(getJournals).toHaveBeenCalledWith();
  });

  it("shows only active journals by default and archived journals on selection", async () => {
    const user = setup();
    await screen.findByText("Active Notes");
    expect(screen.queryByText("Old Notes")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Active" })).toHaveAttribute("aria-pressed", "true");
    await user.click(screen.getByRole("button", { name: "Archived" }));
    expect(screen.getByText("Old Notes")).toBeInTheDocument();
    expect(screen.queryByText("Active Notes")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Archived" })).toHaveAttribute("aria-pressed", "true");
  });

  it("shows separate empty states for active and archived views", async () => {
    const user = setup([]);
    expect(await screen.findByText("No active journals yet. Create your first journal.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Archived" }));
    expect(screen.getByText("No archived journals.")).toBeInTheDocument();
  });

  it("shows a load error", async () => {
    getJournals.mockRejectedValue(new Error("Unable to load journals"));
    render(<MemoryRouter><Journals /></MemoryRouter>);
    expect(await screen.findByRole("alert")).toHaveTextContent("Unable to load journals");
  });

  it("adds a newly created journal to the active list", async () => {
    const user = setup([]);
    await screen.findByText("No active journals yet. Create your first journal.");
    await user.click(screen.getByRole("button", { name: "Simulate journal creation" }));
    expect(screen.getByText("Created Journal")).toBeInTheDocument();
  });

  it("renames a journal and updates the visible title", async () => {
    const user = setup();
    renameJournal.mockResolvedValue({ ...active, title: "Renamed Notes" });
    await screen.findByText("Active Notes");
    await manage(user, "Active Notes");
    await user.click(screen.getByRole("button", { name: "Rename" }));
    const dialog = screen.getByRole("dialog", { name: "Rename Journal" });
    const input = within(dialog).getByRole("textbox", { name: "Journal name" });
    await user.clear(input);
    await user.type(input, "  Renamed Notes  ");
    await user.click(within(dialog).getByRole("button", { name: "Save Changes" }));
    await waitFor(() => expect(renameJournal).toHaveBeenCalledWith("a", "Renamed Notes"));
    expect(await screen.findByText("Renamed Notes")).toBeInTheDocument();
    expect(screen.queryByRole("dialog", { name: "Rename Journal" })).not.toBeInTheDocument();
  });

  it("shows a rename error without closing the dialog", async () => {
    const user = setup();
    renameJournal.mockRejectedValue(new Error("Rename failed"));
    await screen.findByText("Active Notes");
    await manage(user, "Active Notes");
    await user.click(screen.getByRole("button", { name: "Rename" }));
    const dialog = screen.getByRole("dialog", { name: "Rename Journal" });
    await user.click(within(dialog).getByRole("button", { name: "Save Changes" }));
    expect(await within(dialog).findByRole("alert")).toHaveTextContent("Rename failed");
    expect(screen.getByText("Active Notes")).toBeInTheDocument();
  });

  it("does not archive when confirmation is declined", async () => {
    const user = setup();
    const confirm = vi.fn(() => false);
    vi.stubGlobal("confirm", confirm);
    await screen.findByText("Active Notes");
    await manage(user, "Active Notes");
    await user.click(screen.getByRole("button", { name: "Archive", exact: true }));
    expect(confirm).toHaveBeenCalledOnce();
    expect(archiveJournal).not.toHaveBeenCalled();
    expect(screen.getByText("Active Notes")).toBeInTheDocument();
  });

  it("archives a confirmed journal and removes it from the active view", async () => {
    const user = setup();
    vi.stubGlobal("confirm", () => true);
    archiveJournal.mockResolvedValue({ ...active, is_archived: true });
    await screen.findByText("Active Notes");
    await manage(user, "Active Notes");
    await user.click(screen.getByRole("button", { name: "Archive", exact: true }));
    await waitFor(() => expect(archiveJournal).toHaveBeenCalledWith("a"));
    await waitFor(() => expect(screen.queryByText("Active Notes")).not.toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: "Archived" }));
    expect(screen.getByText("Active Notes")).toBeInTheDocument();
  });

  it("restores an archived journal to the active view", async () => {
    const user = setup();
    restoreJournal.mockResolvedValue({ ...archived, is_archived: false });
    await screen.findByText("Active Notes");
    await user.click(screen.getByRole("button", { name: "Archived" }));
    await manage(user, "Old Notes");
    await user.click(screen.getByRole("button", { name: "Restore" }));
    await waitFor(() => expect(restoreJournal).toHaveBeenCalledWith("b"));
    await waitFor(() => expect(screen.queryByText("Old Notes")).not.toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: "Active" }));
    expect(screen.getByText("Old Notes")).toBeInTheDocument();
  });
});
