import AppShell from "@/components/AppShell";
import Home from "@/pages/Home";
import Journals from "@/pages/Journals.jsx";
import Entries from "@/pages/Entries.jsx";
import Editor from "@/pages/Editor.jsx";
import Reader from "@/pages/Reader.jsx";

function App() {
  return (
    <AppShell>
        <Reader />
    </AppShell>
  )
}

export default App