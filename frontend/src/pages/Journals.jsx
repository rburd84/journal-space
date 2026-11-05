import {useEffect, useState} from "react";
import {archiveJournal, getJournals} from "@/lib/api.js";
import {DEV_USER_ID} from "@/lib/devUser.js";
import CreateJournalDialog from "@/components/CreateJournalDialog.jsx";
import ManageJournalCard from "@/components/ManageJournalCard.jsx";
import {Button} from "@/components/ui/button.jsx";

// const sampleJournals = [{
//     id: "journal-1", title: "Daily Reflections", description: "Personal journal",
// }, {
//     id: "journal-2", title: "Small Moments", description: "Personal journal",
// }, {
//     id: "journal-3", title: "Ideas & Notes", description: "Creative journal",
// }, {
//     id: "journal-4", title: "Evening Pages", description: "Personal journal",
// },]

export default function Journals() {
    const [journals, setJournals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [journalToRename, setJournalToRename] = useState(null);
    const [renameTitle, setRenameTitle] = useState("");
    const [actionError, setActionError] = useState("");
    const [saving, setSaving] = useState(false);

    function startRename(journal) {
        setJournalToRename(journal);
        setRenameTitle(journal.title);
        setActionError("");
    }


    function handleJournalCreated(journal) {
        setJournals((current) =>
            [...current, journal].sort((a, b) =>
                a.title.localeCompare(b.title)));
    }

    useEffect(() => {
        async function loadJournals() {
            try {
                const data = await getJournals(DEV_USER_ID);
                setJournals(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        }

        void loadJournals();
    }, []);

    async function handleRename(event) {
        event.preventDefault();

        if (!journalToRename || !renameTitle || saving) return;

        setSaving(true);
        setActionError("");

        try {
            const updated = await renameJournal(
                journalToRename.id,
                renameTitle.trim()
            );

            setJournals((current) =>
                current
                    .map((journal) =>
                        journal.id === updated.id ? updated : journal
                    )
                    .sort((a, b) => a.title.localeCompare(b.title))
            );

            setJournalToRename(null);
        } catch (error) {
            setActionError(error.message);
        } finally {
            setSaving(false);
        }
    }

    async function handleArchive(journal) {
        const confirmed = window.confirm(
            `Archive "${journal.title}"? Its entries will be preserved.`
        );

        if (!confirmed) return;

        setSaving(true);
        setActionError("");

        try {
            const updated = await archiveJournal(journal.id);

            setJournals((current) =>
                current.map((item) =>
                    item.id === updated.id ? updated : item));
        } catch (error) {
            setActionError(error.message);
        } finally {
            setSaving(false);
        }
    }

    if (loading) return <p>Loading journals...</p>;
    if (error) return <p role="alert">{error}</p>;

    return (<div>
        <header className="flex flex-wrap items-center justify-between gap-4">
            <div>
                <p className="mb-3 text-sm font-medium uppercase tracking-wider text-sage-dark">
                    My Journals
                </p>

                <h2 className="font-serif text-3xl text-ink md:text-4xl">
                    Your journals
                </h2>

                <p className="mt-4 text-muted-foreground">
                    A home for the thoughts you want to keep.
                </p>
            </div>

            <CreateJournalDialog onCreated={handleJournalCreated}/>
        </header>

        <section
            aria-label="Journal collection"
            className="mt-10 grid w-full grid-cols-1 gap-5 md:grid-cols-2">
            {journals.filter(journal => !journal.is_archived).length === 0 ? (
                <p className="text-[#6B7168] md:col-span-2">
                    No active journals yet. Create your first journal.
                </p>
            ) : (
                journals
                    .filter(journal => !journal.is_archived)
                    .map((journal) => (
                        <ManageJournalCard
                            key={journal.id}
                            journal={journal}
                            onRename={startRename}
                            onArchive={handleArchive}
                        />
                    )))}
        </section>

        {journalToRename && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
                <div
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="rename-journal-title"
                    className="w-full max-w-md rounded-2xl bg-paper p-6 shadow-xl sm:p-8"
                >
                    <h2
                        id="rename-journal-title"
                        className="font-serif text-2xl text-ink"
                    >
                        Rename Journal
                    </h2>

                    <form onSubmit={handleRename} className="mt-6 space-y-5">
                        <div className="space-y-2">
                            <label
                                htmlFor="rename-title"
                                className="block text-sm font-medium"
                            >
                                Journal name
                            </label>

                            <input
                                id="rename-title"
                                value={renameTitle}
                                onChange={(event) => setRenameTitle(event.target.value)}
                                maxLength={200}
                                required
                                autoFocus
                                className="w-full rounded-lg border  bg-white px-4 py-3 outline-none focus:border-sage"
                            />
                        </div>

                        {actionError && (
                            <p role="alert" className="text-sm text-red-700">
                                {actionError}
                            </p>
                        )}

                        <div className="flex justify-end gap-3">
                            <Button
                                type="button"
                                variant="outline"
                                disabled={saving}
                                onClick={() => setJournalToRename(null)}
                            >
                                Cancel
                            </Button>

                            <Button
                                type="submit"
                                disabled={saving || !renameTitle.trim()}
                            >
                                {saving ? "Saving..." : "Save Changes"}
                            </Button>
                        </div>
                    </form>
                </div>
            </div>
        )}

        {actionError && !journalToRename && (
            <p role="alert" className="mt-4 text-sm text-red-700">
                {actionError}
            </p>
        )}
    </div>);
}

























