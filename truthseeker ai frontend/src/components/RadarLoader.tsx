import { useEffect, useState } from "react";

const MESSAGES = [
  "AI is analyzing the context, linguistic patterns, and claims…",
  "Cross-referencing tone and source signals…",
  "Evaluating factual consistency…",
  "Synthesizing the verdict…",
];

const RadarLoader = () => {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const id = window.setInterval(() => {
      setIdx((i) => (i + 1) % MESSAGES.length);
    }, 2200);
    return () => window.clearInterval(id);
  }, []);

  return (
    <div className="flex flex-col items-center gap-6 py-4 animate-fade-in">
      <div className="relative h-40 w-40">
        {/* Concentric rings */}
        <div className="absolute inset-0 rounded-full border border-brand-1/30" />
        <div className="absolute inset-4 rounded-full border border-brand-1/20" />
        <div className="absolute inset-8 rounded-full border border-brand-1/15" />
        <div className="absolute inset-14 rounded-full border border-brand-1/10" />

        {/* Pulse */}
        <div className="absolute inset-0 rounded-full bg-brand-1/10 animate-radar-pulse" />

        {/* Sweep */}
        <div className="absolute inset-0 animate-radar-sweep">
          <div
            className="absolute left-1/2 top-1/2 h-1/2 w-1/2 origin-top-left"
            style={{
              background:
                "conic-gradient(from 0deg, hsl(var(--brand-1) / 0.55), transparent 60%)",
              clipPath: "polygon(0 0, 100% 0, 0 100%)",
            }}
          />
        </div>

        {/* Center dot */}
        <div className="absolute left-1/2 top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-brand-1 shadow-glow-brand" />
      </div>

      <p
        key={idx}
        className="max-w-sm text-center text-sm text-muted-foreground animate-fade-in"
      >
        {MESSAGES[idx]}
      </p>
    </div>
  );
};

export default RadarLoader;
