import {Star} from "lucide-react";
import {Button} from "@/components/ui/button";

export default function Reader() {
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

                <span className="rounded-full bg-sidebar-selected px-3 py-1 text-xs font-medium text-sage-dark">
                    Published
                </span>
            </header>

            <article className="rounded-xl border border-paper-border bg-paper px-5 py-8 sm:px-8 md:px-12 md:py-12">
                <h1 className="font-serif text-[30px] leading-tight text-ink md:text-4xl">
                    A quiet moment
                </h1>

                <div className="my-8 h-px bg-paper-border" />

                <div className="space-y-6 font-serif text-[17px] leading-[1.8] text-ink md:text-lg">
                    <p>
                        Today I found a little space to slow down and reflect.
                    </p>

                    <p>
                        There was something comforting about the quiet.
                        Nothing needed to be accomplished, and there was
                        nowhere else I needed to be.
                    </p>

                    <p>
                        Sometimes the smallest moments are the ones
                        worth remembering.
                    </p>
                </div>
            </article>

            <footer className="mt-6 flex flex-wrap items-center justify-between gap-4">
                <Button variant="outline" className="h-auto min-h-11 px-4 py-3">
                    <Star size={18} className="fill-sage text-sage" aria-hidden="true" />
                    Favorited
                </Button>

                <Button className="h-auto min-h-11 px-5 py-3">
                    Edit Entry
                </Button>
            </footer>
        </div>
    )
}




















