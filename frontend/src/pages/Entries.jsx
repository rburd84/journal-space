import {Plus} from "lucide-react";
import {Link, useParams} from "react-router";
import {useEffect, useState} from "react";

import EntryCard from "@/components/EntryCard";
import {Button} from "@/components/ui/button";
import {getEntries, getJournal, getJournals} from "@/lib/api.js";
import {DEV_USER_ID} from "@/lib/devUser.js";


export default function Entries() {
    const {journalId} = useParams();
    const [journal, setJournal] = useState(null);
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [favoritesOnly, setFavoritesOnly] = useState(false);
    const [journalNames, setJournalNames] = useState([]);


    useEffect(() => {
        let cancelled = false;

        async function loadEntries() {
            setLoading(true);
            setError("");
            setJournal(null);
            setEntries([]);
            setJournalNames({});

            try {
                if (journalId) {
                    const [journalData, entriesData] = await Promise.all([
                        getJournal(journalId),
                        getEntries(journalId),
                    ]);

                    if (!cancelled) {
                        setJournal(journalData);
                        setEntries(entriesData);
                    }
                } else {
                    const journals = await getJournals(DEV_USER_ID);

                    const activeJournals = journals.filter(
                        (journal) => !journal.is_archived
                    );

                    const namesById = Object.fromEntries(
                        activeJournals.map((journal) => [
                            journal.id,
                            journal.title,
                        ])
                    );

                    const entriesByJournal = await Promise.all(
                        activeJournals.map(journal => getEntries(journal.id))
                    );

                    if (!cancelled) {
                        setJournalNames(namesById);
                        setEntries(entriesByJournal.flat());
                    }
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

        void loadEntries();

        return () => {
            cancelled = true;
        };
    }, [journalId]);

    const visibleEntries = entries
        .filter(entry => {
            if (statusFilter === "all") return true;
            return entry.status === statusFilter;
        })
        .filter(entry => !favoritesOnly || entry.is_favorite)
        .sort(
            (a, b) =>
                new Date(b.created_at).getTime() -
                new Date(a.created_at).getTime()
        );

    return (
        <div>
            <header className="flex flex-wrap items-start justify-between gap-4">
                <div>
                    <p className="mb-3 text-sm font-medium uppercase tracking-wider text-sage-dark">
                        Entries
                    </p>

                    <h2 className="font-serif text-3xl text-ink md:text-4xl">
                        {journal?.title ?? "All Entries"}
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

            <div className="mt-8 flex flex-wrap items-center gap-3">
                <div
                    role="group"
                    aria-label="Filter entries by status"
                    className="flex flex-wrap gap-2"
                >
                    {[
                        {value: "all", label: "All"},
                        {value: "draft", label: "Drafts"},
                        {value: "published", label: "Published"},
                    ].map((filter) => (
                        <Button
                            key={filter.value}
                            variant={
                                statusFilter === filter.value
                                    ? "default"
                                    : "outline"
                            }
                            size="sm"
                            onClick={() => setStatusFilter(filter.value)}
                            aria-pressed={statusFilter === filter.value}
                        >
                            {filter.label}
                        </Button>
                    ))}
                </div>

                <label className="flex cursor-pointer items-center gap-2 text-sm text-ink">
                    <input
                        type="checkbox"
                        checked={favoritesOnly}
                        onChange={(event) =>
                            setFavoritesOnly(event.target.checked)
                        }
                        className="accent-sage"
                    />
                    Favorites only
                </label>
            </div>

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
                ) : visibleEntries.length === 0 ? (
                    <p className="text-sm text-[#667266]">
                        No entries match your filters.
                    </p>
                ) : (
                    visibleEntries.map((entry) => (
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
                            journalName={
                                !journalId
                                    ? journalNames[entry.journal_id]
                                    : undefined
                            }
                        />
                    ))
                )}
            </section>
        </div>
    );
}