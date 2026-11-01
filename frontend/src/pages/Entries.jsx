import {Plus} from "lucide-react"

import EntryCard from "@/components/EntryCard"
import {Button} from "@/components/ui/button"

const sampleEntries = [
    {
        id: "entry-1",
        title: "Finding calm in the everyday",
        date: "October 30, 2026",
        status: "Published",
        isFavorite: true,
    },
    {
        id: "entry-2",
        title: "A few thoughts from this morning",
        date: "October 28, 2026",
        status: "Draft",
        isFavorite: false,
    },
    {
        id: "entry-3",
        title: "The little things that matter",
        date: "October 25, 2026",
        status: "Published",
        isFavorite: false,
    },
    {
        id: "entry-4",
        title: "An unfinished thought",
        date: "October 22, 2026",
        status: "Draft",
        isFavorite: true,
    },
]

export default function Entries() {
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

                <Button className="h-auto min-h-11 px-5 py-3">
                    <Plus size={18} aria-hidden="true"/>
                    New Entry
                </Button>
            </header>

            <section
                aria-label="Journal entries"
                className="mt-10 space-y-4"
            >
                {sampleEntries.map((entry) => (
                    <EntryCard
                        key={entry.id}
                        title={entry.title}
                        date={entry.date}
                        status={entry.status}
                        isFavorite={entry.isFavorite}
                    />
                ))}
            </section>
        </div>
    )
}