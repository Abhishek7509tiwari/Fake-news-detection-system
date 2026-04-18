import { CheckCircle2, AlertTriangle, FileText, Link2, Trash2, Inbox } from "lucide-react";
import { Button } from "@/components/ui/button";
import { clearHistory, type HistoryEntry } from "@/lib/api";
import { toast } from "sonner";

interface Props {
  history: HistoryEntry[];
  onCleared: () => void;
}

const formatTime = (ts: number) => {
  const d = new Date(ts);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const HistoryPanel = ({ history, onCleared }: Props) => {
  const handleClear = () => {
    clearHistory();
    onCleared();
    toast.success("History cleared");
  };

  if (history.length === 0) {
    return (
      <div className="glass flex flex-col items-center justify-center rounded-3xl px-6 py-16 text-center">
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5">
          <Inbox className="h-7 w-7 text-muted-foreground" />
        </div>
        <h3 className="font-display text-lg font-semibold">No analyses yet</h3>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          Run your first analysis from the Analyze tab — your last 20 results will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-xl font-bold">Recent analyses</h2>
          <p className="text-sm text-muted-foreground">Last {history.length} results stored locally on this device.</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleClear} className="gap-2">
          <Trash2 className="h-4 w-4" /> Clear
        </Button>
      </div>

      <div className="grid gap-3">
        {history.map((entry) => {
          const verdict = (entry.result.result || "").toUpperCase();
          const isReal = verdict === "REAL";
          const isFake = verdict === "FAKE";
          const Icon = entry.mode === "url" ? Link2 : FileText;
          const VerdictIcon = isReal ? CheckCircle2 : AlertTriangle;

          const tone = isReal
            ? "text-real bg-real/10 border-real/30"
            : isFake
            ? "text-fake bg-fake/10 border-fake/30"
            : "text-foreground bg-white/5 border-white/10";

          return (
            <div
              key={entry.id}
              className="glass rounded-2xl p-4 transition-all hover:border-white/15 sm:p-5"
            >
              <div className="flex items-start gap-4">
                <span
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border ${tone}`}
                >
                  <VerdictIcon className="h-5 w-5" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`text-sm font-semibold ${isReal ? "text-real" : isFake ? "text-fake" : ""}`}>
                      {verdict || "UNKNOWN"}
                    </span>
                    <span className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] uppercase tracking-wider text-muted-foreground">
                      <Icon className="h-3 w-3" />
                      {entry.mode}
                    </span>
                    <span className="text-[11px] text-muted-foreground">{formatTime(entry.createdAt)}</span>
                  </div>
                  <p className="mt-1.5 line-clamp-2 break-words text-sm text-muted-foreground">
                    {entry.result.original_title || entry.input}
                  </p>
                  {entry.result.reasoning && (
                    <p className="mt-2 line-clamp-2 text-xs text-muted-foreground/80">
                      {entry.result.reasoning}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HistoryPanel;
