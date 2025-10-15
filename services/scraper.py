# import requests
# from bs4 import BeautifulSoup   
# from requests_html import HTMLSession
# import asyncio
import subprocess
import json
import os
import sys

# def scrape_website(url: str) -> str:
#         """Scrape visible text content from a company webpage."""
#         headers = {
#             "User-Agent": (
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/123.0.0.0 Safari/537.36"
#             ),
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#             "Accept-Language": "en-US,en;q=0.9",
#             "Accept-Encoding": "gzip, deflate, br",
#             "Connection": "keep-alive",
#             "Upgrade-Insecure-Requests": "1",
#             "Sec-Fetch-Dest": "document",
#             "Sec-Fetch-Mode": "navigate",
#             "Sec-Fetch-Site": "none",
#             "Sec-Fetch-User": "?1",
#         }
#         try:
#             res = requests.get(url, headers=headers, timeout=10)
#             res.raise_for_status()
#             soup = BeautifulSoup(res.text, 'html.parser')
#             for tag in soup(["script", "style", "noscript"]):
#                 tag.extract()
#             text = soup.get_text(separator="\n", strip=True)
#             return text[:5000]
#         except Exception as e:
#             return f"Error scraping the URL {url}: {str(e)}"

def scrape_website(url: str) -> str:
    """
    Calls scrape_worker.py as a subprocess to safely scrape a URL.
    This avoids async and event loop conflicts in Streamlit.
    """
    worker_path = os.path.join(os.path.dirname(__file__), "scrape_worker.py")
    try:
        result = subprocess.run(
            [sys.executable, worker_path, url],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            return f"Error scraping the URL {url}: {result.stderr.strip()}"
        
        output = json.loads(result.stdout)
        return output.get("text", "")
    except subprocess.TimeoutExpired:
        return f"Error scraping the URL {url}: Timeout"
    except Exception as e:
        return f"Error scraping the URL {url}: {e}"