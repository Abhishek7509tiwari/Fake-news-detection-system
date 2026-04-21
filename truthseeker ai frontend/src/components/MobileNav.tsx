import { Menu, ShieldCheck, ScanSearch, Home, History as HistoryIcon, Info, Settings } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { ViewKey } from "./Sidebar";
import { useState } from "react";

interface Props {
  active: ViewKey;
  onChange: (v: ViewKey) => void;
}

const items: { key: ViewKey; label: string; icon: typeof Home }[] = [
  { key: "home", label: "Overview", icon: Home },
  { key: "analyze", label: "Analyze", icon: ScanSearch },
  { key: "history", label: "History", icon: HistoryIcon },
  { key: "about", label: "About", icon: Info },
  { key: "settings", label: "Settings", icon: Settings },
];

const MobileNav = ({ active, onChange }: Props) => {
  const [open, setOpen] = useState(false);

  const handle = (k: ViewKey) => {
    onChange(k);
    setOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 lg:hidden">
      <div className="glass border-b border-white/5">
        <div className="flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-brand shadow-glow-brand">
              <ShieldCheck className="h-4 w-4 text-primary-foreground" />
            </span>
            <span className="font-display text-base font-bold">
              Truth<span className="text-gradient-brand">Seeker</span>
            </span>
          </div>
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Open menu">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-72 border-white/10 bg-background/95 backdrop-blur-xl">
              <div className="mt-6 flex flex-col gap-1.5">
                {items.map(({ key, label, icon: Icon }) => {
                  const isActive = active === key;
                  return (
                    <button
                      key={key}
                      onClick={() => handle(key)}
                      className={cn(
                        "flex items-center gap-3 rounded-xl px-3.5 py-3 text-sm font-medium transition-all",
                        isActive
                          ? "bg-gradient-brand text-primary-foreground shadow-glow-brand"
                          : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {label}
                    </button>
                  );
                })}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
};

export default MobileNav;
