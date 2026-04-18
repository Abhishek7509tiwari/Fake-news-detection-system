import { ShieldCheck, Home, ScanSearch, History as HistoryIcon, Info, Github } from "lucide-react";
import { cn } from "@/lib/utils";

export type ViewKey = "home" | "analyze" | "history" | "about";

interface Props {
  active: ViewKey;
  onChange: (v: ViewKey) => void;
  historyCount: number;
}

const items: { key: ViewKey; label: string; icon: typeof Home }[] = [
  { key: "home", label: "Overview", icon: Home },
  { key: "analyze", label: "Analyze", icon: ScanSearch },
  { key: "history", label: "History", icon: HistoryIcon },
  { key: "about", label: "About", icon: Info },
];

const Sidebar = ({ active, onChange, historyCount }: Props) => {
  return (
    <aside className="hidden lg:flex lg:w-64 lg:shrink-0 lg:flex-col lg:gap-6 lg:py-6 lg:pr-2">
      {/* Brand */}
      <div className="glass flex items-center gap-3 rounded-2xl px-4 py-4">
        <span className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-brand shadow-glow-brand">
          <ShieldCheck className="h-5 w-5 text-primary-foreground" />
        </span>
        <div className="leading-tight">
          <div className="font-display text-base font-bold">
            Truth<span className="text-gradient-brand">Seeker</span>
          </div>
          <div className="text-[11px] uppercase tracking-widest text-muted-foreground">AI Detector</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="glass flex flex-col gap-1 rounded-2xl p-2">
        {items.map(({ key, label, icon: Icon }) => {
          const isActive = active === key;
          return (
            <button
              key={key}
              onClick={() => onChange(key)}
              className={cn(
                "group flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all",
                isActive
                  ? "bg-gradient-brand text-primary-foreground shadow-glow-brand"
                  : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
              )}
            >
              <span className="flex items-center gap-3">
                <Icon className="h-4 w-4" />
                {label}
              </span>
              {key === "history" && historyCount > 0 && (
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-[10px] font-semibold",
                    isActive ? "bg-black/20 text-primary-foreground" : "bg-white/10 text-foreground"
                  )}
                >
                  {historyCount}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer card */}
      <div className="glass mt-auto rounded-2xl p-4 text-xs text-muted-foreground">
        <p className="mb-2 font-semibold text-foreground">Powered by Groq AI</p>
        <p className="leading-relaxed">
          Connects to your Flask backend at{" "}
          <code className="rounded bg-white/5 px-1.5 py-0.5 text-[11px] text-foreground">
            127.0.0.1:5000
          </code>
        </p>
        <a
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
          className="mt-3 inline-flex items-center gap-1.5 text-muted-foreground transition-colors hover:text-foreground"
        >
          <Github className="h-3.5 w-3.5" /> View source
        </a>
      </div>
    </aside>
  );
};

export default Sidebar;
