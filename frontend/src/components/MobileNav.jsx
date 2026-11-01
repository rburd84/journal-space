import {BookOpen, FileText, House} from "lucide-react";

const navigationItems = [
    {label: "Home", icon: House},
    {label: "My Journals", icon: BookOpen},
    {label: "Entries", icon: FileText},
]

export default function MobileNav() {
    return (
        <nav
            aria-label="Mobile navigation"
            className="fixed inset-x-0 bottom-0 z-20 flex items-center justify-around border-t border-paper-border bg-sidebar px-2 pb-[env(safe-area-inset-bottom)] md:hidden"
        >
            {navigationItems.map(item => {
                const Icon = item.icon
                const isActive = item.label === "Home"

                return (
                    <div
                        key={item.label}
                        className={`flex min-h-16 flex-1 flex-col items-center justify-center gap-1 ${
                            isActive
                                ? "font-medium text-sage-dark"
                                : "text-muted-foreground"
                        }`}>
                        <Icon size={20} aria-hidden="true"/>
                        <span className="text-xs">{item.label}</span>
                    </div>
                )
            })}
        </nav>
    )
}





















