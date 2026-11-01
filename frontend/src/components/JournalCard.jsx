import {BookOpen} from "lucide-react";
import {Component} from "react";

export default function JournalCard({title, description}) {
    return (
        <article className="rounded-xl border border-paper-border bg-paper p-5">
            <BookOpen size={22} className="mb-4 text-sage" aria-hidden="true" />

            <h3 className="font-serif text-xl text-ink">{title}</h3>

            <p className="mt-2 text-sm text-muted-foreground">{description}</p>
        </article>
    )
}