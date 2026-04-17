import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.news_api_fetcher import NewsAPIFetcher
import pprint

fetcher = NewsAPIFetcher()
res = fetcher.fetch_news(category="health", country="in", page_size=5)
pprint.pprint(res)
