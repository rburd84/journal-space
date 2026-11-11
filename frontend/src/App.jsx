import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router";
import { SignedIn, SignedOut, SignIn, useAuth } from "@clerk/clerk-react";
import { setAuthTokenGetter } from "@/lib/api.js";
import AppShell from "@/components/AppShell";
import Home from "@/pages/Home";
import Journals from "@/pages/Journals.jsx";
import Entries from "@/pages/Entries.jsx";
import Editor from "@/pages/Editor.jsx";
import Reader from "@/pages/Reader.jsx";

function AuthenticatedRoutes() {
  const { getToken, userId } = useAuth();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(false);
    // Never mount API-consuming pages before their token provider is installed.
    setAuthTokenGetter(getToken);
    setReady(true);
    return () => {
      setAuthTokenGetter(null);
    };
  }, [getToken, userId]);

  if (!ready) return <p className="p-8">Preparing your private space...</p>;

  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/journals" element={<Journals />} />
        <Route path="/entries" element={<Entries />} />
        <Route path="/journals/:journalId/entries" element={<Entries />} />
        <Route path="/entries/new" element={<Editor />} />
        <Route path="/entries/:entryId/edit" element={<Editor />} />
        <Route path="/journals/:journalId/entries/new" element={<Editor />} />
        <Route path="/entries/:entryId" element={<Reader />} />
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
            <SignIn routing="hash" />
          </div>
        </main>
      </SignedOut>
      <SignedIn>
        <AuthenticatedRoutes />
      </SignedIn>
    </BrowserRouter>
  );
}
