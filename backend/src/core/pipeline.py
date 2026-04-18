import os
import sys
import json
import re
import time
from groq import Groq

# Make sure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.scraper import NewsScraper
from src.core.alert_system import AlertSystem

# ─── Model Hierarchy (best → fallback) ───────────────────────────────────────
# Ordered by quality/capability. On rate-limit (429) the pipeline automatically
# falls through to the next model in the list.
MODEL_HIERARCHY = [
    {
        "id": "compound-beta",              # Groq Compound: web search + code exec + multi-model
        "name": "Groq Compound (Agentic)",
        "ctx": 131072,
    },
    {
        "id": "openai/gpt-oss-120b",        # OpenAI GPT-OSS 120B: flagship open-weight
        "name": "GPT-OSS 120B",
        "ctx": 131072,
    },
    {
        "id": "meta-llama/llama-4-scout-17b-16e-instruct",  # Llama 4 Scout 17B (MoE)
        "name": "Llama 4 Scout 17B",
        "ctx": 131072,
    },
    {
        "id": "qwen/qwen3-32b",             # Qwen3 32B
        "name": "Qwen3 32B",
        "ctx": 32768,
    },
    {
        "id": "llama-3.3-70b-versatile",     # Llama 3.3 70B – production workhorse
        "name": "Llama 3.3 70B",
        "ctx": 131072,
    },
    {
        "id": "openai/gpt-oss-20b",         # GPT-OSS 20B – fast fallback
        "name": "GPT-OSS 20B",
        "ctx": 131072,
    },
    {
        "id": "llama-3.1-8b-instant",        # Llama 3.1 8B – ultra-fast last resort
        "name": "Llama 3.1 8B",
        "ctx": 131072,
    },
]

def get_model_by_id(model_id: str):
    """Return the model dict for a given ID, or None."""
    for m in MODEL_HIERARCHY:
        if m["id"] == model_id:
            return m
    return None


class AutomatedPipeline:
    def __init__(self, api_key=None):
        self.scraper = NewsScraper()
        self.alert_system = AlertSystem()

        # .env file lives in the backend root for persistence
        self._env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env"
        )

        # Priority: explicit arg → env var → saved .env file
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "") or self._load_saved_key()
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
            print(f"[Pipeline] Groq API key loaded successfully.")
        else:
            self.client = None
            print("Warning: GROQ_API_KEY not set. Pipeline will not be able to analyze text.")

        # Track which model was actually used for the last call
        self.last_model_used = None

    def _load_saved_key(self):
        """Load the API key from the saved .env file."""
        try:
            if os.path.exists(self._env_path):
                with open(self._env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GROQ_API_KEY="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
        return ""

    def _save_key(self, api_key):
        """Persist the API key to the .env file so it survives restarts."""
        try:
            # Read existing lines (if any), replace or append
            lines = []
            found = False
            if os.path.exists(self._env_path):
                with open(self._env_path, "r") as f:
                    for line in f:
                        if line.strip().startswith("GROQ_API_KEY="):
                            lines.append(f"GROQ_API_KEY={api_key}\n")
                            found = True
                        else:
                            lines.append(line)
            if not found:
                lines.append(f"GROQ_API_KEY={api_key}\n")
            with open(self._env_path, "w") as f:
                f.writelines(lines)
            print(f"[Pipeline] API key saved to {self._env_path}")
        except Exception as e:
            print(f"[Pipeline] Warning: could not save API key to .env: {e}")

    def configure_api(self, api_key):
        """Set the API key at runtime and persist it to disk."""
        self.api_key = api_key
        self.client = Groq(api_key=self.api_key)
        self._save_key(api_key)

    @staticmethod
    def get_model_hierarchy():
        """Return the full model hierarchy for the frontend to display."""
        return MODEL_HIERARCHY

    def _analyze_with_groq(self, text):
        """
        Try each model in the hierarchy. On 429/rate-limit/unavailable errors,
        fall through to the next model automatically.
        """
        if not self.client:
            return None, 0.0, "API key not configured.", None

        system_prompt = """You are an expert AI Fake News Detector. Analyze news article text and determine if it is likely "REAL" or "FAKE" news.
Look for linguistic patterns, extreme bias, unsubstantiated claims, or classic misinformation tactics.

Provide your analysis in STRICT JSON format with exactly three keys:
- "result": string of either "REAL" or "FAKE"
- "confidence": a float between 0.0 and 1.0 representing your confidence in this assessment
- "reasoning": a detailed 2-3 sentence explanation of why you reached this verdict.

Do not include markdown tags like ```json in the output, just raw JSON."""

        user_prompt = f"Article text:\n{text[:8000]}"

        last_error = None

        for model_info in MODEL_HIERARCHY:
            model_id = model_info["id"]
            model_name = model_info["name"]

            # Per-model retry (for transient 503s etc.)
            for attempt in range(2):
                try:
                    print(f"[Pipeline] Trying model: {model_name} ({model_id}) – attempt {attempt+1}")
                    response = self.client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.3,
                        max_tokens=512,
                    )
                    self.last_model_used = model_info
                    return self._parse_response(response, model_name)

                except Exception as e:
                    last_error = e
                    error_str = str(e).lower()
                    is_rate_limit = any(k in error_str for k in [
                        "429", "rate", "limit", "quota", "too many",
                        "503", "unavailable", "overloaded", "capacity",
                    ])
                    if is_rate_limit:
                        print(f"[Pipeline] {model_name} rate-limited/unavailable: {e}")
                        if attempt == 0:
                            time.sleep(1)       # brief pause before retry on same model
                            continue
                        else:
                            break               # move to next model in hierarchy
                    else:
                        # Non-rate-limit error (auth, bad request, etc.) — don't retry
                        print(f"[Pipeline] {model_name} error (non-retryable): {e}")
                        return None, 0.0, str(e), None

        # All models exhausted
        return None, 0.0, f"All models rate-limited. Last error: {last_error}", None

    def _parse_response(self, response, model_name):
        """Extract result, confidence, reasoning from the LLM response."""
        try:
            response_text = response.choices[0].message.content.strip()

            # Strip markdown fences
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            else:
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    response_text = response_text[start:end+1]

            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                return None, 0.0, f"Failed to parse AI response as JSON: {e}", model_name

            result = data.get("result", "FAKE").upper()
            if result not in ["REAL", "FAKE"]:
                result = "FAKE"

            confidence = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "No context provided.")

            return result, confidence, reasoning, model_name
        except Exception as e:
            print(f"[Pipeline] Error parsing response from {model_name}: {e}")
            return None, 0.0, str(e), model_name

    def run_url(self, url):
        """Runs the pipeline for a given URL."""
        if not self.client:
            return {"error": "Groq API key not configured."}

        # 1. Scrape
        print(f"[Pipeline] Scraping {url}...")
        scraped_data = self.scraper.scrape_url(url)

        if scraped_data.get("error"):
            return {"error": scraped_data["error"]}

        text = scraped_data.get("text", "")
        title = scraped_data.get("title", "Unknown Title")

        if not text:
            return {"error": "No text content found in article."}

        # 2. Analyze
        result, confidence, reasoning, model_used = self._analyze_with_groq(text)

        if not result:
            return {"error": f"Analysis failed: {reasoning}"}

        # 3. Alert / Result
        if result == "FAKE":
            response_data = self.alert_system.trigger_alert(title, confidence, source=url)
            response_data["result"] = "FAKE"
        else:
            response_data = self.alert_system.log_real_news(title, confidence)
            response_data["result"] = "REAL"

        response_data["original_title"] = title
        response_data["reasoning"] = reasoning
        response_data["scraped_text_preview"] = text[:200] + "..."
        response_data["model_used"] = model_used
        return response_data

    def run_text(self, text):
        """Runs the pipeline for raw text input."""
        if not self.client:
            return {"error": "Groq API key not configured."}

        result, confidence, reasoning, model_used = self._analyze_with_groq(text)

        if not result:
            return {"error": f"Analysis failed: {reasoning}"}

        title = "User Input Text"

        if result == "FAKE":
            response_data = self.alert_system.trigger_alert(title, confidence, source="Manual Input")
            response_data["result"] = "FAKE"
        else:
            response_data = self.alert_system.log_real_news(title, confidence)
            response_data["result"] = "REAL"

        response_data["reasoning"] = reasoning
        response_data["model_used"] = model_used
        return response_data


if __name__ == "__main__":
    pipeline = AutomatedPipeline()
    # print(pipeline.run_text("This is a test article..."))
