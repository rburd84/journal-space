import {useEffect, useState} from "react";
import {Star} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Link, useParams} from "react-router";
import {DEV_USER_ID} from "@/lib/devUser.js";
import {getJournals} from "@/lib/api.js";

export default function Editor() {
    const {journalId, entryId} = useParams();
    const [title, setTitle] = useState("A quiet moment");
    const [content, setContent] = useState(
        "Today I found a little space to slow down and reflect."
    );
    const [isLoading, setIsLoading] = useState(false);
    const [loadError, setLoadError] = useState(null);
    const [isSaving, setIsSaving] = useState(false);
    const [saveError, setSaveError] = useState(null);
    const [savedEntry, setSavedEntry] = useState(null);
    const [saveSuccess, setSaveSuccess] = useState(false);
    const [isPublishing, setIsPublishing] = useState(false);
    const [publishError, setPublishError] = useState(null);
    const [selectedJournalId, setSelectedJournalId] = useState(journalId ?? "");
    const [availableJournals, setAvailableJournals] = useState([]);
    const [journalsLoading, setJournalsLoading] = useState(false);
    const [journalsError, setJournalsError] = useState("");
    const [isTogglingFavorite, setIsTogglingFavorite] = useState(false);
    const [favoriteError, setFavoriteError] = useState(null);
    const isEditMode = Boolean(entryId);
    const effectiveJournalId = isEditMode
        ? savedEntry?.journal_id
        : journalId || selectedJournalId;

    useEffect(() => {
        if (!entryId) return;

        const controller = new AbortController();

        async function loadEntry() {
            setIsLoading(true);
            setLoadError(null);
            setSaveSuccess(false);

            try {
                const response = await fetch(`/api/entries/${entryId}`, {
                    signal: controller.signal,
                });

                if (!response.ok) {
                    throw new Error(
                        `Failed to load entry (HTTP ${response.status})`
                    );
                }

                const entry = await response.json();

                if (controller.signal.aborted) return;

                setTitle(entry.title);
                setContent(entry.content);
                setSavedEntry(entry);
            } catch (error) {
                if (error.name !== "AbortError") {
                    setLoadError(error.message);
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
        if (journalId || entryId) return;

        let cancelled = false;

        async function loadJournals() {
            setJournalsLoading(true);
            setJournalsError("");

            try {
                const data = await getJournals(DEV_USER_ID);

                if (!cancelled) {
                    setAvailableJournals(
                        data.filter((journal) => !journal.is_archived)
                    );
                }
            } catch (error) {
                if (!cancelled) {
                    setJournalsError(error.message);
                }
            } finally {
                if (!cancelled) {
                    setJournalsLoading(false);
                }
            }
        }

        void loadJournals();

        return () => {
            cancelled = true;
        };
    }, [journalId, entryId]);

    async function handleSaveDraft() {
        if (
            isSaving ||
            !title.trim() ||
            (!savedEntry && !effectiveJournalId)
        ) return;

        setIsSaving(true);
        setSaveError(null);
        setSaveSuccess(false);

        try {
            const isExistingEntry = savedEntry !== null;

            const url = isExistingEntry
                ? `/api/entries/${savedEntry.id}`
                : "/api/entries/";

            const response = await fetch(url, {
                method: isExistingEntry ? "PATCH" : "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(
                    isExistingEntry
                        ? {
                            title: title.trim(),
                            content,
                        }
                        : {
                            journal_id: effectiveJournalId,
                            title: title.trim(),
                            content,
                        }
                )
            });

            if (!response.ok) {
                const errorBody = await response.text();

                console.error("Save failed:", {
                    status: response.status,
                    body: errorBody,
                });

                throw new Error(
                    `Failed to save entry (HTTP ${response.status}): ${errorBody}`
                );
            }

            const entry = await response.json();

            setSavedEntry(entry);
            setSaveSuccess(true);
            console.log("Saved draft:", entry);
        } catch (error) {
            setSaveError(error.message);
        } finally {
            setIsSaving(false);
        }
    }

    async function handlePublish() {
        if (!savedEntry || isPublishing || savedEntry.status === "published") {
            return;
        }

        setIsPublishing(true);
        setPublishError(null);

        try {
            const response = await fetch(
                `/api/entries/${savedEntry.id}/publish`,
                {method: "PATCH",}
            );

            if (!response.ok) {
                throw new Error(`Failed to publish entry (HTTP ${response.status})`);
            }

            const publishedEntry = await response.json();
            setSavedEntry(publishedEntry);
        } catch (error) {
            setPublishError(error.message);
        } finally {
            setIsPublishing(false);
        }
    }

    async function handleToggleFavorite() {
        if (!savedEntry || isTogglingFavorite) return;

        setIsTogglingFavorite(true);
        setFavoriteError(null);

        try {
            const response = await fetch(
                `/api/entries/${savedEntry.id}/favorite`,
                {method: "PATCH"}
            );

            if (!response.ok) {
                throw new Error(
                    `Failed to update favorite (HTTP ${response.status})`
                );
            }

            const updatedEntry = await response.json();
            setSavedEntry(updatedEntry);
        } catch (error) {
            setFavoriteError(error.message);
        } finally {
            setIsTogglingFavorite(false);
        }
    }

    if (isEditMode && isLoading) {
        return <p className="p-6 text-muted-foreground">Loading entry...</p>;
    }

    if (isEditMode && (loadError || !savedEntry)) {
        return (
            <p role="alert" className="p-6 text-red-700">
                {loadError || "Entry could not be loaded."}
            </p>
        );
    }

    return (
        <div className="mx-auto w-full min-w-0 max-w-[760px]">
            <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
                <div>
                    {!isEditMode && !journalId ? (
                        <div>
                            <label
                                htmlFor="entry-journal"
                                className="mb-2 block text-sm font-medium text-sage-dark"
                            >
                                Write in journal
                            </label>

                            {journalsLoading ? (
                                <p className="text-sm text-muted-foreground">
                                    Loading journals...
                                </p>
                            ) : journalsError ? (
                                <p role="alert" className="text-sm text-red-700">
                                    Unable to load journals: {journalsError}
                                </p>
                            ) : availableJournals.length === 0 ? (
                                <p className="text-sm text-muted-foreground">
                                    No active journals.{" "}
                                    <Link to="/journals" className="text-sage-dark underline">
                                        Create a journal
                                    </Link>
                                </p>
                            ) : (
                                <select
                                    id="entry-journal"
                                    value={selectedJournalId}
                                    onChange={e => setSelectedJournalId(e.target.value)}
                                    className="rounded-lg border border-paper-border bg-paper px-3 py-2 text-sm text-ink outline-none"
                                >
                                    <option value="">Select a journal</option>

                                    {availableJournals.map((journal) => (
                                        <option key={journal.id} value={journal.id}>
                                            {journal.title}
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>
                    ) : (
                        <p className="text-sm font-medium text-sage-dark">
                            {availableJournals.find((journal) => journal.id === effectiveJournalId)?.title
                                ?? "Journal Entry"}
                        </p>
                    )}

                    <p className="mt-1 text-sm text-muted-foreground">
                        {savedEntry?.created_at
                            ? new Date(savedEntry.created_at).toLocaleDateString()
                            : new Date().toLocaleDateString()}
                    </p>
                </div>

                <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-muted-foreground">
                    {savedEntry?.status === "published" ? "Published" : "Draft"}
                </span>
            </header>

            <section
                aria-label="Journal editor"
                className="rounded-xl border border-paper-border bg-paper px-5 py-8 sm:px-8 md:px-12 md:py-12"
            >
                <label htmlFor="entry-title" className="sr-only">
                    Entry title
                </label>

                <input
                    id="entry-title"
                    type="text"
                    value={title}
                    onChange={(e) => {
                        setTitle(e.target.value);
                        setSaveSuccess(false);
                    }}
                    placeholder="Untitled entry"
                    className="block w-full min-w-0 border-0 bg-transparent font-serif text-[clamp(1.75rem,5vw,2.5rem)] leading-tight text-ink outline-none"
                />

                <div className="my-8 h-px bg-paper-border"/>

                <label htmlFor="entry-content" className="sr-only">
                    Entry content
                </label>

                <textarea
                    id="entry-content"
                    value={content}
                    onChange={(e) => {
                        setContent(e.target.value);
                        setSaveSuccess(false);
                    }}
                    placeholder="Begin writing..."
                    rows={12}
                    className="block w-full min-w-0 resize-y border-0 bg-transparent font-serif text-[17px] leading-[1.8] text-ink outline-none md:text-lg"
                />
            </section>

            <footer className="mt-6 flex flex-wrap items-center justify-between gap-4">
                <Button
                    variant="outline"
                    className="h-auto min-h-11 px-4 py-3"
                    onClick={handleToggleFavorite}
                    disabled={!savedEntry || isTogglingFavorite}
                    aria-pressed={Boolean(savedEntry?.is_favorite)}
                >
                    <Star
                        size={18}
                        className={savedEntry?.is_favorite ? "fill-sage text-sage" : ""}
                        aria-hidden="true"
                    />
                    {isTogglingFavorite
                        ? "Updating..."
                        : savedEntry?.is_favorite
                            ? "Favorited"
                            : "Favorite"}
                </Button>

                {favoriteError && (
                    <p role="alert" className="text-sm text-red-700">
                        {favoriteError}
                    </p>
                )}

                <div className="flex flex-wrap gap-3">
                    <Button
                        variant="outline"
                        className="h-auto min-h-11 px-5 py-3"
                        onClick={handleSaveDraft}
                        disabled={
                            isSaving ||
                            !title.trim() ||
                            (!savedEntry && !effectiveJournalId)
                        }
                    >
                        {isSaving
                            ? "Saving..."
                            : savedEntry
                                ? "Save Changes"
                                : "Save Draft"}
                    </Button>

                    <Button
                        className="h-auto min-h-11 px-5 py-3"
                        onClick={handlePublish}
                        disabled={
                            !savedEntry ||
                            isPublishing ||
                            savedEntry.status === "published"
                        }
                    >
                        {isPublishing
                            ? "Publishing..."
                            : savedEntry?.status === "published"
                                ? "Published"
                                : "Publish"}
                    </Button>
                </div>

                {saveError && (
                    <p role="alert" className="mt-4 text-sm text-red-700">
                        {saveError}
                    </p>
                )}

                {saveSuccess && (
                    <p role="status" className="mt-4 text-sm text-sage-dark">
                        Entry saved successfully.
                    </p>
                )}

                {publishError && (
                    <p role="alert" className="mt-4 text-sm text-red-700">
                        {publishError}
                    </p>
                )}

                {savedEntry?.status === "published" && (
                    <p role="status" className="mt-4 text-sm text-sage-dark">
                        Entry published successfully.
                    </p>
                )}

            </footer>
        </div>
    );
}

