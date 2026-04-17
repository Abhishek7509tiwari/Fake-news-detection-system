import os
import sys
import json
from google import genai

# Make sure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.scraper import NewsScraper
from src.core.alert_system import AlertSystem

class AutomatedPipeline:
    def __init__(self, api_key=None):
        self.scraper = NewsScraper()
        self.alert_system = AlertSystem()
        
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "AIzaSyB8hzixiGLWiYBLkH4Pgh-sy8G-PlH3m6s")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: GEMINI_API_KEY not set. Pipeline will not be able to analyze text.")

    def configure_api(self, api_key):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)

    def _analyze_with_gemini(self, text):
        if not self.client:
            return None, 0.0, "API key not configured."
        
        prompt = f"""
You are an expert AI Fake News Detector. Analyze the following news article text and determine if it is likely "REAL" or "FAKE" news.
Look for linguistic patterns, extreme bias, unsubstantiated claims, or classic misinformation tactics.

Provide your analysis in STRICT JSON format with exactly three keys:
- "result": string of either "REAL" or "FAKE"
- "confidence": a float between 0.0 and 1.0 representing your confidence in this assessment
- "reasoning": a brief sentence explaining why.

Do not include markdown tags like ```json in the output, just raw JSON.

Article text:
{text[:8000]}
""" 
        import time
        max_retries = 3
        retry_delay = 2
        
        response = None
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                break
            except Exception as e:
                last_error = e
                error_str = str(e)
                if "503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str or "high demand" in error_str:
                    print(f"API busy (503/429), retrying... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    print(f"Error calling Gemini API: {e}")
                    return None, 0.0, str(e)
        
        if not response:
            return None, 0.0, f"Analysis failed after {max_retries} attempts. Last error: {last_error}"

        try:
            # Try to parse the response robustly
            response_text = response.text.strip()
            
            # Find JSON block if it's wrapped in markdown
            import re
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            else:
                # If no markdown blocks, try to find the start and end of a JSON object
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    response_text = response_text[start:end+1]
                    
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                return None, 0.0, f"Failed to parse AI response as JSON: {e}"
            
            result = data.get("result", "FAKE").upper()
            if result not in ["REAL", "FAKE"]:
                result = "FAKE"
            
            confidence = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "No context provided.")
            
            return result, confidence, reasoning
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None, 0.0, str(e)

    def run_url(self, url):
        """Runs the pipeline for a given URL."""
        if not self.client:
            return {"error": "Gemini API key not configured."}

        # 1. Scrape
        print(f"Scraping {url}...")
        scraped_data = self.scraper.scrape_url(url)
        
        if scraped_data.get("error"):
            return {"error": scraped_data["error"]}
            
        text = scraped_data.get("text", "")
        title = scraped_data.get("title", "Unknown Title")
        
        if not text:
            return {"error": "No text content found in article."}

        # 2. Analyze
        result, confidence, reasoning = self._analyze_with_gemini(text)
        
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
        return response_data

    def run_text(self, text):
        """Runs the pipeline for raw text input."""
        if not self.client:
             return {"error": "Gemini API key not configured."}
             
        result, confidence, reasoning = self._analyze_with_gemini(text)
        
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
        return response_data

if __name__ == "__main__":
    # Test
    pipeline = AutomatedPipeline()
    # print(pipeline.run_text("This is a test article..."))
