import {useEffect, useState} from "react";
import {getJournals} from "@/lib/api.js";
import {DEV_USER_ID} from "@/lib/devUser.js";
import {Link} from "react-router";
import CreateJournalDialog from "@/components/CreateJournalDialog.jsx";
import {BookOpen} from "lucide-react";

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

            {/*<Button className="h-auto min-h-11 px-5 py-3">*/}
            {/*    <Plus size={18} aria-hidden="true"/>*/}
            {/*    New Journal*/}
            {/*</Button>*/}
            <CreateJournalDialog onCreated={handleJournalCreated}/>
        </header>

        <section
            aria-label="Journal collection"
            className="mt-10 grid w-full grid-cols-1 gap-5 md:grid-cols-2">
            {journals.length === 0 ? (
                <p className="text-[#6B7168] md:col-span-2">
                    No journals yet. Create your first journal.
                </p>
            ) : (
                journals.map((journal) => (
                    <Link
                        key={journal.id}
                        to={`/journals/${journal.id}/entries`}
                        className="
                          block w-full min-w-0
                          rounded-2xl border border-[#E8E4D8]
                          bg-[#FDFBF4] p-6
                          transition-colors duration-200
                          hover:border-[#82947B]
                          hover:bg-[#F5F5EE]
                        "
                    >
                        <BookOpen
                            size={24}
                            className="mb-5 text-[#82947B]"
                            aria-hidden="true"
                        />

                        <h2 className="break-words font-serif text-2xl text-[#343A32]">
                            {journal.title}
                        </h2>

                        <p className="mt-2 text-sm capitalize text-[#6B7168]">
                            {journal.type} journal
                        </p>
                    </Link>

                )))}
        </section>
    </div>);
}

























