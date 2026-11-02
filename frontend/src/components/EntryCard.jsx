import {Star} from "lucide-react";
import {Link} from "react-router";

export default function EntryCard({
                                      id,
                                      title,
                                      date,
                                      status,
                                      isFavorite,
                                  }) {
    return (
        <article className="rounded-xl border border-paper-border bg-paper p-5 md:p-6">
            <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                    <h3 className="font-serif text-xl text-ink">
                        <Link
                            to={`/entries/${id}`}
                            className="rounded-sm hover:text-sage-dark focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-sage"
                        >
                            {title}
                        </Link>
                    </h3>

                    <p className="mt-2 text-sm text-muted-foreground">
                        {date}
                    </p>
                </div>

                {isFavorite && (
                    <Star
                        size={19}
                        className="shrink-0 fill-sage text-sage"
                        aria-label="Favorite entry"
                    />
                )}
            </div>

            <div className="mt-4">
                <span
                    className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${
                        status?.toLowerCase() === "published"
                            ? "bg-sidebar-selected text-sage-dark"
                            : "bg-secondary text-muted-foreground"
                    }`}>
                    {status === "published" ? "Published" : status === "draft" ? "Draft" : status}
                </span>
            </div>
        </article>
    );
}
















