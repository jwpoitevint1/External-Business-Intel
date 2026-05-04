from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup


REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 ExternalBusinessIntel/1.0"}


def fetch_google_news(query: str):
    url = f"https://news.google.com/search?q={quote_plus(query)}"
    results = []

    try:
        with httpx.Client(headers=REQUEST_HEADERS, timeout=20, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for item in soup.select("article")[:10]:
                text = item.get_text(separator=" ", strip=True)
                if text:
                    results.append(text)
    except Exception as exc:
        results.append(f"google_news_ingestion_error: {type(exc).__name__}")

    return results


def fetch_reddit(query: str):
    url = f"https://www.reddit.com/search.json?q={quote_plus(query)}"
    results = []

    try:
        with httpx.Client(headers=REQUEST_HEADERS, timeout=20, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()

            for post in data.get("data", {}).get("children", [])[:10]:
                title = post.get("data", {}).get("title", "")
                if title:
                    results.append(title)
    except Exception as exc:
        results.append(f"reddit_ingestion_error: {type(exc).__name__}")

    return results
