import {beforeEach, describe, expect, it, vi} from "vitest";
import {render, screen, waitFor} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CreateJournalDialog from "@/components/CreateJournalDialog";
import {createJournal} from "@/lib/api";
import {DEV_USER_ID} from "@/lib/devUser.js";

vi.mock("@/lib/api", () => ({createJournal: vi.fn()}));

const openDialog = async (user) => {
    await user.click(screen.getByRole("button", {name: /new journal/i}));
    // The current component sets aria-hidden="true" on the dialog.
    // Query by heading until the accessibility issue is fixed separately.
    expect(screen.getByRole("heading", {name: /create a journal/i, hidden: true})).toBeInTheDocument();
};

beforeEach(() => {
    vi.resetAllMocks();
});

describe("CreateJournalDialog", () => {
    it("starts closed and opens when New Journal is clicked", async () => {
        const user = userEvent.setup();
        render(<CreateJournalDialog onCreated={vi.fn()}/>);
        expect(screen.queryByRole("heading", {name: /create a journal/i, hidden: true})).not.toBeInTheDocument();
        await openDialog(user);
        expect(screen.getByLabelText(/journal name/i)).toBeInTheDocument();
    });

    it("starts with Personal as the selected journal type", async () => {
        const user = userEvent.setup();
        render(<CreateJournalDialog onCreated={vi.fn()}/>);
        await openDialog(user);
        expect(screen.getByLabelText(/journal type/i)).toHaveValue("personal");
        expect(
            screen.getByLabelText(/journal type/i).querySelectorAll("option")
        ).toHaveLength(6);
    });

    it("disables submission for an empty or whitespace-only title", async () => {
        const user = userEvent.setup();
        render(<CreateJournalDialog onCreated={vi.fn()}/>);
        await openDialog(user);
        const submit = screen.getByRole("button", {name: /^create journal$/i, hidden: true});
        expect(submit).toBeDisabled();
        await user.type(screen.getByLabelText(/journal name/i), "   ");
        expect(submit).toBeDisabled();
        expect(createJournal).not.toHaveBeenCalled();
    });

    it("creates a journal with a trimmed title and selected type", async () => {
        const user = userEvent.setup();
        const journal = {id: "journal-1", title: "My Dreams", type: "dream"};
        createJournal.mockResolvedValue(journal);
        const onCreated = vi.fn();
        render(<CreateJournalDialog onCreated={onCreated}/>);
        await openDialog(user);
        await user.type(screen.getByLabelText(/journal name/i), "  My Dreams  ");
        await user.selectOptions(screen.getByLabelText(/journal type/i), "dream");
        await user.click(screen.getByRole("button", {name: /^create journal$/i, hidden: true}));
        await waitFor(() => expect(onCreated).toHaveBeenCalledWith(journal));
        expect(createJournal).toHaveBeenCalledWith({
            userId: DEV_USER_ID,
            title: "My Dreams",
            type: "dream",
        });
        expect(createJournal).toHaveBeenCalledTimes(1);
        expect(screen.queryByRole("heading", {name: /create a journal/i, hidden: true})).not.toBeInTheDocument();
    });

    it("shows an API error and leaves the dialog open for retry", async () => {
        const user = userEvent.setup();
        createJournal.mockRejectedValue(new Error("Unable to create journal"));
        const onCreated = vi.fn();
        render(<CreateJournalDialog onCreated={onCreated}/>);
        await openDialog(user);
        await user.type(screen.getByLabelText(/journal name/i), "My Journal");
        await user.click(screen.getByRole("button", {name: /^create journal$/i, hidden: true}));
        expect(await screen.findByRole("alert", {hidden: true})).toHaveTextContent("Unable to create journal");
        expect(screen.getByRole("heading", {name: /create a journal/i, hidden: true})).toBeInTheDocument();
        expect(onCreated).not.toHaveBeenCalled();
    });

    it("closes without calling the API when canceled", async () => {
        const user = userEvent.setup();
        render(<CreateJournalDialog onCreated={vi.fn()}/>);
        await openDialog(user);
        await user.type(screen.getByLabelText(/journal name/i), "Not saved");
        await user.click(screen.getByRole("button", {name: /cancel/i, hidden: true}));
        expect(screen.queryByRole("heading", {name: /create a journal/i, hidden: true})).not.toBeInTheDocument();
        expect(createJournal).not.toHaveBeenCalled();
    });

    it("prevents duplicate submissions while the request is pending", async () => {
        const user = userEvent.setup();
        let resolveRequest;
        createJournal.mockImplementation(() => new Promise((resolve) => {
            resolveRequest = resolve;
        }));
        const onCreated = vi.fn();
        render(<CreateJournalDialog onCreated={onCreated}/>);
        await openDialog(user);
        await user.type(screen.getByLabelText(/journal name/i), "Once only");
        await user.click(screen.getByRole("button", {name: /^create journal$/i, hidden: true}));
        expect(screen.getByRole("button", {name: /creating/i, hidden: true})).toBeDisabled();
        expect(screen.getByRole("button", {name: /cancel/i, hidden: true})).toBeDisabled();
        expect(createJournal).toHaveBeenCalledTimes(1);
        resolveRequest({id: "journal-2", title: "Once only"});
        await waitFor(() => expect(onCreated).toHaveBeenCalledTimes(1));
    });
});
