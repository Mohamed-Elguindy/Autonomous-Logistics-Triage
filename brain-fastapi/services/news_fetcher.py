import httpx
import os
import asyncio # New import for concurrency if needed
from dotenv import load_dotenv
load_dotenv()
import feedparser
import urllib.parse
import logging
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_URL = "https://newsapi.org/v2/everything"

RISK_KEYWORDS = [
    "port strike",
    "port closure",
    "port congestion",
    "typhoon",
    "hurricane",
    "cyclone",
    "tropical storm",
    "canal blocked",
    "ship grounded",
    "maritime accident",
    "customs delay",
    "border closure",
    "piracy attack",
    "flooding port",
    "terminal shutdown",
]

async def fetch_news(keyword: str, page_size: int = 5) -> list[dict]:
    params = {
        "q": keyword,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "searchIn": "title,description",
        "apiKey": NEWSAPI_KEY,
    }

    # Use AsyncClient for non-blocking calls
    async with httpx.AsyncClient() as client:
        response = await client.get(NEWSAPI_URL, params=params)

    if response.status_code != 200:
        print(f"[NewsAPI Error] Status: {response.status_code} | {response.text}")
        return []

    data = response.json()
    articles = data.get("articles", [])

    return [{
        "title": a.get("title", ""),
        "description": a.get("description", ""),
        "content": a.get("content", ""),
        "published_at": a.get("publishedAt", ""),
        "source": a.get("source", {}).get("name", ""),
    } for a in articles]
""""
async def fetch_risk_news_for_region(region: str) -> list[dict]:
    all_articles = []

    # Loop through keywords and await the results
    for keyword in RISK_KEYWORDS:
        query = f"{keyword} {region}"
        articles = await fetch_news(query, page_size=3)
        all_articles.extend(articles)

    # Deduplicate by title
    seen = set()
    unique_articles = []
    for article in all_articles:
        if article["title"] not in seen:
            seen.add(article["title"])
            unique_articles.append(article)

    return unique_articles
"""
"""
async def fetch_risk_news_for_region(region: str) -> list[dict]:
    """
"""
    Temporary Mock News to bypass NewsAPI Rate Limits.
    Returns data in the exact format your agent expects.
    """
"""
    print(f"🏗️ Using MOCK news for region: {region}")
    
    # These mock articles are designed to look like real logistics risks
    mock_database = [
        {
            "title": f"Major Port Strike in {region} threatens supply chains",
            "description": "Port workers have announced a 48-hour walkout starting tomorrow, halting all container traffic.",
            "url": "https://example.com/news/1",
            "source": "Logistics Insider"
        },
        {
            "title": f"Severe flooding reported near {region} highways",
            "description": "Record-breaking rainfall has caused multiple road closures on major transit routes.",
            "url": "https://example.com/news/2",
            "source": "Weather Daily"
        },
        {
            "title": "Global Shipping Rates Spike",
            "description": "General news about shipping costs that shouldn't necessarily trigger a high-severity alert.",
            "url": "https://example.com/news/3",
            "source": "Business Weekly"
        }
    ]
    
    # Return the list to keep the async gather working
    return mock_database



async def fetch_risk_news_for_region(region: str) -> list[dict]:
    articles = []
    with DDGS() as ddgs:
        # 'news' is a specific method in the DDGS library
        results = ddgs.news(f"{region} logistics shipping risk", max_results=5)
        for r in results:
            articles.append({
                "title": r['title'],
                "description": r['body'],
                "url": r['url'],
                "source": r['source']
            })
    return articles
"""


logger = logging.getLogger(__name__)

# =====================================================================
# OLD GOOGLE RSS IMPLEMENTATION (COMMENTED OUT)
# =====================================================================
# async def fetch_risk_news_for_region(region: str) -> list[dict]:
#     """
#     Fetches news using Google News RSS. 
#     Highly stable, free, and bypasses most 'DecodeError' or 'RateLimit' issues.
#     """
#     articles = []
#     try:
#         # 1. Clean and encode the query
#         query = urllib.parse.quote(f"{region} logistics shipping risk")
#         # ceid=US:en tells Google to give us US/English results
#         rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
#         
#         # 2. Parse the RSS feed (This is a lightweight XML fetch)
#         feed = feedparser.parse(rss_url)
#         
#         for entry in feed.entries[:5]: # Take top 5
#             articles.append({
#                 "title": entry.get('title', 'No Title'),
#                 "description": entry.get('summary', 'No description'),
#                 "url": entry.get('link', '#'),
#                 "source": entry.get('source', {}).get('title', 'Google News')
#             })
#             
#     except Exception as e:
#         logger.error(f"⚠️ Google RSS Fetch failed for {region}: {e}")
#         return [] # Return empty list so the Agent doesn't crash
# 
#     return articles


# =====================================================================
# NEW TAVILY IMPLEMENTATION
# =====================================================================
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

async def fetch_risk_news_for_region(region: str) -> list[dict]:
    """
    Fetches real-time logistics and shipping risk news using the Tavily API.
    Specifically uses the 'news' topic to ensure high-quality recent events.
    """
    if not TAVILY_API_KEY:
        logger.error("⚠️ TAVILY_API_KEY is missing from environment variables.")
        return []

    articles = []
    query = f"latest shipping logistics supply chain risks, port strikes, or natural disasters in {region}"
    
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced", 
        "topic": "news",            
        "days": 7,                  
        "max_results": 5,
        "include_raw_content": False
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post("https://api.tavily.com/search", json=payload)
            response.raise_for_status() 
            data = response.json()
            
            results = data.get("results", [])
            
            if not results:
                logger.warning(f"⚠️ Tavily returned 0 news articles for region: {region}")
                return []

            for r in results:
                # Extract the domain name to use as the "source"
                raw_url = r.get('url', '')
                source_domain = raw_url.split('/')[2] if '//' in raw_url else 'Tavily Search'

                articles.append({
                    "title": r.get('title', 'No Title'),
                    "description": r.get('content', 'No description'), 
                    "url": raw_url,
                    "source": source_domain
                })
                
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ [ERROR] Tavily API HTTP Error for {region}: Status {e.response.status_code} | {e.response.text}")
    except Exception as e:
        logger.error(f"❌ [ERROR] Tavily fetch failed for {region}: {e}")

    return articles

# ---- Manual test, run this file directly to explore the data ----
if __name__ == "__main__":
    async def run_tests():
        print("=" * 60)
        print("TEST 1: Single keyword search")
        print("=" * 60)
        articles = await fetch_news("port strike", page_size=3)
        for i, a in enumerate(articles):
            print(f"\n--- Article {i+1} ---")
            print(f"Source:      {a['source']}")
            print(f"Published:   {a['published_at']}")
            print(f"Title:       {a['title']}")
            print(f"Description: {a['description']}")
            print(f"Content:     {a['content'][:200] if a['content'] else 'N/A'}...")

        print("\n")
        print("=" * 60)
        print("TEST 2: Region-based risk search (Tokyo)")
        print("=" * 60)
        regional_articles = await fetch_risk_news_for_region("Tokyo")
        print(f"\nTotal unique articles found: {len(regional_articles)}")
        for i, a in enumerate(regional_articles[:5]):
            print(f"\n--- Article {i+1} ---")
            print(f"Source:      {a['source']}")
            print(f"Title:       {a['title']}")
            print(f"Description: {a['description']}")

    asyncio.run(run_tests())