import Sidebar from "./Sidebar"

export default function AppShell({ children }) {
    return (
        <div className="flex min-h-screen bg-canvas">
            <Sidebar />

            <main className="min-w-0 flex-1 p-8 lg:p-12">
                <div className="mx-auto max-w-4xl">
                    {children}
                </div>
            </main>
        </div>
    )
}