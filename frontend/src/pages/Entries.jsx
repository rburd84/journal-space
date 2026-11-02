import {Plus} from "lucide-react";
import {Link} from "react-router";
import {useEffect, useState} from "react";

import EntryCard from "@/components/EntryCard";
import {Button} from "@/components/ui/button";


export default function Entries() {
    const [apiEntries, setApiEntries] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [fetchError, setFetchError] = useState(null);

    useEffect(() => {
        async function loadEntries() {
            try {
                const journalId = "17ec65a6-88db-44e3-aacf-6d81bd16fca9";

                const response = await fetch(
                    `/api/entries/?journal_id=${journalId}`
                );

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();
                setApiEntries(data);

                console.log("Entries from API:", data);
            } catch (error) {
                setFetchError(error.message);
                console.error("Failed to load entries:", error);
            } finally {
                setIsLoading(false);
            }
        }

        loadEntries();
    }, []);

    return (
        <div>
            <header className="flex flex-wrap items-start justify-between gap-4">
                <div>
                    <p className="mb-3 text-sm font-medium uppercase tracking-wider text-sage-dark">
                        Entries
                    </p>

                    <h2 className="font-serif text-3xl text-ink md:text-4xl">
                        Your entries
                    </h2>

                    <p className="mt-4 text-muted-foreground">
                        A collection of moments, thoughts, and reflections.
                    </p>
                </div>

                <Button
                    nativeButton={false}
                    render={<Link to="/entries/new"/>}
                    className="h-auto min-h-11 px-5 py-3">
                    <Plus size={18} aria-hidden="true"/>
                    New Entry
                </Button>
            </header>

            <section
                aria-label="Journal entries"
                className="mt-10 space-y-4"
            >
                {isLoading ? (
                    <p className="text-sm text-[#667266]">
                        Loading your entries...
                    </p>
                ) : fetchError ? (
                    <p className="text-sm text-red-700">
                        Unable to load entries: {fetchError}
                    </p>
                ) : apiEntries.length === 0 ? (
                    <p className="text-sm text-[#667266]">
                        No entries yet. Start writing your first entry.
                    </p>
                ) : (
                    apiEntries.map((entry) => (
                        <EntryCard
                            key={entry.id}
                            id={entry.id}
                            title={entry.title}
                            date={new Date(entry.created_at).toLocaleDateString(
                                "en-US",
                                {
                                    month: "long",
                                    day: "numeric",
                                    year: "numeric",
                                }
                            )}
                            status={entry.status}
                            isFavorite={entry.is_favorite}
                        />
                    ))
                )}
            </section>
        </div>
    );
}