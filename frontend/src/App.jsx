import { Button } from "@/components/ui/button";
import AppShell from "@/components/AppShell.jsx";

function App() {
  return (
    <AppShell>
        <div>
            <p className="mb-3 text-sm font-medium uppercase tracking-wider text-sage-dark">
                Home
            </p>

            <h2 className="font-serif text-4xl text-ink">
                Welcome to Stillspace
            </h2>

            <p className="mt-4 text-muted-foreground">
                A quiet place for your thoughts.
            </p>


            <section className="mt-10 rounded-xl border border-paper-border bg-paper p-8">
                <h3 className="font-serif text-2xl text-ink">
                    Your writing space
                </h3>

                <p className="mt-3 text-muted-foreground">
                    A little room to pause and reflect.
                </p>
            </section>
        </div>
    </AppShell>
  )
}

export default App