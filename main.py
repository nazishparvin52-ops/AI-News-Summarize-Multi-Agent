from datetime import datetime
from html import escape
import logging
from urllib.parse import urlencode, urlparse
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.core.engine import run_news_engine

app = FastAPI()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="frontend/templates")
ALLOWED_CATEGORIES = {"business", "sports", "politics", "entertainment"}


def parse_news(text: str):
    def extract(section):
        match = re.search(
            rf"(?is)(?:\*\*)?{section}(?:\*\*)?\s*:(?:\*\*)?\s*(.*?)(?=\n\s*(?:\*\*)?(?:HEADLINES|SUMMARY|ARTICLES)(?:\*\*)?\s*:(?:\*\*)?|$)",
            text,
        )
        return match.group(1).strip() if match else ""

    return extract("HEADLINES"), extract("SUMMARY")


def format_list(text):
    items = []
    for line in text.splitlines():
        line = line.strip().lstrip("-• ").strip()
        if line:
            items.append(f"<li>{escape(line)}</li>")
    return "".join(items) or "<li>No headlines were generated for these articles.</li>"


def article_cards(articles):
    cards = []
    for article in articles:
        title = escape(article.get("title") or "Untitled article")
        description = escape(article.get("description") or "Description unavailable.")
        publisher = escape(article.get("publisher") or "Publisher unavailable")
        published = escape(article.get("published") or "Date unavailable")
        raw_url = article.get("url", "")
        parsed = urlparse(raw_url)
        valid_url = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        if not valid_url:
            link = ""
        else:
            link = f'<a class="text-blue-300 underline" href="{escape(raw_url, quote=True)}" target="_blank" rel="noopener noreferrer">Open source</a>'
        save_button = (
            f'<button type="button" class="mt-3 rounded-lg border border-blue-400/30 px-3 py-1 text-sm text-blue-200 hover:bg-blue-500/10" '
            f'data-save-article data-title="{escape(article.get("title") or "Untitled article", quote=True)}" '
            f'data-url="{escape(raw_url, quote=True)}" data-publisher="{escape(article.get("publisher") or "Publisher unavailable", quote=True)}">☆ Save article</button>'
        ) if valid_url else ""
        cards.append(
            f'<article class="rounded-xl border border-white/10 bg-slate-950/60 p-4">'
            f'<h3 class="font-semibold">{title}</h3>'
            f'<p class="article-description mt-2 text-slate-300">{description}</p>'
            f'<p class="mt-3 text-sm text-slate-400">{publisher} · {published}</p>'
            f'<div class="mt-2">{link}</div>{save_button}</article>'
        )
    return "".join(cards) or '<p class="text-slate-300">No recent articles were found in the last 24 hours.</p>'


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/news", response_class=HTMLResponse)
def get_news(category: str, keyword: str = "", period: str = "today", count: int = 5):
    category = category.strip().lower()
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=400, detail="Choose one of the available news categories.")
    keyword = keyword.strip()[:80]
    if period not in {"today", "1d", "7d"}:
        raise HTTPException(status_code=400, detail="Choose Today, the last 24 hours, or the last 7 days.")
    if count not in {3, 5, 10}:
        raise HTTPException(status_code=400, detail="Choose 3, 5, or 10 articles.")
    refresh_params = urlencode({"category": category, "keyword": keyword, "period": period, "count": count})
    try:
        result, articles = run_news_engine(category, keyword, period, count)
    except Exception:
        logger.exception("News refresh failed for category %s", category)
        return HTMLResponse(
            '<div class="rounded-2xl border border-rose-400/30 bg-rose-950/40 p-6">'
            '<h2 class="text-xl font-bold text-rose-300">News could not refresh right now</h2>'
            '<p class="mt-3 text-slate-200">The news provider may be temporarily busy. Wait a few seconds and try again.</p>'
            f'<button type="button" hx-get="/news?{escape(refresh_params, quote=True)}" hx-target="#news-container" hx-swap="innerHTML" hx-indicator="#loader" class="mt-4 rounded-lg border border-white/20 px-4 py-2 hover:bg-white/10">Try again</button>'
            '</div>',
            status_code=503,
        )

    headlines, summary = parse_news(result)
    fetched_at = articles[0].get("fetched_at") if articles else ""
    try:
        fetched_display = datetime.fromisoformat(fetched_at).astimezone().strftime("%d %b %Y, %I:%M %p") if fetched_at else "Not available"
    except ValueError:
        fetched_display = "Not available"
    fallback_notice = (
        '<div class="rounded-xl border border-amber-300/30 bg-amber-950/30 p-4 text-amber-100">'
        'AI summary is temporarily unavailable. This brief uses the fetched article descriptions.'
        '</div>'
        if "NOTICE:" in result else ""
    )
    return f"""
    <div class="space-y-6">
        {fallback_notice}
        <div class="flex flex-wrap items-center justify-between gap-3">
            <p class="text-sm text-slate-400">Google News · {len(articles)} articles · Fetched {escape(fetched_display)}</p>
            <div class="flex gap-2">
                <button type="button" hx-get="/news?{escape(refresh_params, quote=True)}" hx-target="#news-container" hx-swap="innerHTML" hx-indicator="#loader" class="rounded-lg border border-white/15 px-4 py-2 text-sm hover:bg-white/10">↻ Refresh news</button>
            </div>
        </div>
        <section class="bg-slate-900 p-6 rounded-2xl">
            <h2 class="text-xl font-bold text-blue-400">📌 Headlines</h2>
            <ul class="list-disc pl-6 mt-3 space-y-1">{format_list(headlines)}</ul>
        </section>
        <section class="bg-slate-900 p-6 rounded-2xl">
            <h2 class="text-xl font-bold text-green-400">🧠 Summary</h2>
            <p id="news-summary" class="mt-3 text-slate-300 leading-relaxed">{escape(summary or 'No summary was returned.')}</p>
            <button type="button" data-copy-summary class="mt-4 rounded-lg border border-emerald-400/30 px-3 py-1 text-sm text-emerald-200 hover:bg-emerald-500/10">Copy summary</button>
        </section>
        <section class="bg-slate-900 p-6 rounded-2xl">
            <h2 class="text-xl font-bold text-purple-400">📰 Source articles</h2>
            <div class="mt-4 space-y-3">{article_cards(articles)}</div>
        </section>
    </div>
    """
