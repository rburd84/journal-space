import {Archive, BookOpen, Ellipsis, Pencil, RotateCcw} from "lucide-react";
import {useState} from "react";

import {Button} from "@/components/ui/button.jsx";
import {Link} from "react-router";

export default function ManageJournalCard({
                                              journal,
                                              onRename,
                                              onArchive,
                                              onRestore,
                                          }) {
    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <article
            className="
                relative min-w-0 rounded-2xl border border-[#E8E4D8]
              bg-paper p-6
             "
        >
            <div className="absolute right-4 top-4 z-10">
                <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Manage ${journal.title}`}
                    onClick={() => setMenuOpen((current) => !current)}
                >
                    <Ellipsis size={20}/>
                </Button>

                {menuOpen && (
                    <div
                        className="absolute right-0 top-full z-20 mt-1 min-w-40 rounded-xl border border-[#E8E4D8] bg-paper p-1 shadow-lg">
                        <button
                            type="button"
                            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-[#E9EDE5]"
                            onClick={() => {
                                setMenuOpen(false);
                                onRename(journal);
                            }}
                        >
                            <Pencil size={16}/>
                            Rename
                        </button>

                        {journal.is_archived ? (
                            <button
                                type="button"
                                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-[#E9EDE5]"
                                onClick={() => {
                                    setMenuOpen(false);
                                    onRestore(journal);
                                }}
                            >
                                <RotateCcw size={16}/>
                                Restore
                            </button>
                        ) : (
                            <button
                                type="button"
                                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-[#E9EDE5]"
                                onClick={() => {
                                    setMenuOpen(false);
                                    onArchive(journal);
                                }}
                            >
                                <Archive size={16}/>
                                Archive
                            </button>
                        )}
                    </div>
                )}
            </div>

            <Link
                to={`/journals/${journal.id}/entries`}
                className="block min-w-0 pr-10"
            >
                <BookOpen
                    size={24}
                    className="mb-5 text-sage"
                    aria-hidden="true"/>

                <h2 className="break-words font-serif text-2xl text-ink">
                    {journal.title}
                </h2>

                <p className="mt-2 text-sm capitalize text-[#6B7168]">
                    {journal.type} journal
                </p>
            </Link>
        </article>
    );
}
