import {
  CheckCircle2,
  AlertTriangle,
  FileText,
  Quote,
  RotateCcw,
  Link2,
  Copy,
  Gauge,
  Cpu,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import type { AnalyzeMode, AnalyzeResponse } from "@/lib/api";

interface Props {
  data: AnalyzeResponse;
  input?: { mode: AnalyzeMode; value: string } | null;
  onReset: () => void;
}

const ResultsDashboard = ({ data, input, onReset }: Props) => {
  const verdict = (data.result || "").toUpperCase();
  const isReal = verdict === "REAL";
  const isFake = verdict === "FAKE";

  const confidencePct = Math.round((data.confidence ?? 0) * 100);

  const tone = isReal
    ? {
        label: "REAL NEWS",
        sub: "Looks credible based on linguistic & contextual signals",
        icon: CheckCircle2,
        ring: "border-real/40",
        text: "text-real",
        glow: "shadow-glow-real",
        bg: "bg-real/10",
        bar: "bg-real",
      }
    : isFake
    ? {
        label: "FAKE NEWS",
        sub: "Suspicious — review the reasoning carefully",
        icon: AlertTriangle,
        ring: "border-fake/40",
        text: "text-fake",
        glow: "shadow-glow-fake",
        bg: "bg-fake/10",
        bar: "bg-fake",
      }
    : {
        label: verdict || "UNCERTAIN",
        sub: "The model couldn't reach a confident verdict",
        icon: AlertTriangle,
        ring: "border-white/15",
        text: "text-foreground",
        glow: "",
        bg: "bg-white/5",
        bar: "bg-white/30",
      };

  const Icon = tone.icon;

  const copyReasoning = async () => {
    if (!data.reasoning) return;
    try {
      await navigator.clipboard.writeText(data.reasoning);
      toast.success("Reasoning copied");
    } catch {
      toast.error("Couldn't copy to clipboard");
    }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Verdict banner */}
      <div
        className={`glass relative overflow-hidden rounded-3xl border ${tone.ring} ${tone.glow} p-6 sm:p-8`}
      >
        <div className={`absolute inset-x-0 top-0 h-1 ${tone.bar}`} />
        <div className="flex flex-col items-start gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${tone.bg}`}>
              <Icon className={`h-7 w-7 ${tone.text}`} />
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-[0.25em] text-muted-foreground">Verdict</div>
              <div className={`font-display text-3xl font-bold tracking-tight sm:text-4xl ${tone.text}`}>
                {tone.label}
              </div>
              <div className="mt-1 text-sm text-muted-foreground">{tone.sub}</div>
            </div>
          </div>
          <Button variant="outline" onClick={onReset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            New analysis
          </Button>
        </div>

        {/* Model used badge */}
        {data.model_used && (
          <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-muted-foreground">
            <Cpu className="h-3 w-3 text-brand-1" />
            Analyzed by <span className="font-semibold text-foreground">{data.model_used.name}</span>
          </div>
        )}
      </div>

      <div className="grid gap-5 lg:grid-cols-5">
        {/* Reasoning */}
        {data.reasoning && (
          <div className="glass rounded-2xl p-6 lg:col-span-3">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                <Quote className="h-4 w-4 text-brand-1" />
                AI Reasoning
              </div>
              <button
                onClick={copyReasoning}
                className="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-white/5 hover:text-foreground"
              >
                <Copy className="h-3.5 w-3.5" /> Copy
              </button>
            </div>
            <p className="whitespace-pre-line text-sm leading-relaxed text-muted-foreground">
              {data.reasoning}
            </p>
          </div>
        )}

        {/* Source preview + Confidence */}
        <div className="glass rounded-2xl p-6 lg:col-span-2 space-y-5">
          {/* Confidence meter */}
          {data.confidence != null && data.confidence > 0 && (
            <div>
              <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-foreground">
                <Gauge className="h-4 w-4 text-brand-2" />
                Confidence
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-3 rounded-full bg-white/10 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ease-out ${tone.bar}`}
                    style={{ width: `${confidencePct}%` }}
                  />
                </div>
                <span className={`text-lg font-bold tabular-nums ${tone.text}`}>
                  {confidencePct}%
                </span>
              </div>
            </div>
          )}

          {/* Source info */}
          <div>
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
              <FileText className="h-4 w-4 text-brand-2" />
              Source Preview
            </div>
            {data.original_title && (
              <h3 className="mb-2 font-display text-lg font-semibold leading-snug text-foreground">
                {data.original_title}
              </h3>
            )}
            {data.scraped_text_preview ? (
              <p className="line-clamp-[10] text-sm leading-relaxed text-muted-foreground">
                {data.scraped_text_preview}
              </p>
            ) : (
              !data.original_title && (
                <p className="text-sm text-muted-foreground">No additional source metadata returned.</p>
              )
            )}

            {input?.mode === "url" && (
              <a
                href={input.value}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex items-center gap-1.5 text-xs text-brand-1 transition-colors hover:text-brand-2"
              >
                <Link2 className="h-3.5 w-3.5" /> Open original source
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;
