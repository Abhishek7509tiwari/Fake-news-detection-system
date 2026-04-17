import logging
import sys
import os

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "fake_news_alerts.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("FakeNewsAlert")

class AlertSystem:
    def __init__(self):
        pass

    def trigger_alert(self, title, confidence, source="Unknown"):
        """
        Triggers an alert if fake news is detected.
        """
        alert_msg = f"FAKE NEWS DETECTED\nTitle: {title}\nSource: {source}\nConfidence: {confidence:.2%}"
        
        # Log to file and console
        logger.warning(alert_msg)
        
        # Return alert data structure for UI
        return {
            "alert": True,
            "level": "critical",
            "message": alert_msg,
            "title": title,
            "confidence": confidence
        }

    def log_real_news(self, title, confidence):
        """
        Logs real news detection.
        """
        msg = f"✅ Real News Verified: {title} ({confidence:.2%})"
        logger.info(msg)
        return {
            "alert": False,
            "level": "info",
            "message": msg,
            "title": title,
            "confidence": confidence
        }
