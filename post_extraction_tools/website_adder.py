import json
import time
import re
import os
from typing import Optional
from urllib.parse import urlparse
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

# with open("../data/uncleaned_companies.json", "r") as f:
#     companies = json.load(f).get("companies", [])
EXCLUDE_WORDS = {"inc.", "llc", "ltd", "corp", "corporation", "the"}

def clean_url(url: str) -> str:
    """Trim tracking and subpage paths to get the main domain."""
    try:
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        return domain
    except:
        return url
    
def extract_website_from_tables(soup: BeautifulSoup, comp_name) -> Optional[str]:
    """
    Finds the first website URL in an <a> tag within any table row (<tr>) 
    in the BeautifulSoup object.
    """
    tables = soup.find_all("table")
    def is_website_link(href: str) -> bool:
        href = href.lower()
        return href.startswith(("http://", "https://")) and not any(
            href.startswith(p) for p in ["#", "mailto:", "javascript:", "tel:"]
        )
    def company_name_exists() -> bool:
        temp_parts = comp_name.lower().split()
        comp_name_parts = [word for word in temp_parts if word not in EXCLUDE_WORDS]
        for w in comp_name_parts:
            if w in href.lower():
                return True
        return False

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            anchor_tags = row.find_all("a", href=True)
            for a_tag in anchor_tags:
                href = a_tag["href"]
                if is_website_link(href):
                    if company_name_exists():
                        return href
                    
    return None

def find_company_website(company_name, location=None, industry=None):
    query = f"{company_name} {location or ''} {industry or ''} official website"
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
    if not results:
        return None
    
    best_match = None
    best_score = 0

    for r in results:
        url = r.get("href") or r.get("url")
        if not url:
            continue
        cleaned = clean_url(url)
        domain = urlparse(cleaned).netloc.lower()
        score = 0
        name = company_name.lower().split()[0]

        if name in domain:
            score += 5
        if any(domain.endswith(tld) for tld in [".com", ".org", ".net", ".co", ".io"]):
            score += 2
        if any(domain.startswith(prefix) for prefix in ["support.", "careers.", "ir.", "blog.", "community.", "forum.", "media.", "news.", "docs.", "developer.", "help.", "about.", "ttlc.", "privacy.", "terms.",  "legal.", "events.", "partners.", "investors.", "research.", "customers.", "resources.", "contact.", "shop.", "store.", "login.", "app.", "apps.", "download.", "downloads.", "status.", "jobs.", "work.", "team.", "company.", "corporate."]):
            score -= 3
        if re.search(r"/(drivers|about|news|products|careers|support)", url, re.IGNORECASE):
            score -= 2

        if score > best_score:
            best_score = score
            best_match = cleaned
        
    return best_match

def find_all_company_websites(companies):
    for c in companies:
        if not c.get("website_url"):
            print(f"Searching for {c['company_name']}...")
            temp_url = find_company_website(
                c["company_name"],
                location=c.get("location"),
                industry=c.get("industry_type")
            )
            
            temp_parts = c["company_name"].lower().split()
            comp_name_parts = [word for word in temp_parts if word not in EXCLUDE_WORDS]
            len_thres = int(len(comp_name_parts)/2)
            count = 0
            if temp_url:
                for p in comp_name_parts:
                    if p in temp_url.lower():
                        count += 1
            if count >= len_thres:
                c["website_url"] = temp_url
                print(f"Found website via DDG: {c['website_url']}")
            else:
                c["website_url"] = None
                print(f"No suitable website found via DDG for {c['company_name']}")
            time.sleep(2)
    return companies

# with open("../data/companies_with_urls.json", "r") as f:
#     companies = json.load(f)

def check_percent_with_urls(companies):
    percent_with_urls = sum(1 for c in companies if c.get("website_url")) / len(companies) * 100
    return percent_with_urls

def wiki_search_mode(companies):
    percent_with_urls = check_percent_with_urls(companies)
    if percent_with_urls < 100:
        print("Less than 100% of companies have website URLs. Going to wikisearch mode...")

        for c in companies:
            if not c.get("website_url"):
                print(f"Wikisearching for {c['company_name']}...")
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/123.0 Safari/537.36"
                    )
                }
                if("(" in c["company_name"]):
                    mod_comp_name = c["company_name"].split("(")[0].strip()
                    wiki_url = f"https://en.wikipedia.org/wiki/{mod_comp_name.replace(' ', '_')}"
                else:
                    mod_comp_name = c["company_name"]
                    # print(mod_comp_name.replace(' ', '_'))
                    wiki_url = f"https://en.wikipedia.org/wiki/{mod_comp_name.replace(' ', '_')}"
                try:
                    res = requests.get(wiki_url, headers=headers, timeout=10)
                    res.raise_for_status()
                    soup = BeautifulSoup(res.text, 'html.parser')
                    website_url = extract_website_from_tables(soup, mod_comp_name)
                    if website_url:
                        c["website_url"] = clean_url(website_url)
                        print(f"Found website via Wikipedia: {c['website_url']}")
                    else:
                        print(f"No website found on Wikipedia for {c['company_name']}")
                except Exception as e:
                    print(f"Error accessing Wikipedia for {c['company_name']}: {str(e)}")
                    continue

                time.sleep(5)
    else:
        print("All companies already have website URLs. Skipping wikisearch mode...")
    print("Saving results...")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(root_dir, "..", "data")
    os.makedirs(data_folder, exist_ok=True)

    file_path = os.path.join(data_folder, "all_cleaned_companies.json")

    with open(file_path, "w") as f:
        json.dump({"companies": companies}, f, indent=2)
    print("Enriched company list saved to all_cleaned_companies.json")
    return {"companies": companies}


# with open("../data/uncleaned_companies.json", "r") as f:
#     companies = json.load(f).get("companies", [])
# intermediate_data = find_all_company_websites(companies)
# final_data = wiki_search_mode(intermediate_data)