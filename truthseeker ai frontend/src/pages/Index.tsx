import { useEffect, useMemo, useState } from "react";
import Sidebar, { type ViewKey } from "@/components/Sidebar";
import MobileNav from "@/components/MobileNav";
import HomeView from "@/components/HomeView";
import Analyzer from "@/components/Analyzer";
import HistoryPanel from "@/components/HistoryPanel";
import AboutView from "@/components/AboutView";
import ApiKeyBanner from "@/components/ApiKeyBanner";
import SettingsView from "@/components/SettingsView";
import { checkHealth, loadHistory, type HistoryEntry } from "@/lib/api";

const Index = () => {
  const [view, setView] = useState<ViewKey>("home");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [needsKey, setNeedsKey] = useState(false);
  const [backendDown, setBackendDown] = useState(false);

  useEffect(() => {
    setHistory(loadHistory());

    // Check backend health on mount
    checkHealth()
      .then((h) => {
        setBackendDown(false);
        setNeedsKey(!h.api_key_configured);
      })
      .catch(() => {
        setBackendDown(true);
      });
  }, []);

  const headerTitle = useMemo(() => {
    switch (view) {
      case "home":
        return "Overview";
      case "analyze":
        return "Analyze";
      case "history":
        return "History";
      case "about":
        return "About";
      case "settings":
        return "Settings";
    }
  }, [view]);

  return (
    <div className="min-h-screen">
      <MobileNav active={view} onChange={setView} />

      <div className="container mx-auto flex gap-6 px-4 lg:px-6">
        <Sidebar active={view} onChange={setView} historyCount={history.length} />

        <main className="flex-1 py-6 lg:py-8">
          {/* Page header (desktop) */}
          <div className="mb-6 hidden items-end justify-between lg:flex">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">TruthSeeker AI</p>
              <h1 className="font-display text-3xl font-bold">{headerTitle}</h1>
            </div>
            <div className="text-right text-xs text-muted-foreground">
              <p>
                Backend: <code className="rounded bg-white/5 px-1.5 py-0.5 text-foreground">127.0.0.1:5000</code>
              </p>
            </div>
          </div>

          {/* Backend down warning */}
          {backendDown && (
            <div className="glass mb-6 rounded-2xl border border-fake/30 p-5 flex items-center gap-3 animate-fade-in">
              <span className="text-fake text-lg">⚠</span>
              <div>
                <p className="text-sm font-semibold text-fake">Backend Unreachable</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Flask server at <code>127.0.0.1:5000</code> is not responding. Start it with <code>backend\scripts\run_flask.bat</code>
                </p>
              </div>
            </div>
          )}

          {/* API key banner */}
          {!backendDown && needsKey && (
            <div className="mb-6">
              <ApiKeyBanner onConfigured={() => setNeedsKey(false)} />
            </div>
          )}

          <div key={view} className="animate-fade-in">
            {view === "home" && <HomeView history={history} onStart={() => setView("analyze")} />}
            {view === "analyze" && <Analyzer onAnalyzed={setHistory} />}
            {view === "history" && <HistoryPanel history={history} onCleared={() => setHistory([])} />}
            {view === "about" && <AboutView />}
            {view === "settings" && <SettingsView />}
          </div>

          <footer className="mt-12 border-t border-white/5 pt-6 text-center text-xs text-muted-foreground">
            <span className="text-gradient-brand font-semibold">TruthSeeker</span> — clarity in a noisy world. Powered by Groq AI.
          </footer>
        </main>
      </div>
    </div>
  );
};

export default Index;
