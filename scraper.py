import requests
from bs4 import BeautifulSoup
from config import RSS_FEEDS, logger
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, timedelta, timezone

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.content

def parse_rss_feed(feed_url):
    articles = []
    try:
        logger.info(f"Fetching RSS feed: {feed_url}")
        content = fetch_url(feed_url)
        soup = BeautifulSoup(content, 'lxml-xml')
        
        items = soup.find_all('item')
        if not items:
            items = soup.find_all('entry') # Atom fallback

        # 24 hours ago
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)

        for item in items:
            title = item.title.text if item.title else "No Title"
            link = item.link.text if item.link else (item.find('link')['href'] if item.find('link') else "")
            
            # Get content (try content:encoded first, then description, then summary)
            content_tag = item.find('content:encoded')
            if not content_tag:
                content_tag = item.find('description')
            if not content_tag:
                content_tag = item.find('summary')
            
            text_content = ""
            if content_tag:
                # Clean HTML tags
                text_content = BeautifulSoup(content_tag.text, 'html.parser').get_text(separator=' ', strip=True)

            # Date parsing
            pub_date_str = item.pubDate.text if item.pubDate else (item.published.text if item.find('published') else "")
            
            # Simple check if article is within last 24h is complex due to various date formats.
            # We will rely on history.csv to deduplicate later, but we grab recent items.
            
            if link:
                articles.append({
                    "title": title,
                    "url": link,
                    "content": text_content,
                    "published_date": pub_date_str,
                    "source": feed_url
                })
        
        logger.info(f"Found {len(articles)} articles in {feed_url}")
    except Exception as e:
        logger.error(f"Error parsing RSS feed {feed_url}: {e}")
    
    return articles

def scrape_articles():
    all_articles = []
    for feed in RSS_FEEDS:
        articles = parse_rss_feed(feed)
        all_articles.extend(articles)
    
    # Remove duplicates based on URL
    unique_articles = {article['url']: article for article in all_articles if article['url']}
    logger.info(f"Total unique articles fetched: {len(unique_articles)}")
    return list(unique_articles.values())

if __name__ == "__main__":
    # Test scraping
    articles = scrape_articles()
    for a in articles[:3]:
        print(a['title'], a['url'])
