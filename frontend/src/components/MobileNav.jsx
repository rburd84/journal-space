import {BookOpen, FileText, House} from "lucide-react";
import {NavLink} from "react-router";

const navigationItems = [
    {label: "Home", path: "/", icon: House, end: true,},
    {label: "My Journals", path: "/journals", icon: BookOpen},
    {label: "Entries", path: "/entries", icon: FileText, end: true,},
]

export default function MobileNav() {
    return (<nav
            aria-label="Mobile navigation"
            className="fixed inset-x-0 bottom-0 z-50 border-t border-paper-border bg-sidebar pb-[env(safe-area-inset-bottom)] md:hidden"
        >
            <div className="flex items-center justify-around">
                {navigationItems.map((item) => {
                    const Icon = item.icon

                    return (<NavLink
                            key={item.path}
                            to={item.path}
                            end={item.end}
                            className={({isActive}) => `flex min-h-16 flex-1 flex-col items-center justify-center gap-1 text-xs transition-colors ${isActive ? "text-sage-dark" : "text-muted-foreground"}`}
                        >
                            <Icon size={20} aria-hidden="true"/>
                            <span>{item.label}</span>
                        </NavLink>)
                })}
            </div>
        </nav>)
}





















