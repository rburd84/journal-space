import {Plus} from "lucide-react";
import {Link, useParams} from "react-router";
import {useEffect, useState} from "react";

import EntryCard from "@/components/EntryCard";
import {Button} from "@/components/ui/button";
import {getEntries, getJournal} from "@/lib/api.js";


export default function Entries() {
    const {journalId} = useParams();
    const [journal, setJournal] = useState(null);
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {
        if (!journalId) {
            setLoading(false);
            return;
        }

        let cancelled = false;

        async function loadJournalEntries() {
            setLoading(true);
            setError("");

            try {
                const [journalData, entriesData] = await Promise.all([
                    getJournal(journalId),
                    getEntries(journalId),
                ]);

                if (!cancelled) {
                    setJournal(journalData);
                    setEntries(entriesData);
                }
            } catch (error) {
                if (!cancelled) {
                    setError(error.message);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        void loadJournalEntries();

        return () => {
            cancelled = true;
        };
    }, [journalId]);

    return (
        <div>
            <header className="flex flex-wrap items-start justify-between gap-4">
                <div>
                    <p className="mb-3 text-sm font-medium uppercase tracking-wider text-sage-dark">
                        Entries
                    </p>

                    <h2 className="font-serif text-3xl text-ink md:text-4xl">
                        {journal?.title ?? "Journal Entries"}
                    </h2>

                    <p className="mt-4 text-muted-foreground">
                        A collection of moments, thoughts, and reflections.
                    </p>
                </div>

                <Button
                    nativeButton={false}
                    render={<Link to={
                                      journalId
                                          ? `/journals/${journalId}/entries/new`
                                          : "/entries/new"
                                  }/>}
                    className="h-auto min-h-11 px-5 py-3">
                    <Plus size={18} aria-hidden="true"/>
                    New Entry
                </Button>
            </header>

            <section
                aria-label="Journal entries"
                className="mt-10 space-y-4"
            >
                {loading ? (
                    <p className="text-sm text-[#667266]">
                        Loading your entries...
                    </p>
                ) : error ? (
                    <p className="text-sm text-red-700">
                        Unable to load entries: {error}
                    </p>
                ) : entries.length === 0 ? (
                    <p className="text-sm text-[#667266]">
                        No entries yet. Start writing your first entry.
                    </p>
                ) : (
                    entries.map((entry) => (
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