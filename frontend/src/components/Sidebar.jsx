import {BookOpen, ChevronLeft, ChevronRight, FileText, House, Plus} from "lucide-react";
import {Button} from "@/components/ui/button.jsx";
import {useState} from "react";

const navigationItems = [
    {label: "Home", icon: House},
    {label: "My Journals", icon: BookOpen},
    {label: "Entries", icon: FileText},
]

export default function Sidebar() {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <aside
            className={`flex min-h-screen shrink-0 flex-col border-r border-paper-border bg-sidebar p-4 transition-all duration-200 ${
                isExpanded ? "w-60" : "w-20 lg:w-60"
            }`}>
            <div className="mb-10 flex items-center justify-between">
                <h1 className={`font-serif text-2xl text-ink ${
                    isExpanded ? "block" : "hidden lg:block"
                }`}>Stillspace</h1>

                <button
                    type="button"
                    onClick={() => setIsExpanded(!isExpanded)}
                    aria-label={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
                    aria-expanded={isExpanded}
                    className="flex h-11 w-11 items-center justify-center rounded-lg text-muted-foreground hover:bg-sidebar-selected lg:hidden"
                >
                    {isExpanded ? (
                        <ChevronLeft size={20}/>
                    ) : (
                        <ChevronRight size={20}/>
                    )}</button>
            </div>


            <nav aria-label="Main navigation" className="space-y-2">
                {navigationItems.map(item => {
                    const Icon = item.icon
                    const isActive = item.label === "Home"

                    return (
                        <div
                            key={item.label}
                            title={item.label}
                            className={`flex min-h-11 items-center gap-3 rounded-lg px-3 py-3 ${
                                isActive
                                    ? "bg-sidebar-selected font-medium text-ink"
                                    : "text-muted-foreground"
                            }`}>
                            <Icon size={20} className="shrink-0" aria-hidden="true"/>

                            <span
                                className={
                                    isExpanded ? "block" : "hidden lg:block"
                                }>{item.label}</span>
                        </div>
                    )
                })}
            </nav>

            <div className="mt-auto pt-8">
                <Button
                    className={`h-auto min-h-11 ${
                        isExpanded ? "w-full" : "w-full lg:w-full"
                    }`}
                    title="New Entry"
                    aria-label="New Entry">
                    <Plus size={18} aria-hidden="true"/>
                    <span className={isExpanded ? "block" : "hidden lg:block"}>
                        New Entry
                    </span>
                </Button>
            </div>
        </aside>
    )
}





















