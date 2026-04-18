import { ShieldCheck, Workflow, ServerCog, Lock } from "lucide-react";

const sections = [
  {
    icon: Workflow,
    title: "How it works",
    body: "You paste an article or URL. The frontend sends it to your local Flask backend at http://127.0.0.1:5000/api/analyze, which uses Groq AI (Llama 3.3 70B) to evaluate the content. The verdict (REAL or FAKE) and the model's reasoning are returned and rendered in the dashboard.",
  },
  {
    icon: ServerCog,
    title: "Backend contract",
    body: "POST JSON with either {\"text\": \"…\"} or {\"url\": \"…\"}. The response should include result, reasoning, and optionally original_title and scraped_text_preview. An error field will be surfaced as a toast.",
  },
  {
    icon: Lock,
    title: "Privacy",
    body: "TruthSeeker runs entirely against your own backend. Recent analyses are stored only in your browser's localStorage so you can review them later — clearing your history removes them immediately.",
  },
  {
    icon: ShieldCheck,
    title: "Limitations",
    body: "AI verdicts are an aid, not a final source of truth. Always review the reasoning, check the original source, and cross-reference with reputable outlets before acting on a result.",
  },
];

const AboutView = () => {
  return (
    <div className="space-y-6">
      <div className="glass rounded-3xl p-6 sm:p-8">
        <h2 className="font-display text-2xl font-bold sm:text-3xl">
          About <span className="text-gradient-brand">TruthSeeker</span>
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground sm:text-base">
          A premium frontend for an AI-powered fake news detector — designed to make Groq AI's
          verdicts clear, fast and actionable.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {sections.map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.title} className="glass rounded-2xl p-6">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-white/5">
                <Icon className="h-5 w-5 text-brand-1" />
              </span>
              <h3 className="mt-4 font-display text-lg font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.body}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AboutView;
