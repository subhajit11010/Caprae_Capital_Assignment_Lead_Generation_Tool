from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import tool
from bs4 import BeautifulSoup
from langchain.agents import initialize_agent, AgentType
from services.llm_client import LLMClient
import requests, json

# creating the parametrix search tool
class ParametricSearch:
    def __init__(self, llm):
        self.llm = llm
        self.ddgsearch = DuckDuckGoSearchResults()
        self.tools = [self.parametric_search, self.ddgsearch]
        self.agent = initialize_agent(self.tools, self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
        
    @tool
    def parametric_search(url: str) -> str:
        """Scrape visible text content from a company webpage."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        }
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()
            text = soup.get_text(separator="\n", strip=True)
            return text[:5000]
        except Exception as e:
            return f"Error scraping the URL {url}: {str(e)}"
    