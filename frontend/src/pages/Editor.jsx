import {useState} from "react";
import {Star} from "lucide-react";
import {Button} from "@/components/ui/button";

export default function Editor() {
    const [title, setTitle] = useState("A quiet moment");
    const [content, setContent] = useState(
        "Today I found a little space to slow down and reflect."
    );

    return (
        <div className="mx-auto max-w-[760px]">
            <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
                <div>
                    <p className="text-sm font-medium text-sage-dark">
                        Daily Reflections
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                        October 31, 2026
                    </p>
                </div>

                <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-muted-foreground">
                    Draft
                </span>
            </header>

            <section
                aria-label="Journal editor"
                className="rounded-xl border border-paper-border bg-paper px-5 py-8 sm:px-8 md:px-12 md:py-12"
            >
                <label htmlFor="entry-title" className="sr-only">
                    Entry title
                </label>

                <input
                    id="entry-title"
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Untitled entry"
                    className="w-full border-0 bg-transparent font-serif text-[30px] leading-tight text-ink outline-none placeholder:text-muted-foreground md:text-4xl"
                />

                <div className="my-8 h-px bg-paper-border" />

                <label htmlFor="entry-content" className="sr-only">
                    Entry content
                </label>

                <textarea
                    id="entry-content"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Begin writing..."
                    rows={12}
                    className="w-full resize-y border-0 bg-transparent font-serif text-[17px] leading-[1.8] text-ink outline-none placeholder:text-muted-foreground md:text-lg"
                />
            </section>

            <footer className="mt-6 flex flex-wrap items-center justify-between gap-4">
                <Button variant="outline" className="h-auto min-h-11 px-4 py-3">
                    <Star size={18} aria-hidden="true" />
                    Favorite
                </Button>

                <div className="flex flex-wrap gap-3">
                    <Button variant="outline" className="h-auto min-h-11 px-5 py-3">
                        Save Draft
                    </Button>

                    <Button className="h-auto min-h-11 px-5 py-3">
                        Publish
                    </Button>
                </div>
            </footer>
        </div>
    )
}




















