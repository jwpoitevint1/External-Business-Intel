import httpx
from bs4 import BeautifulSoup


def fetch_google_news(query: str):
    url = f"https://news.google.com/search?q={query}"
    results = []

    with httpx.Client() as client:
        resp = client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select("article")[:10]:
            text = item.get_text(separator=" ")
            results.append(text)

    return results


def fetch_reddit(query: str):
    url = f"https://www.reddit.com/search.json?q={query}"
    headers = {"User-Agent": "intel-agent"}
    results = []

    with httpx.Client() as client:
        resp = client.get(url, headers=headers)
        data = resp.json()

        for post in data.get("data", {}).get("children", []):
            results.append(post["data"].get("title", ""))

    return results
