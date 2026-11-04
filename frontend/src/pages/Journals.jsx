import {Plus} from "lucide-react";
import {Button} from "@/components/ui/button";
import {useEffect, useState} from "react";
import {getJournals} from "@/lib/api.js";
import {DEV_USER_ID} from "@/lib/devUser.js";
import {Link} from "react-router";

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

    if (loading) return <p>Loading journals...</p>;
    if (error) return <p role="alert">{error}</p>;

    return (<div>
        <header className="flex flex-wrap items-start justify-between gap-4">
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

            <Button className="h-auto min-h-11 px-5 py-3">
                <Plus size={18} aria-hidden="true"/>
                New Journal
            </Button>
        </header>

        <section
            aria-label="Journal collection"
            className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {journals.length === 0 ? (
                <p>No journals yet. Create your first journal.</p>
            ) : (
                <div>
                    {journals.map((journal) => (
                        <Link
                            key={journal.id}
                            to={`/journals/${journal.id}/entries`}
                        >
                            {journal.title}
                        </Link>
                    ))}
                </div>
            )}
            {/*{sampleJournals.map((journal) => (<JournalCard*/}
            {/*    key={journal.id}*/}
            {/*    title={journal.title}*/}
            {/*    description={journal.description}*/}
            {/*/>))}*/}
        </section>
    </div>);
}

























