import {BrowserRouter, Route, Routes} from "react-router";
import AppShell from "@/components/AppShell";
import Home from "@/pages/Home";
import Journals from "@/pages/Journals.jsx";
import Entries from "@/pages/Entries.jsx";
import Editor from "@/pages/Editor.jsx";
import Reader from "@/pages/Reader.jsx";

function App() {
    return (
        <BrowserRouter>
            <AppShell>
                <Routes>
                    <Route path="/" element={<Home/>}/>
                    <Route path="/journals" element={<Journals/>}/>
                    <Route path="/entries" element={<Entries/>}/>
                    <Route path="/entries/new" element={<Editor/>}/>
                    <Route path="/entries/:entryId/edit" element={<Editor/>}/>
                    <Route path="/journals/:journalId/entries/new" element={<Editor/>}/>
                    <Route path="/entries/:entryId" element={<Reader/>}/>
                </Routes>
            </AppShell>
        </BrowserRouter>
    );
}

export default App;