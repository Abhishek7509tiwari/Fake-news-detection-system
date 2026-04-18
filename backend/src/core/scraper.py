import requests
from bs4 import BeautifulSoup
try:
    from newspaper import Article
except ImportError:
    Article = None

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def scrape_url(self, url):
        """
        Scrapes content from a given URL.
        Tries newspaper3k first, then falls back to BeautifulSoup.
        """
        data = {
            "title": "",
            "text": "",
            "error": None
        }

        # Method 1: Newspaper3k
        if Article:
            try:
                article = Article(url)
                article.download()
                article.parse()
                data["title"] = article.title
                data["text"] = article.text
                if data["text"]:
                    return data
            except Exception as e:
                print(f"Newspaper3k failed: {e}")

        # Method 2: BeautifulSoup Fallback
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the main article title
            title_tag = soup.find('h1')
            if title_tag:
                data["title"] = title_tag.get_text().strip()
            
            # Try to find the main article content
            # This is heuristic and might need adjustment for specific sites
            paragraphs = soup.find_all('p')
            text_content = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50] # Filter short paragraphs
            data["text"] = "\n".join(text_content)
            
            if not data["text"]:
                 data["error"] = "Could not extract text content."

        except Exception as e:
            data["error"] = f"Scraping failed: {str(e)}"

        return data

if __name__ == "__main__":
    # Test
    scraper = NewsScraper()
    url = "https://www.bbc.com/news/world-us-canada-68213642" # Example URL (might change)
    # print(scraper.scrape_url(url))
