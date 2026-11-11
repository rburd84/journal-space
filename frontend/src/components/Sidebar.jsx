import {BookOpen, ChevronLeft, ChevronRight, FileText, House, Plus} from "lucide-react";
import {useState} from "react";
import {NavLink} from "react-router";

const navigationItems = [{label: "Home", icon: House}, {label: "My Journals", icon: BookOpen}, {
    label: "Entries", icon: FileText
},];

export default function Sidebar() {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <aside
            className={`flex min-h-screen shrink-0 flex-col border-r border-paper-border bg-sidebar p-4 transition-all duration-200 ${isExpanded ? "w-60" : "w-20 lg:w-60"}`}
            id="sidebar">
            <div className="mb-10 flex items-center justify-between">
                <h1 className={`font-serif text-2xl text-ink ${isExpanded ? "block" : "hidden lg:block"}`}>Stillspace</h1>

                <button
                    type="button"
                    onClick={() => setIsExpanded(!isExpanded)}
                    aria-label={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
                    aria-expanded={isExpanded}
                    className="flex h-11 w-11 items-center justify-center rounded-lg text-muted-foreground hover:bg-sidebar-selected lg:hidden"
                >
                    {isExpanded ? (<ChevronLeft size={20}/>) : (<ChevronRight size={20}/>)}</button>
            </div>

            <NavLink
                to="/"
                end
                className={({isActive}) => `flex items-center gap-3 rounded-lg px-3 py-3 transition-colors ${isActive ? "bg-sidebar-selected text-sage-dark" : "text-muted-foreground hover:bg-sidebar-selected/50"}`}
            >
                <House size={20} className="shrink-0"/>

                <span className={isExpanded ? "inline" : "hidden lg:inline"}>
                Home
            </span>

                {/*{!isExpanded && <span>Home</span>}*/}
            </NavLink>

            <NavLink
                to="/journals"
                className={({isActive}) => `flex items-center gap-3 rounded-lg px-3 py-3 transition-colors ${isActive ? "bg-sidebar-selected text-sage-dark" : "text-muted-foreground hover:bg-sidebar-selected/50"}`}
            >
                <BookOpen size={20} className="shrink-0"/>
                <span className={isExpanded ? "inline" : "hidden lg:inline"}>
                My Journals
            </span>
                {/*{!isExpanded && <span>My Journals</span>}*/}
            </NavLink>

            <NavLink
                to="/entries"
                end
                className={({isActive}) => `flex items-center gap-3 rounded-lg px-3 py-3 transition-colors ${isActive ? "bg-sidebar-selected text-sage-dark" : "text-muted-foreground hover:bg-sidebar-selected/50"}`}
            >
                <FileText size={20} className="shrink-0"/>
                <span className={isExpanded ? "inline" : "hidden lg:inline"}>
                Entries
            </span>
                {/*{!isExpanded && <span>Entries</span>}*/}
            </NavLink>

            <NavLink
                to="/entries/new"
                className={({isActive}) => `flex items-center gap-3 rounded-lg bg-sage-dark px-3 py-3 text-white transition-colors hover:opacity-90 ${isActive ? "ring-2 ring-sage ring-offset-2" : ""}`}
            >
                <Plus size={20} className="shrink-0"/>
                <span className={isExpanded ? "inline" : "hidden lg:inline"}>
                New Entry
            </span>
                {/*{!isExpanded && <span>New Entry</span>}*/}
            </NavLink>
        </aside>);
}





















