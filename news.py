from datetime import datetime, timedelta, timezone

from gnews import GNews
from crewai.tools import tool


def fetch_latest_news(
    category: str,
    max_results: int = 5,
    period: str = "1d",
    keyword: str = "",
) -> list[dict]:
    """Fetch recent Google News articles for a category and optional keyword."""
    if period == "today":
        today = datetime.now().astimezone().date()
        tomorrow = today + timedelta(days=1)
        google_news = GNews(
            language="en",
            country="PK",
            max_results=max_results,
            start_date=(today.year, today.month, today.day),
            end_date=(tomorrow.year, tomorrow.month, tomorrow.day),
        )
    else:
        google_news = GNews(
            language="en",
            country="PK",
            period=period,
            max_results=max_results,
        )
    query = f"{category} {keyword}".strip()
    articles = google_news.get_news(query)
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return [
        {
            "title": article.get("title", "")[:200],
            "description": article.get("description", "")[:500],
            "url": article.get("url", ""),
            "published": article.get("published date", ""),
            "publisher": (article.get("publisher") or {}).get("title", ""),
            "fetched_at": fetched_at,
        }
        for article in articles
    ]


@tool("Fetch News")
def news_tool(category: str):
    """Fetch recent Google News articles for a category."""
    return fetch_latest_news(category)
