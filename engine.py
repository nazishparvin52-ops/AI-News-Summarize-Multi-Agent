import json
import logging

from crewai import Crew, Process

from backend.agents.factory import create_digest_editor, create_news_analyst
from backend.tasks.factory import create_news_tasks
from backend.tools.news import fetch_latest_news

logger = logging.getLogger(__name__)


def source_based_fallback(articles):
    """Keep usable, clearly labeled results when the model provider is busy."""
    headlines = "\n".join(f"- {item.get('title') or 'Untitled article'}" for item in articles)
    descriptions = []
    for item in articles:
        text = (item.get("description") or "").strip()
        if text and text not in descriptions:
            descriptions.append(text)
    if descriptions:
        summary = " ".join(descriptions[:3])
        summary = summary[:1200].rsplit(" ", 1)[0] if len(summary) > 1200 else summary
    else:
        summary = "Google News returned article headlines, but no descriptions. Open the source articles for details."
    return (
        "NOTICE: The AI provider did not answer this time. This brief uses only the fetched Google News descriptions.\n\n"
        f"HEADLINES:\n{headlines}\n\nSUMMARY:\n{summary}"
    )


def run_news_engine(category, query=None, period="1d", count=5):
    """Fetch recent source data, then analyze and edit it with two agents."""
    articles = fetch_latest_news(category, max_results=count, period=period, keyword=query or "")
    if not articles:
        return "HEADLINES:\n\nSUMMARY:\nNo recent articles were returned.\n\nARTICLES:", articles

    analyst = create_news_analyst()
    editor = create_digest_editor()
    analysis_task, digest_task = create_news_tasks(category, analyst, editor)

    crew = Crew(
        agents=[analyst, editor],
        tasks=[analysis_task, digest_task],
        process=Process.sequential,
        verbose=False,
    )
    try:
        result = crew.kickoff(inputs={"article_records": json.dumps(articles, ensure_ascii=False)})
        return str(result), articles
    except Exception:
        logger.exception("CrewAI/Groq digest failed for category %s", category)
        return source_based_fallback(articles), articles
