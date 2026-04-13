import httpx
import os
import asyncio # New import for concurrency if needed
from dotenv import load_dotenv

load_dotenv()

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