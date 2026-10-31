import { Button } from "@/components/ui/button";

function App() {
  return (
    <main className="min-h-screen bg-canvas p-6 md:p-12">
        <div className="mx-auto max-w-3xl">
            <h1 className="text-4xl font-serif text-ink">
                Stillspace
            </h1>

            <p className="mt-3 text-muted">
                A quiet place for your thoughts.
            </p>


            <section className="mt-10 rounded-xl border border-paper-border bg-paper p-8">
                <p className="text-sm font-medium text-sage-dark">
                    My Journal
                </p>

                <h2 className="mt-4 font-serif text-lg leading-8 text-ink">
                    A moment to reflect
                </h2>

                <p className="mt-4 font-serif text-lg leading-8 text-ink">
                    Every thought deserves a little space.
                </p>

                <div className="mt-8">
                    <Button className="h-auto px-5 py-3">Start Writing</Button>
                </div>
            </section>
        </div>
    </main>
  )
}

export default App