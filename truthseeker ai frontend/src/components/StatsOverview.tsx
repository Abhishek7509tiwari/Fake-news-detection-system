import { ShieldCheck, AlertTriangle, CheckCircle2, Activity } from "lucide-react";
import type { HistoryEntry } from "@/lib/api";

interface Props {
  history: HistoryEntry[];
}

const StatsOverview = ({ history }: Props) => {
  const total = history.length;
  const fake = history.filter((h) => (h.result.result || "").toUpperCase() === "FAKE").length;
  const real = history.filter((h) => (h.result.result || "").toUpperCase() === "REAL").length;
  const accuracy = total > 0 ? Math.round((real / total) * 100) : 0;

  const stats = [
    {
      label: "Total Analyses",
      value: total,
      icon: Activity,
      iconClass: "text-brand-1 bg-brand-1/10",
    },
    {
      label: "Real Detected",
      value: real,
      icon: CheckCircle2,
      iconClass: "text-real bg-real/10",
    },
    {
      label: "Fake Detected",
      value: fake,
      icon: AlertTriangle,
      iconClass: "text-fake bg-fake/10",
    },
    {
      label: "Real Ratio",
      value: `${accuracy}%`,
      icon: ShieldCheck,
      iconClass: "text-brand-2 bg-brand-2/10",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
      {stats.map((s, i) => {
        const Icon = s.icon;
        return (
          <div
            key={s.label}
            className="glass animate-fade-in rounded-2xl p-4 sm:p-5"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground">{s.label}</div>
                <div className="mt-2 font-display text-2xl font-bold sm:text-3xl">{s.value}</div>
              </div>
              <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${s.iconClass}`}>
                <Icon className="h-5 w-5" />
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatsOverview;
