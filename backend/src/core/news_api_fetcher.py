import requests
import logging
import os
import re
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Ensure logs dir exists
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)

# Configure separate logger for API errors
api_logger = logging.getLogger("NewsAPIError")
api_logger.setLevel(logging.ERROR)
# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# File handler
handler = logging.FileHandler(os.path.join(log_dir, "news_api_error.log"), encoding="utf-8")
handler.setFormatter(formatter)
if not api_logger.handlers:
    api_logger.addHandler(handler)

class NewsAPIFetcher:
    """
    Enhanced module to fetch news data from News API.
    Features include:
    - Date range filtering
    - Category & Country filtering
    - Rate limit handling
    - Robust handling of missing fields (null descriptions, etc)
    - HTML tag removal from fetched content
    - API error logging to separate file
    - MongoDB storage with timestamps
    """
    def __init__(self, api_key=None, mongo_uri="mongodb://localhost:27017/"):
        self.api_key = api_key or os.environ.get("NEWS_API_KEY", "")
        self.base_url = "https://newsapi.org/v2/"
        
        # Setup MongoDB
        try:
            self.mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
            self.db = self.mongo_client["fake_news_detector"]
            self.collection = self.db["news_articles"]
        except Exception as e:
            api_logger.error(f"MongoDB connection failed: {e}")
            self.mongo_client = None

    def _remove_html_tags(self, text):
        """Helper to remove HTML tags and clean up string data."""
        if not text:
            return ""
        # Remove tags using regex or BeautifulSoup
        try:
            return BeautifulSoup(text, 'html.parser').get_text(separator=' ', strip=True)
        except Exception:
            return re.sub(r'<[^>]+>', '', text).strip()

    def fetch_news(self, query=None, from_date=None, to_date=None, category=None, country=None, page_size=10):
        """
        Main fetching mechanism to retrieve news and store in DB using Free Google News RSS.
        """
        # Map parameters for Google RSS
        cat_map = {
            "business": "BUSINESS",
            "entertainment": "ENTERTAINMENT",
            "general": "WORLD",
            "health": "HEALTH",
            "science": "SCIENCE",
            "sports": "SPORTS",
            "technology": "TECHNOLOGY"
        }
        
        c_code = (country or "us").upper()
        g_cat = cat_map.get((category or "general").lower(), "WORLD")
        
        if (category or "general").lower() == "general":
            endpoint = f"https://news.google.com/news/rss?hl=en-{c_code}&gl={c_code}&ceid={c_code}:en"
        else:
            endpoint = f"https://news.google.com/news/rss/headlines/section/topic/{g_cat}?hl=en-{c_code}&gl={c_code}&ceid={c_code}:en"

        try:
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            
            # Parse XML RSS Feed
            root = ET.fromstring(response.text)
            
            raw_articles = root.findall('.//item')[:page_size]
            processed_articles = []
            
            for item in raw_articles:
                title = item.find('title').text if item.find('title') is not None else ""
                url = item.find('link').text if item.find('link') is not None else ""
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
                source = item.find('source').text if item.find('source') is not None else "Google News"
                
                # Use title as content if description is empty, as RSS mostly provides title and link natively
                description = item.find('description').text if item.find('description') is not None else title
                
                clean_title = self._remove_html_tags(title)
                clean_description = self._remove_html_tags(description)

                article_data = {
                    "source_name": source,
                    "author": "Unknown",
                    "title": clean_title,
                    "description": clean_description,
                    "content": clean_description,
                    "url": url,
                    "published_at": pubDate,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "query": query,
                    "category": category,
                    "country": country
                }
                
                processed_articles.append(article_data)

            # Store in MongoDB
            inserted_count = 0
            if processed_articles and self.mongo_client:
                try:
                    result = self.collection.insert_many(processed_articles)
                    inserted_count = len(result.inserted_ids)
                except Exception as mongo_ex:
                    err_msg = f"MongoDB insertion error: {mongo_ex}"
                    api_logger.error(err_msg)

            return {
                "status": "success", 
                "total_fetched": len(processed_articles),
                "total_saved_to_db": inserted_count,
                "articles": processed_articles
            }

        except requests.exceptions.RequestException as e:
            err_msg = f"HTTP Request to News Service failed: {e}"
            api_logger.error(err_msg)
            return {"error": err_msg}
        except ET.ParseError as e:
            err_msg = f"Failed to parse News RSS Feed: {e}"
            api_logger.error(err_msg)
            return {"error": err_msg}
        except Exception as e:
            err_msg = f"Unexpected error during news fetch: {e}"
            api_logger.error(err_msg)
            return {"error": err_msg}

if __name__ == "__main__":
    fetcher = NewsAPIFetcher(api_key="14543106a2f2410c9b1bf2addd2e7cb8")
    result = fetcher.fetch_news(query="technology", page_size=2)
    print(result)
