import {PenLine} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Link} from "react-router";
import JournalCard from "@/components/JournalCard.jsx";

const sampleJournals = [{
    id: "journal-1", title: "Daily Reflections", description: "Personal journal",
}, {
    id: "journal-2", title: "Small Moments", description: "Personal journal",
},];

export default function Home() {
    return (<div>
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
            <h3 className="font-serif text-2xl text-ink">
                Your journals
            </h3>

            <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
                {sampleJournals.map((journal) => (<JournalCard
                    key={journal.id}
                    title={journal.title}
                    description={journal.description}
                />))}
            </div>
        </section>
    </div>);
}

























