import requests
from bs4 import BeautifulSoup
from config import logger
import urllib.parse
import time

def search_google(query):
    """
    Performs a simple Google search to find information without an API key.
    Note: Can be blocked if done too frequently.
    """
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title = g.find('h3').text if g.find('h3') else "No Title"
                # snippet = g.find('div', {'style': '-webkit-line-clamp:2'}).text if g.find('div', {'style': '-webkit-line-clamp:2'}) else ""
                results.append({"title": title, "link": link})
        return results
    except Exception as e:
        logger.error(f"Google search failed for query '{query}': {e}")
        return []

def enrich_founders(startup_name, founders_list):
    """
    Enrich founder details without failing the workflow.
    """
    enriched_founders = []
    for founder in founders_list:
        logger.info(f"Enriching founder: {founder} of {startup_name}")
        query = f"{founder} {startup_name} founder LinkedIn"
        search_results = search_google(query)
        
        linkedin_url = ""
        title = "Founder / Co-Founder" # Default fallback
        
        # Priority: Extract from Google search results
        for res in search_results:
            if "linkedin.com/in/" in res["link"]:
                linkedin_url = res["link"]
                # Attempt to extract title from the search title e.g. "John Doe - CEO - StartupName"
                parts = res["title"].split("-")
                if len(parts) > 1:
                    title = parts[1].strip()
                break
                
        enriched_founders.append({
            "name": founder,
            "title": title,
            "linkedin_url": linkedin_url
        })
        time.sleep(2) # Prevent rate limiting
        
    return enriched_founders

if __name__ == "__main__":
    print(enrich_founders("Zepto", ["Aadit Palicha", "Kaivalya Vohra"]))
