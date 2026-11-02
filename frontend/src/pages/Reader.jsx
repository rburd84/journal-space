import {Star} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Link, useParams} from "react-router";


const sampleEntries = [
    {
        id: "entry-1",
        title: "Finding calm in the everyday",
        date: "October 30, 2026",
        status: "Published",
        isFavorite: true,
        content: [
            "Today I found a little space to slow down and reflect.",
            "There was something comforting about the quiet. Nothing needed to be accomplished, and there was nowhere else I needed to be.",
            "Sometimes the smallest moments are the ones worth remembering.",
        ],
    },
    {
        id: "entry-2",
        title: "A few thoughts from this morning",
        date: "October 28, 2026",
        status: "Draft",
        isFavorite: false,
        content: [
            "The morning started slowly, with a warm cup of tea and a few moments of silence.",
            "I want to make more room for mornings like this.",
        ],
    },
    {
        id: "entry-3",
        title: "The little things that matter",
        date: "October 25, 2026",
        status: "Published",
        isFavorite: false,
        content: [
            "Today reminded me that meaningful moments don't have to be extraordinary.",
            "A kind word, a familiar smile, and a little time outdoors were enough.",
        ],
    },
    {
        id: "entry-4",
        title: "An unfinished thought",
        date: "October 22, 2026",
        status: "Draft",
        isFavorite: true,
        content: [
            "There is something I've been meaning to write about, but I haven't quite found the words yet.",
        ],
    },
];

export default function Reader() {
    const {entryId} = useParams();

    const entry = sampleEntries.find(
        (item) => item.id === entryId
    );

    if (!entry) {
        return (
            <p className="text-muted-foreground">
                Entry not found.
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
                        {entry.date}
                    </p>
                </div>

                <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${
                        entry.status === "Published"
                            ? "bg-sidebar-selected text-sage-dark"
                            : "bg-secondary text-muted-foreground"
                    }`}
                >
                    {entry.status}
                </span>
            </header>

            <article className="rounded-xl border border-paper-border bg-paper px-5 py-8 sm:px-8 md:px-12 md:py-12">
                <h1 className="font-serif text-[30px] leading-tight text-ink md:text-4xl">
                    {entry.title}
                </h1>

                <div className="my-8 h-px bg-paper-border"/>

                <div className="space-y-6 font-serif text-[17px] leading-[1.8] text-ink md:text-lg">
                    {entry.content.map((paragraph, index) => (
                        <p key={index}>{paragraph}</p>
                    ))}
                </div>
            </article>

            <footer className="mt-6 flex flex-wrap items-center justify-between gap-4">
                <Button
                    variant="outline"
                    className="h-auto min-h-11 px-4 py-3"
                >
                    <Star
                        size={18}
                        className={entry.isFavorite ? "fill-sage text-sage" : ""}
                        aria-hidden="true"
                    />
                    {entry.isFavorite ? "Favorited" : "Favorite"}
                </Button>

                <Button
                    nativeButton={false}
                    render={<Link to="/entries/new"/>}
                    className="h-auto min-h-11 px-5 py-3"
                >
                    Edit Entry
                </Button>
            </footer>
        </div>
    );
}




















