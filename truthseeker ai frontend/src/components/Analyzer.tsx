import { useState } from "react";
import { toast } from "sonner";
import { FileText, Link2, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  analyzeContent,
  BackendUnreachableError,
  saveHistoryEntry,
  type AnalyzeMode,
  type AnalyzeResponse,
  type HistoryEntry,
} from "@/lib/api";
import RadarLoader from "./RadarLoader";
import ResultsDashboard from "./ResultsDashboard";

const isLikelyUrl = (v: string) => {
  try {
    const u = new URL(v.trim());
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
};

const SAMPLES: Record<AnalyzeMode, { label: string; value: string }[]> = {
  text: [
    {
      label: "Sample: dramatic claim",
      value:
        "BREAKING: Scientists confirm chocolate cures all known diseases overnight! Government allegedly hiding the cure for decades — share before they delete this!",
    },
    {
      label: "Sample: factual report",
      value:
        "The European Central Bank announced today a 0.25% reduction in its main interest rate, citing easing inflation across the eurozone, according to a statement published on its official website.",
    },
  ],
  url: [
    { label: "Sample URL", value: "https://www.bbc.com/news" },
  ],
};

interface Props {
  onAnalyzed: (entries: HistoryEntry[]) => void;
}

const Analyzer = ({ onAnalyzed }: Props) => {
  const [mode, setMode] = useState<AnalyzeMode>("text");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [lastInput, setLastInput] = useState<{ mode: AnalyzeMode; value: string } | null>(null);

  const charCount = text.length;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const value = mode === "text" ? text.trim() : url.trim();

    if (!value) {
      toast.error(mode === "text" ? "Please paste some article text." : "Please paste an article URL.");
      return;
    }
    if (mode === "url" && !isLikelyUrl(value)) {
      toast.error("That doesn't look like a valid URL. Include http:// or https://");
      return;
    }
    if (mode === "text" && value.length < 30) {
      toast.error("Please paste at least 30 characters for a meaningful analysis.");
      return;
    }

    setLoading(true);
    setResult(null);
    setLastInput({ mode, value });
    try {
      const data = await analyzeContent({ mode, value });
      if (data.error) {
        toast.error(data.error);
        setResult(null);
      } else {
        setResult(data);
        const entry: HistoryEntry = {
          id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
          createdAt: Date.now(),
          mode,
          input: value,
          result: data,
        };
        const updated = saveHistoryEntry(entry);
        onAnalyzed(updated);
        toast.success("Analysis complete");
      }
    } catch (err) {
      if (err instanceof BackendUnreachableError) {
        toast.error("Backend unreachable", {
          description: "Make sure your Flask server is running on http://127.0.0.1:5000",
        });
      } else {
        toast.error(err instanceof Error ? err.message : "Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setText("");
    setUrl("");
    setLastInput(null);
  };

  const loadSample = (v: string) => {
    if (mode === "text") setText(v);
    else setUrl(v);
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="glass rounded-3xl p-5 sm:p-7">
        {/* Header row */}
        <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-display text-xl font-bold">Run an analysis</h2>
            <p className="text-sm text-muted-foreground">
              Choose a mode and paste your content. We'll send it to Groq AI for verdict & reasoning.
            </p>
          </div>

          {/* Mode toggle */}
          <div className="inline-flex shrink-0 rounded-full border border-white/10 bg-background/40 p-1">
            {(["text", "url"] as AnalyzeMode[]).map((m) => {
              const active = mode === m;
              const Icon = m === "text" ? FileText : Link2;
              return (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMode(m)}
                  className={`relative inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all ${
                    active
                      ? "bg-gradient-brand text-primary-foreground shadow-glow-brand"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {m === "text" ? "Text" : "URL"}
                </button>
              );
            })}
          </div>
        </div>

        {/* Inputs */}
        <div className="space-y-4">
          {mode === "text" ? (
            <div className="relative">
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste a news article here…"
                disabled={loading}
                className="min-h-[200px] resize-y border-white/10 bg-background/40 text-base placeholder:text-muted-foreground/70 focus-visible:ring-brand-1"
              />
              <div className="pointer-events-none absolute bottom-2 right-3 text-[11px] text-muted-foreground">
                {charCount} chars
              </div>
            </div>
          ) : (
            <Input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/article"
              disabled={loading}
              className="h-12 border-white/10 bg-background/40 text-base placeholder:text-muted-foreground/70 focus-visible:ring-brand-1"
            />
          )}

          {/* Samples */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1 text-xs uppercase tracking-wider text-muted-foreground">
              <Sparkles className="h-3 w-3 text-brand-1" /> Try
            </span>
            {SAMPLES[mode].map((s) => (
              <button
                key={s.label}
                type="button"
                disabled={loading}
                onClick={() => loadSample(s.value)}
                className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-muted-foreground transition-colors hover:border-brand-1/40 hover:bg-brand-1/10 hover:text-foreground disabled:opacity-50"
              >
                {s.label}
              </button>
            ))}
          </div>

          {/* Submit / loader */}
          {loading ? (
            <RadarLoader />
          ) : (
            <Button
              type="submit"
              size="lg"
              className="group h-12 w-full gap-2 bg-gradient-brand text-primary-foreground transition-all hover:shadow-glow-brand hover:brightness-110"
            >
              <Search className="h-4 w-4 transition-transform group-hover:scale-110" />
              Analyze Now
            </Button>
          )}
        </div>
      </form>

      {result && <ResultsDashboard data={result} input={lastInput} onReset={reset} />}
    </div>
  );
};

export default Analyzer;
