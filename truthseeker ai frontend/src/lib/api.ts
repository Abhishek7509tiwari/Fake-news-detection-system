export type AnalyzeMode = "text" | "url";

export interface ModelInfo {
  id: string;
  name: string;
  ctx: number;
}

export interface AnalyzeResponse {
  result?: "FAKE" | "REAL" | string;
  reasoning?: string;
  confidence?: number;
  original_title?: string;
  scraped_text_preview?: string;
  model_used?: ModelInfo | null;
  error?: string;
}

export interface AnalyzeArgs {
  mode: AnalyzeMode;
  value: string;
}

const API_BASE = "http://127.0.0.1:5000";
const API_URL = `${API_BASE}/api/analyze`;

export class BackendUnreachableError extends Error {
  constructor(message = "Backend unreachable") {
    super(message);
    this.name = "BackendUnreachableError";
  }
}

export async function analyzeContent({ mode, value }: AnalyzeArgs): Promise<AnalyzeResponse> {
  const body = mode === "url" ? { url: value } : { text: value };

  let response: Response;
  try {
    response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new BackendUnreachableError(
      "Could not reach the TruthSeeker backend at http://127.0.0.1:5000. Make sure your Flask server is running."
    );
  }

  let data: AnalyzeResponse | null = null;
  try {
    data = (await response.json()) as AnalyzeResponse;
  } catch {
    throw new Error(`Invalid response from server (status ${response.status}).`);
  }

  if (!response.ok && !data?.error) {
    throw new Error(`Request failed with status ${response.status}.`);
  }

  return data ?? {};
}

/* ---------- API Key management ---------- */

export interface HealthResponse {
  status: string;
  api_key_configured: boolean;
  model_hierarchy?: string[];
}

export async function checkHealth(): Promise<HealthResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    return (await res.json()) as HealthResponse;
  } catch {
    throw new BackendUnreachableError(
      "Could not reach the TruthSeeker backend. Make sure your Flask server is running."
    );
  }
}

export async function setApiKey(apiKey: string): Promise<{ status?: string; error?: string }> {
  try {
    const res = await fetch(`${API_BASE}/api/set-key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey }),
    });
    return await res.json();
  } catch {
    throw new BackendUnreachableError(
      "Could not reach the TruthSeeker backend. Make sure your Flask server is running."
    );
  }
}

export interface ModelsResponse {
  models: ModelInfo[];
  last_used: ModelInfo | null;
}

export async function getModels(): Promise<ModelsResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/models`);
    return (await res.json()) as ModelsResponse;
  } catch {
    throw new BackendUnreachableError(
      "Could not reach the TruthSeeker backend. Make sure your Flask server is running."
    );
  }
}

/* ---------- Local history ---------- */

export interface HistoryEntry {
  id: string;
  createdAt: number;
  mode: AnalyzeMode;
  input: string;
  result: AnalyzeResponse;
}

const HISTORY_KEY = "truthseeker.history.v1";
const HISTORY_LIMIT = 20;

export function loadHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as HistoryEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveHistoryEntry(entry: HistoryEntry): HistoryEntry[] {
  const current = loadHistory();
  const next = [entry, ...current].slice(0, HISTORY_LIMIT);
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
  } catch {
    /* ignore quota */
  }
  return next;
}

export function clearHistory(): void {
  try {
    localStorage.removeItem(HISTORY_KEY);
  } catch {
    /* ignore */
  }
}
