import { ScanSearch, ShieldCheck, Sparkles, ArrowRight, Brain, Lock, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import StatsOverview from "./StatsOverview";
import type { HistoryEntry } from "@/lib/api";

interface Props {
  history: HistoryEntry[];
  onStart: () => void;
}

const features = [
  {
    icon: Brain,
    title: "Groq-powered reasoning",
    desc: "Analyzes tone, claims and source quality to produce a clear verdict and explanation.",
  },
  {
    icon: Globe,
    title: "Text or URL input",
    desc: "Paste raw article text or a link — we'll handle the rest via your Flask backend.",
  },
  {
    icon: Lock,
    title: "Private by default",
    desc: "No accounts. History is stored only in your browser, never on our servers.",
  },
];

const HomeView = ({ history, onStart }: Props) => {
  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl">
        <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-20 left-1/2 h-[420px] w-[720px] -translate-x-1/2 rounded-full bg-brand-1/15 blur-3xl animate-bg-drift" />
          <div className="absolute right-0 top-10 h-[260px] w-[260px] rounded-full bg-brand-2/15 blur-3xl" />
        </div>

        <div className="glass rounded-3xl px-6 py-10 sm:px-10 sm:py-14">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs text-muted-foreground backdrop-blur">
            <Sparkles className="h-3.5 w-3.5 text-brand-1" />
            Powered by Groq AI
          </div>
          <h1 className="font-display text-4xl font-bold leading-[1.05] sm:text-5xl md:text-6xl">
            Detect misinformation in <span className="text-gradient-brand">seconds</span>.
          </h1>
          <p className="mt-4 max-w-xl text-base text-muted-foreground sm:text-lg">
            TruthSeeker AI examines articles for linguistic patterns, contextual signals and
            unsupported claims — then gives you a clear verdict with reasoning you can review.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Button
              onClick={onStart}
              size="lg"
              className="group h-12 gap-2 bg-gradient-brand text-primary-foreground transition-all hover:shadow-glow-brand hover:brightness-110"
            >
              <ScanSearch className="h-4 w-4" />
              Start analyzing
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Button>
            <Button variant="outline" size="lg" asChild className="h-12">
              <a href="#features">
                <ShieldCheck className="h-4 w-4" /> How it works
              </a>
            </Button>
          </div>
        </div>
      </section>

      {/* Stats */}
      <StatsOverview history={history} />

      {/* Features */}
      <section id="features" className="grid gap-4 md:grid-cols-3">
        {features.map((f, i) => {
          const Icon = f.icon;
          return (
            <div
              key={f.title}
              className="glass animate-fade-in rounded-2xl p-6"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-brand shadow-glow-brand">
                <Icon className="h-5 w-5 text-primary-foreground" />
              </span>
              <h3 className="mt-4 font-display text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
            </div>
          );
        })}
      </section>
    </div>
  );
};

export default HomeView;
