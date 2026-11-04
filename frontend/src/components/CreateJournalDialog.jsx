import {useState} from "react";
import {createJournal} from "@/lib/api";
import {DEV_USER_ID} from "@/lib/devUser.js";
import {Button} from "@/components/ui/button.jsx";
import {Plus} from "lucide-react";

const JOURNAL_TYPES = [
    {value: "personal", label: "Personal"},
    {value: "gratitude", label: "Gratitude"},
    {value: "dream", label: "Dream"},
    {value: "reflection", label: "Reflection"},
    {value: "productivity", label: "Productivity"},
    {value: "custom", label: "Custom"},
];

export default function CreateJournalDialog({onCreated}) {
    const [open, setOpen] = useState(false);
    const [title, setTitle] = useState("");
    const [type, setType] = useState("personal");
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(event) {
        event.preventDefault();

        if (!title.trim() || saving) return;

        setSaving(true);
        setError("");

        try {
            const journal = await createJournal({
                userId: DEV_USER_ID,
                title: title.trim(),
                type,
            });

            onCreated(journal);

            setTitle("");
            setType("personal");
            setOpen(false);
        } catch (error) {
            setError(error.message);
        } finally {
            setSaving(false);
        }
    }

    return (
        <>
            <Button
                onClick={() => setOpen(true)}
                className="min-h-11 px-5"
            >
                <Plus size={18} aria-hidden="true"/>
                New Journal
            </Button>

            {open && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
                    <div
                        role="dialog"
                        aria-hidden="true"
                        aria-labelledby="create-journal-title"
                        className="w-full max-w-md rounded-2xl bg-[#FDFBF4] p-6 shadow-xl sm:p-8"
                    >
                        <h2
                            id="create-journal-title"
                            className="font-serif text-2xl text-[#343A32]"
                        >Create a Journal</h2>

                        <p className="mt-2 text-sm text-[#6B7168]">
                            Give your thoughts a space of their own.
                        </p>

                        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
                            <div className="space-y-2">
                                <label
                                    htmlFor="journal-title"
                                    className="block text-sm font-medium text-[#343A32]"
                                >Journal name
                                </label>

                                <input
                                    id="journal-title"
                                    type="text"
                                    value={title}
                                    onChange={(event) => setTitle(event.target.value)}
                                    maxLength={200}
                                    required
                                    autoFocus
                                    placeholder="e.g. Daily Reflections"
                                    className="w-full rounded-lg border border-[#DADDD4] bg-white px-4 py-3 text-[#343A32] outline-none focus:border-[#82947B]"
                                />
                            </div>

                            <div className="space-y-2">
                                <label
                                    htmlFor="journal-type"
                                    className="block text-sm font-medium text-[#343A32]"
                                >
                                    Journal type
                                </label>

                                <select
                                    id="journal-type"
                                    value={type}
                                    onChange={(event) => setType(event.target.value)}
                                    className="w-full rounded-lg border border-[#DADDD4] bg-white px-4 py-3 text-[#343A32] outline-none focus:border-[#82947B]"
                                >
                                    {JOURNAL_TYPES.map((option) => (
                                        <option key={option.value} value={option.value}>
                                            {option.label}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {error && (
                                <p role="alert" className="text-sm text-red-700">
                                    {error}
                                </p>
                            )}

                            <div className="flex justify-end gap-3 pt-2">
                                <Button
                                    type="button"
                                    variant="outline"
                                    disabled={saving}
                                    onClick={() => setOpen(false)}
                                >
                                    Cancel
                                </Button>

                                <Button
                                    type="submit"
                                    disabled={saving || !title.trim()}
                                >
                                    {saving ? "Creating..." : "Create Journal"}
                                </Button>
                            </div>

                        </form>
                    </div>
                </div>
            )}
        </>
    );
}





















