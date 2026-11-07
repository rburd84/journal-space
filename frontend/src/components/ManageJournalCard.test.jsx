import {describe, expect, it, vi} from "vitest";
import {render, screen} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {MemoryRouter} from "react-router";
import ManageJournalCard from "@/components/ManageJournalCard.jsx";

const activeJournal = {
    id: "journal-1",
    title: "Morning Notes",
    type: "personal",
    is_archived: false,
};

function setup(journal = activeJournal) {
    const user = userEvent.setup();
    const onRename = vi.fn();
    const onArchive = vi.fn();
    const onRestore = vi.fn();

    render(
        <MemoryRouter>
            <ManageJournalCard
                journal={journal}
                onRename={onRename}
                onArchive={onArchive}
                onRestore={onRestore}
            />
        </MemoryRouter>
    );

    return {user, onRename, onArchive, onRestore};
}

describe("ManageJournalCard", () => {
    it("displays the journal title and type", () => {
        setup();
        expect(screen.getByRole("heading", {name: "Morning Notes"})).toBeInTheDocument();
        expect(screen.getByText("personal journal")).toBeInTheDocument();
    });

    it("links to the journal entries page", () => {
        setup();
        expect(screen.getByRole("link", {name: /Morning Notes/i}))
            .toHaveAttribute("href", "/journals/journal-1/entries");
    });

    it("opens and closes the management menu", async () => {
        const {user} = setup();
        const manage = screen.getByRole("button", {name: "Manage Morning Notes"});
        expect(screen.queryByRole("button", {name: "Rename"})).not.toBeInTheDocument();
        await user.click(manage);
        expect(screen.getByRole("button", {name: "Rename"})).toBeInTheDocument();
        await user.click(manage);
        expect(screen.queryByRole("button", {name: "Rename"})).not.toBeInTheDocument();
    });

    it("calls onRename with the journal and closes the menu", async () => {
        const {user, onRename} = setup();
        await user.click(screen.getByRole("button", {name: "Manage Morning Notes"}));
        await user.click(screen.getByRole("button", {name: "Rename"}));
        expect(onRename).toHaveBeenCalledExactlyOnceWith(activeJournal);
        expect(screen.queryByRole("button", {name: "Rename"})).not.toBeInTheDocument();
    });

    it("offers Archive rather than Restore for active journals", async () => {
        const {user} = setup();
        await user.click(screen.getByRole("button", {name: "Manage Morning Notes"}));
        expect(screen.getByRole("button", {name: "Archive"})).toBeInTheDocument();
        expect(screen.queryByRole("button", {name: "Restore"})).not.toBeInTheDocument();
    });

    it("calls onArchive with the active journal and closes the menu", async () => {
        const {user, onArchive, onRestore} = setup();
        await user.click(screen.getByRole("button", {name: "Manage Morning Notes"}));
        await user.click(screen.getByRole("button", {name: "Archive"}));
        expect(onArchive).toHaveBeenCalledExactlyOnceWith(activeJournal);
        expect(onRestore).not.toHaveBeenCalled();
        expect(screen.queryByRole("button", {name: "Archive"})).not.toBeInTheDocument();
    });

    it("offers Restore for archived journals and calls onRestore", async () => {
        const archivedJournal = {...activeJournal, is_archived: true};
        const {user, onRestore, onArchive} = setup(archivedJournal);
        await user.click(screen.getByRole("button", {name: "Manage Morning Notes"}));
        expect(screen.queryByRole("button", {name: "Archive"})).not.toBeInTheDocument();
        await user.click(screen.getByRole("button", {name: "Restore"}));
        expect(onRestore).toHaveBeenCalledExactlyOnceWith(archivedJournal);
        expect(onArchive).not.toHaveBeenCalled();
        expect(screen.queryByRole("button", {name: "Restore"})).not.toBeInTheDocument();
    });
});
