import {BookOpen} from "lucide-react";

export default function JournalCard({title, description}) {
    return (
        <article className="rounded-2xl border border-[#E8E4D8] bg-paper p-6">
            <BookOpen
                size={24}
                className="mb-5 text-sage"
                aria-hidden="true"
            />

            <h2 className="font-serif text-2xl text-ink">
                {title}
            </h2>

            <p className="mt-2 text-sm text-[#6B7168]">
                {description}
            </p>
        </article>
    );
}