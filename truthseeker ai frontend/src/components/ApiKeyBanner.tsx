import { useState } from "react";
import { KeyRound, CheckCircle2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { setApiKey } from "@/lib/api";

interface Props {
  onConfigured: () => void;
}

const ApiKeyBanner = ({ onConfigured }: Props) => {
  const [key, setKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = key.trim();
    if (!trimmed) {
      toast.error("Please paste your Groq API key.");
      return;
    }
    setLoading(true);
    try {
      const res = await setApiKey(trimmed);
      if (res.error) {
        toast.error(res.error);
      } else {
        setDone(true);
        toast.success("API key configured successfully!");
        setTimeout(onConfigured, 600);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to set API key.");
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <div className="glass rounded-2xl border border-real/30 p-5 flex items-center gap-3 animate-fade-in">
        <CheckCircle2 className="h-5 w-5 text-real shrink-0" />
        <p className="text-sm text-real font-medium">API key configured — you're all set!</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="glass rounded-2xl border border-amber-500/30 p-5 space-y-3 animate-fade-in">
      <div className="flex items-start gap-3">
        <KeyRound className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-semibold text-foreground">Groq API Key Required</p>
          <p className="text-xs text-muted-foreground mt-1">
            Your backend needs a valid Groq API key to analyze articles. 
            Get one free at{" "}
            <a
              href="https://console.groq.com/keys"
              target="_blank"
              rel="noreferrer"
              className="text-brand-1 underline underline-offset-2 hover:text-brand-2"
            >
              console.groq.com/keys
            </a>
          </p>
        </div>
      </div>
      <div className="flex gap-2">
        <Input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="Paste your Groq API key here…"
          disabled={loading}
          className="flex-1 h-10 border-white/10 bg-background/40 text-sm placeholder:text-muted-foreground/60 focus-visible:ring-brand-1"
        />
        <Button
          type="submit"
          disabled={loading || !key.trim()}
          className="h-10 gap-2 bg-gradient-brand text-primary-foreground hover:brightness-110"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <KeyRound className="h-4 w-4" />}
          Set Key
        </Button>
      </div>
    </form>
  );
};

export default ApiKeyBanner;
