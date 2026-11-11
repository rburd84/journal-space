import {Star, Trash2} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Link, useNavigate, useParams} from "react-router";
import {useEffect, useState} from "react";
import {apiFetch, getJournal} from "@/lib/api.js";


export default function Reader() {
    const {entryId} = useParams();
    const navigate = useNavigate();
    const [entry, setEntry] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [journalTitle, setJournalTitle] = useState("");
    const [isTogglingFavorite, setIsTogglingFavorite] = useState(false);
    const [favoriteError, setFavoriteError] = useState(null);
    const [isDeleting, setIsDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState(null);

    useEffect(() => {
        const controller = new AbortController();

        async function loadEntry() {
            setIsLoading(true);
            setError(null);
            setEntry(null);

            try {
                const response = await apiFetch(`/entries/${entryId}`, {
                    signal: controller.signal,
                });

                if (!response.ok) {
                    throw new Error(
                        response.status === 404
                            ? "Entry not found."
                            : `Failed to load entry (HTTP ${response.status})`
                    );
                }

                const data = await response.json();

                if (!controller.signal.aborted) {
                    setEntry(data);
                }
            } catch (error) {
                if (!controller.signal.aborted) {
                    setError(error.message);
                }
            } finally {
                if (!controller.signal.aborted) {
                    setIsLoading(false);
                }
            }
        }

        void loadEntry();

        return () => controller.abort();
    }, [entryId]);

    useEffect(() => {
        if (!entry?.journal_id) return;

        let cancelled = false;

        async function loadJournal() {
            try {
                const journal = await getJournal(entry.journal_id);

                if (!cancelled) {
                    setJournalTitle(journal.title);
                }
            } catch (error) {
                console.error("Unable to load journal:", error);
            }
        }

        void loadJournal();

        return () =>
            cancelled = true;
    }, [entry?.journal_id]);

    async function handleToggleFavorite() {
        if (!entry || isTogglingFavorite) return;

        setIsTogglingFavorite(true);
        setFavoriteError(null);

        try {
            const response = await apiFetch(`/entries/${entry.id}/favorite`,
                {method: "PATCH"}
            );

            if (!response.ok) {
                throw new Error(
                    `Failed to update favorite (HTTP ${response.status})`
                );
            }

            const updatedEntry = await response.json();

            setEntry(updatedEntry);
        } catch (error) {
            setFavoriteError(error.message);
        } finally {
            setIsTogglingFavorite(false);
        }
    }

    async function handleDelete() {
        if (!entry || isDeleting) return;

        const confirmed = window.confirm(
            "Delete this entry permanently? This action cannot be undone."
        );

        if (!confirmed) return;

        setIsDeleting(true);
        setDeleteError(null);

        try {
            const response = await apiFetch(`/entries/${entry.id}`,
                {method: "DELETE"}
            );

            if (!response.ok) {
                throw new Error(
                    `Failed to delete entry (HTTP ${response.status})`
                );
            }

            navigate(`/journals/${entry.journal_id}/entries`, {
                replace: true,
            });
        } catch (error) {
            setDeleteError(error.message);
        } finally {
            setIsDeleting(false);
        }
    }

    if (isLoading) {
        return (
            <p className="p-6 text-muted-foreground">
                Loading entry...
            </p>
        );
    }

    if (!entry) {
        return (
            <p role="alert" className="text-red-700">
                {error || "Entry not found."}
            </p>
        );
    }

    return (
        <div className="mx-auto max-w-[760px]">
            <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
                <div>
                    <p className="text-sm font-medium text-sage-dark">
                        {journalTitle || "Journal Entry"}
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                        {new Date(entry.created_at).toLocaleDateString("en-US", {
                            month: "long",
                            day: "numeric",
                            year: "numeric",
                        })}
                    </p>
                </div>

                <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${
                        entry.status === "published"
                            ? "bg-sidebar-selected text-sage-dark"
                            : "bg-secondary text-muted-foreground"
                    }`}
                >
                    {entry.status === "published" ? "Published" : "Draft"}
                </span>
            </header>

            <article className="rounded-xl border border-paper-border bg-paper px-5 py-8 sm:px-8 md:px-12 md:py-12">
                <h1 className="font-serif text-[30px] leading-tight text-ink md:text-4xl">
                    {entry.title}
                </h1>

                <div className="my-8 h-px bg-paper-border"/>

                <div
                    className="min-w-0 whitespace-pre-wrap break-words font-serif text-[17px] leading-[1.8] text-ink md:text-lg">
                    {entry.content}
                </div>
            </article>

            <footer className="mt-6 flex flex-wrap items-center justify-between gap-4">
                <Button
                    variant="outline"
                    className="h-auto min-h-11 px-4 py-3"
                    onClick={handleToggleFavorite}
                    disabled={isTogglingFavorite}
                    aria-pressed={Boolean(entry.is_favorite)}
                >
                    <Star
                        size={18}
                        className={entry.is_favorite ? "fill-sage text-sage" : ""}
                        aria-hidden="true"
                    />
                    {isTogglingFavorite
                        ? "Updating..."
                        : entry.is_favorite ? "Favorited" : "Favorite"
                    }
                </Button>

                {favoriteError && (
                    <p role="alert" className="text-sm text-red-700">
                        {favoriteError}
                    </p>
                )}

                <div className="flex gap-2">
                    <Button
                        nativeButton={false}
                        render={<Link to={`/entries/${entry.id}/edit`}/>}
                        className="h-auto min-h-11 px-5 py-3"
                    >
                        Edit Entry
                    </Button>

                    <Button
                        variant="outline"
                        className="h-auto min-h-11 px-4 py-3 text-red-700"
                        onClick={handleDelete}
                        disabled={isDeleting}
                    >
                        <Trash2 size={18} aria-hidden={true}/>
                        {isDeleting ? "Deleting..." : "Delete Entry"}
                    </Button>

                    {deleteError && (
                        <p role="alert" className="w-full text-sm text-red-700">
                            {deleteError}
                        </p>
                    )}
                </div>
            </footer>
        </div>
    );
}




















