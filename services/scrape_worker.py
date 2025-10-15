import sys
import json
from requests_html import HTMLSession

def scrape_website(url: str) -> str:
    session = HTMLSession()
    try:
        res = session.get(url, timeout=15)
        res.html.render(timeout=20)
        text = " ".join(res.html.text.split())
        return text[:8000]
    except Exception as e:
        return f"Error scraping the URL {url}: {e}"
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No URL provided"}))
        sys.exit(1)
    
    url = sys.argv[1]
    result = scrape_website(url)
    print(json.dumps({"text": result}))
