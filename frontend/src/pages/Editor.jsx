import {useState, useEffect} from "react";
import {Star} from "lucide-react";
import {Button} from "@/components/ui/button";
import {useParams} from "react-router";

export default function Editor() {
    const [title, setTitle] = useState("A quiet moment");
    const {journalId, entryId} = useParams();
    const [content, setContent] = useState(
        "Today I found a little space to slow down and reflect."
    );
    const [isLoading, setIsLoading] = useState(false);
    const [loadError, setLoadError] = useState(null);
    const [isSaving, setIsSaving] = useState(false);
    const [saveError, setSaveError] = useState(null);
    const [savedEntry, setSavedEntry] = useState(null);
    const [isPublishing, setIsPublishing] = useState(false);
    const [publishError, setPublishError] = useState(null);
    const isEditMode = Boolean(entryId);

    useEffect(() => {
        if (!entryId) return;

        const controller = new AbortController();

        async function loadEntry() {
            setIsLoading(true);
            setLoadError(null);

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

        loadEntry();

        return () => controller.abort();
    }, [entryId]);

    async function handleSaveDraft() {
        if (isSaving || !title.trim()) return;

        setIsSaving(true);
        setSaveError(null);

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
                            journal_id: journalId,
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
        <div className="mx-auto max-w-[760px]">
            <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
                <div>
                    <p className="text-sm font-medium text-sage-dark">
                        Daily Reflections
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                        October 31, 2026
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
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Untitled entry"
                    className="w-full border-0 bg-transparent font-serif text-[30px] leading-tight text-ink outline-none placeholder:text-muted-foreground md:text-4xl"
                />

                <div className="my-8 h-px bg-paper-border"/>

                <label htmlFor="entry-content" className="sr-only">
                    Entry content
                </label>

                <textarea
                    id="entry-content"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Begin writing..."
                    rows={12}
                    className="w-full resize-y border-0 bg-transparent font-serif text-[17px] leading-[1.8] text-ink outline-none placeholder:text-muted-foreground md:text-lg"
                />
            </section>

            <footer className="mt-6 flex flex-wrap items-center justify-between gap-4">
                <Button variant="outline" className="h-auto min-h-11 px-4 py-3">
                    <Star size={18} aria-hidden="true"/>
                    Favorite
                </Button>

                <div className="flex flex-wrap gap-3">
                    <Button
                        variant="outline"
                        className="h-auto min-h-11 px-5 py-3"
                        onClick={handleSaveDraft}
                        disabled={isSaving || !title.trim()}
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

                {savedEntry && (
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

