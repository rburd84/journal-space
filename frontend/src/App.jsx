import {useCallback, useEffect, useState} from "react";
import {BrowserRouter, Route, Routes} from "react-router";
import {SignedIn, SignedOut, SignIn, useAuth} from "@clerk/clerk-react";
import {setAuthTokenGetter} from "@/lib/api.js";
import AppShell from "@/components/AppShell";
import Home from "@/pages/Home";
import Journals from "@/pages/Journals.jsx";
import Entries from "@/pages/Entries.jsx";
import Editor from "@/pages/Editor.jsx";
import Reader from "@/pages/Reader.jsx";

function AuthenticatedRoutes() {
    const {getToken, userId, isLoaded, isSignedIn} = useAuth();
    const [status, setStatus] = useState("loading");
    const [attempt, setAttempt] = useState(0);
    const retry = useCallback(() => setAttempt((value) => value + 1), []);

    useEffect(() => {
        let cancelled = false;
        setAuthTokenGetter(null);
        setStatus("loading");

        if (!isLoaded || !isSignedIn || !userId) return () => {
            cancelled = true;
        };

        async function prepare() {
            try {
                // Do not mount API-consuming pages until Clerk can actually supply a token.
                const token = await getToken();
                if (cancelled) return;
                if (!token) {
                    setStatus("unavailable");
                    return;
                }
                setAuthTokenGetter(getToken);
                setStatus("ready");
            } catch {
                if (!cancelled) setStatus("unavailable");
            }
        }

        void prepare();
        return () => {
            cancelled = true;
            setAuthTokenGetter(null);
        };
    }, [getToken, userId, isLoaded, isSignedIn, attempt]);

    if (status === "loading") return <p className="p-8">Preparing your private space...</p>;
    if (status === "unavailable") return (
        <div className="p-8">
            <p>Your session is still becoming available. Please try again.</p>
            <button type="button" onClick={retry}>Retry connection</button>
        </div>
    );

    return (
        <AppShell>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/journals" element={<Journals/>}/>
                <Route path="/entries" element={<Entries/>}/>
                <Route path="/journals/:journalId/entries" element={<Entries/>}/>
                <Route path="/entries/new" element={<Editor/>}/>
                <Route path="/entries/:entryId/edit" element={<Editor/>}/>
                <Route path="/journals/:journalId/entries/new" element={<Editor/>}/>
                <Route path="/entries/:entryId" element={<Reader/>}/>
            </Routes>
        </AppShell>
    );
}

export default function App() {
    return (
        <BrowserRouter>
            <SignedOut>
                <main className="flex min-h-screen items-center justify-center bg-canvas p-6">
                    <div className="w-full max-w-md">
                        <h1 className="mb-6 text-center font-serif text-3xl text-ink">Stillspace</h1>
                        <SignIn routing="hash"/>
                    </div>
                </main>
            </SignedOut>
            <SignedIn><AuthenticatedRoutes/></SignedIn>
        </BrowserRouter>
    );
}
