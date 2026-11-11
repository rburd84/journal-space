import { UserButton } from "@clerk/clerk-react";
import Sidebar from "./Sidebar";
import MobileHeader from "./MobileHeader";
import MobileNav from "./MobileNav";

export default function AppShell({ children }) {
  return (
    <div className="min-h-screen bg-canvas md:flex">
      <div className="hidden md:block"><Sidebar /></div>
      <MobileHeader />
      <main className="min-w-0 flex-1 px-5 pb-24 pt-8 md:px-8 md:pb-12 lg:px-12">
        <div className="mx-auto max-w-4xl">
          <div className="mb-5 flex justify-end" aria-label="Account controls">
            <UserButton />
          </div>
          {children}
        </div>
      </main>
      <MobileNav />
    </div>
  );
}
