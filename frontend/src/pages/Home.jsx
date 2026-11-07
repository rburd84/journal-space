import {useEffect, useState} from 'react';
import {PenLine} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Link} from "react-router";
import JournalCard from "@/components/JournalCard.jsx";

import {getEntries, getJournals} from "@/lib/api.js";
import {DEV_USER_ID} from "@/lib/devUser.js";
import EntryCard from "@/components/EntryCard.jsx";


export default function Home() {
    const [journals, setJournals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [entryCount, setEntryCount] = useState(0);
    const [recentEntries, setRecentEntries] = useState([]);


    useEffect(() => {
        let cancelled = false;

        async function loadJournals() {
            try {
                const data = await getJournals(DEV_USER_ID);

                const active = data.filter(
                    journal => !journal.is_archived
                );

                const entriesByJournal = await Promise.all(
                    active.map(journal => getEntries(journal.id))
                );

                const journalNames = Object.fromEntries(
                    active.map(journal => [journal.id, journal.title])
                );

                const allEntries = entriesByJournal.flat();

                const latestEntries = [...allEntries]
                    .sort(
                        (a, b) =>
                            new Date(b.created_at).getTime() -
                            new Date(a.created_at).getTime()
                    )
                    .slice(0, 5)
                    .map(entry => ({
                        ...entry,
                        journalName: journalNames[entry.journal_id],
                    }));

                if (!cancelled) {
                    setJournals(data);
                    setEntryCount(allEntries.length);
                    setRecentEntries(latestEntries);
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

        void loadJournals();

        return () => {
            cancelled = true;
        };
    }, []);

    const activeJournals = journals
        .filter(journal => !journal.is_archived);

    const previewJournals = activeJournals.slice(0, 3);

    return (
        <div>
            <header>
                <p className="mb-3 text-sm font-medium uppercase tracking-wider text-sage-dark">
                    Home
                </p>

                <h2 className="font-serif text-3xl text-ink md:text-4xl">
                    A quiet moment for yourself.
                </h2>

                <p className="mt-4 max-w-xl text-muted-foreground">
                    Your thoughts have a place here. Begin whenever you're ready.
                </p>
            </header>

            <section
                aria-label="Your journal activity"
                className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2"
            >
                <div className="rounded-xl border border-paper-border bg-paper p-6">
                    <p className="text-sm font-medium text-muted-foreground">
                        Active journals
                    </p>

                    <p className="mt-3 font-serif text-3xl text-ink">
                        {loading ? "-" : error ? "-" : activeJournals.length}
                    </p>
                </div>

                <div className="rounded-xl border border-paper-border bg-paper p-6">
                    <p className="text-sm font-medium text-muted-foreground">
                        Total entries
                    </p>

                    <p className="mt-3 font-serif text-3xl text-ink">
                        {loading ? "-" : error ? "-" : entryCount}
                    </p>
                </div>
            </section>

            <section className="mt-10 rounded-xl border border-paper-border bg-paper p-6 md:p-10">
                <div className="flex items-center gap-2 text-sage-dark">
                    <PenLine size={20} aria-hidden="true"/>
                    <span className="text-sm font-medium">
                        Your writing space
                    </span>
                </div>

                <h3 className="mt-6 font-serif text-2xl text-ink md:text-3xl">
                    Every thought deserves a little space.
                </h3>

                <p className="mt-4 max-w-lg leading-7 text-muted-foreground">
                    Start with a few words. There's no right way to begin.
                </p>

                <Button
                    nativeButton={false}
                    render={<Link to="/entries/new"/>}
                    className="h-auto px-5 py-3"
                >
                    Start Writing
                </Button>
            </section>

            <section className="mt-12">
                <div className="flex items-center justify-between gap-4">
                    <h3 className="font-serif text-2xl text-ink">
                        Your journals
                    </h3>

                    <Link
                        to="/journals"
                        className="text-sm font-medium text-sage-dark hover:underline"
                    >
                        View all journals
                    </Link>
                </div>

                {loading ? (
                    <p className="mt-5 text-muted-foreground">
                        Loading journals...
                    </p>
                ) : error ? (
                    <p role="alert" className="mt-5 text-sm text-red-700">
                        Unable to load journals: {error}
                    </p>
                ) : activeJournals.length === 0 ? (
                    <div className="mt-5 rounded-xl border border-paper-border bg-paper p-6">
                        <p className="text-muted-foreground">
                            No journals yet. Create your first journal to get started.
                        </p>

                        <Link
                            to="/journals"
                            className="mt-3 inline-block text-sm font-medium text-sage-dark hover:underline">
                            Go to My Journals
                        </Link>
                    </div>
                ) : (
                    <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
                        {previewJournals.map((journal) => (
                            <Link
                                key={journal.id}
                                to={`/journals/${journal.id}/entries`}
                                className="block min-w-0"
                            >
                                <JournalCard
                                    title={journal.title}
                                    description={`${journal.type} journal`}
                                />
                            </Link>
                        ))}
                    </div>
                )}
            </section>

            <section className="mt-12" aria-label="Recent entries">
                <div className="flex items-center justify-between gap-4">
                    <h3 className="font-serif text-2xl text-ink">
                        Recent entries
                    </h3>

                    <Link
                        to="/entries"
                        className="text-sm font-medium text-sage-dark hover:underline"
                    >
                        View all entries
                    </Link>
                </div>

                {loading ? (
                    <p className="mt-5 text-muted-foreground">
                        Loading recent entries...
                    </p>
                ) : error ? (
                    <p role="alert" className="mt-5 text-sm text-red-700">
                        Unable to load recent entries: {error}
                    </p>
                ) : recentEntries.length === 0 ? (
                    <div className="mt-5 rounded-xl border border-paper-border bg-paper p-6">
                        <p className="text-muted-foreground">
                            {activeJournals.length === 0
                                ? "Create a journal to begin your writing journey."
                                : "No entries yet. Your writing will appear here."}
                        </p>

                        <Link
                            to={activeJournals.length === 0 ? "/journals" : "/entries/new"}
                            className="mt-3 inline-block text-sm font-medium text-sage-dark hover:underline"
                        >
                            {activeJournals.length === 0
                                ? "Create a journal"
                                : "Write your first entry"}
                        </Link>
                    </div>
                ) : (
                    <div className="mt-5 space-y-4">
                        {recentEntries.map((entry) => (
                            <EntryCard
                                key={entry.id}
                                id={entry.id}
                                title={entry.title}
                                entry={entry}
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
                                journalName={entry.journalName}
                            />
                        ))}
                    </div>
                )}
            </section>
        </div>);
}



















