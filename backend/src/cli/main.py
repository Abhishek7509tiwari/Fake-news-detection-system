import sys
import os
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.absolute()))
from src.core.pipeline import AutomatedPipeline

def predict(text, pipeline):
    if not text.strip():
        return

    is_url = text.startswith("http://") or text.startswith("https://")
    if is_url:
        result_data = pipeline.run_url(text)
    else:
        result_data = pipeline.run_text(text)
    
    if "error" in result_data:
        print(f"Error: {result_data['error']}")
        return

    result = result_data.get("result", "UNKNOWN")
    confidence = result_data.get("confidence", 0.0)
    reasoning = result_data.get("reasoning", "No specific reasoning.")
    
    print("\n" + "="*40)
    print(f"Prediction: {result}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Reasoning: {reasoning}")
    print("="*40 + "\n")

if __name__ == "__main__":
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyB8hzixiGLWiYBLkH4Pgh-sy8G-PlH3m6s")

    pipeline = AutomatedPipeline(api_key=api_key)

    print("--- Fake News Detector CLI (Powered by Gemini) ---")
    
    # Check if text was passed as argument
    if len(sys.argv) > 1:
        # Join all arguments as one string in case the text wasn't quoted
        text = " ".join(sys.argv[1:])
        predict(text, pipeline)
    else:
        # Interactive mode
        print("Enter news text to classify (or type 'exit' to quit):")
        while True:
            try:
                user_input = input(">> ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                predict(user_input, pipeline)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
