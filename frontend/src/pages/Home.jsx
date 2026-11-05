import {useEffect, useState} from 'react';
import {PenLine} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Link} from "react-router";
import JournalCard from "@/components/JournalCard.jsx";

import {getJournals} from "@/lib/api.js";
import {DEV_USER_ID} from "@/lib/devUser.js";


export default function Home() {
    const [journals, setJournals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {
        let cancelled = false;

        async function loadJournals() {
            try {
                const data = await getJournals(DEV_USER_ID);

                if (!cancelled) {
                    setJournals(data);
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
        .filter(journal => !journal.is_archived)
        .slice(0, 3);

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
                        {activeJournals.map((journal) => (
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
        </div>);
}