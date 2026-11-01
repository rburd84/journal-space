import {BookOpen, FileText, House, Plus} from "lucide-react";
import {Button} from "@/components/ui/button.jsx";

const navigationItems = [
    {label: "Home", icon: House},
    {label: "My Journals", icon: BookOpen},
    {label: "Entries", icon: FileText},
]

export default function Sidebar() {
    return (
        <aside className="flex min-h-screen w-60 shrink-0 flex-col border-r border-paper-border bg-sidebar p-5">
            <h1 className="mb-12 font-serif text-2xl text-ink">Stillspace</h1>

            <nav aria-label="Main navigation" className="space-y-2">
                {navigationItems.map(item => {
                    const Icon = item.icon
                    const isActive = item.label === "Home"

                    return (
                        <div
                            key={item.label}
                            className={`flex items-center gap-3 rounded-lg px-4 py-3 ${
                                isActive
                                    ? "bg-sidebar-selected font-medium text-ink"
                                    : "text-muted-foreground"
                            }`}>
                            <Icon size={19} aria-hidden="true"/>
                            <span>{item.label}</span>
                        </div>
                    )
                })}
            </nav>

            <div className="mt-auto pt-8">
                <Button className="h-auto w-full py-3">
                    <Plus size={18} aria-hidden="true"/>
                    New Entry
                </Button>
            </div>
        </aside>
    )
}





















