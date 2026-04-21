import ApiKeyBanner from "@/components/ApiKeyBanner";
import { Settings } from "lucide-react";

const SettingsView = () => {
  return (
    <div className="space-y-6">
      <div className="glass rounded-2xl border border-white/5 p-6 animate-fade-in shadow-xl">
        <h2 className="font-display text-xl font-bold mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5 text-muted-foreground" />
          Settings
        </h2>
        <div className="space-y-4 text-sm text-muted-foreground">
          <p>
            Configure your application settings and update required API keys here.
          </p>
          
          <div className="pt-4 border-t border-white/5">
            <h3 className="text-foreground font-semibold mb-3">API Configuration</h3>
            <ApiKeyBanner onConfigured={() => {}} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsView;
