# AI News Assistant

AI News Assistant retrieves recent articles for a selected category and creates a short digest with two CrewAI agents. The News Analyst identifies points supported by the fetched articles. The Digest Editor turns those notes into headlines and a summary. Article titles, publishers, publication times, and links come from the fetched records.

## Group Members

| Name | Roll No. |
| --- | ---: |
| Nazish Parvin | 5 |
| Sahar Khalil | 103 |
| Munaza Bibi | 114 |

**Session:** 2022–2026

## Categories

- Business
- Sports
- Politics
- Entertainment

The app requests up to ten articles from Google News for the selected category, keyword, and time range. Google News may return the same headlines again when those remain the most recent available stories. The app does not continuously stream news in the background.

## Added user features

- Search within a selected category with a keyword; press Enter or select **Search news** to run it. Typing one of the four category names selects that category directly.
- Choose news from today, the last 24 hours, or the last 7 days.
- Choose 3, 5, or 10 source articles.
- Refresh the current category and filters.
- Copy the generated summary.
- Save articles in browser storage on the current device and reopen their sources later.

## Screenshot plan

These are distinct, real app states suitable for project documentation. Select the filters first, then click a category. Wait for the loading indicator to finish before capturing.

1. Home page before choosing a category.
2. Business results with default filters.
3. Sports results with default filters.
4. Politics results with default filters.
5. Entertainment results with default filters.
6. Search box filled with `sports`, then press Enter to open Sports results.
7. Business results searched with the keyword `Pakistan`.
8. Politics results searched with the keyword `elections`.
9. Sports results searched with the keyword `cricket`.
10. Business results for today with 3 articles.
11. Business results for the last 24 hours with 5 articles.
12. Sports results for the last 7 days with 10 articles.
13. Entertainment results for the last 7 days with 3 articles.
14. A result after saving an article and the saved articles panel.
15. A result after using **Copy summary** or **Refresh news**.

If a keyword returns no articles, try another current keyword. The search and time-window options depend on the availability of recent Google News stories.

## Run on Windows

Open the project folder in Visual Studio Code. From the menu, choose **Terminal → New Terminal**. Check that the terminal path ends with `AI_NEWS_ASSISTANT` before entering these commands.

Activate the project's existing virtual environment (the extensionless command works in PowerShell):

```powershell
   .\venv\Scripts\Activate
```

If PowerShell says script execution is blocked, allow scripts only in that terminal window, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Install the listed packages if this is the first run or dependencies have changed:

```powershell
pip install -r requirements.txt
```

Make sure the `.env` file in this project folder contains your own Groq key. Do not share the key or paste it into a screenshot:

```text
GROQ_API_KEY=your_groq_api_key
```

Start the website:

```powershell
uvicorn backend.main:app --reload
```

Keep this terminal open while using the site. In Chrome, open `http://127.0.0.1:8000` and select a news category. The first response can take a little time because the app fetches articles and calls the two AI agents.

To stop the server, click inside the same terminal where the server messages are appearing, then press **Ctrl+C once**. You do not need to hold it down. Close that terminal only after the server has stopped.

## How the request works

1. The browser sends the selected category to FastAPI.
2. The app asks Google News for up to five articles from the last 24 hours.
3. The News Analyst reviews those article records and extracts supported points.
4. The Digest Editor uses the analyst's notes to prepare headlines and a summary.
5. The page shows the digest and source links, publisher names, and publication times.

## Stack and layout

- Python, FastAPI, Jinja2, and Uvicorn
- CrewAI with two sequential agents
- Groq-hosted `openai/gpt-oss-20b` model through LiteLLM
- GNews package for article retrieval
- HTMX, Tailwind CSS, and Inter font in the browser

```text
backend/
  main.py                 Web routes and safe result rendering
  core/engine.py          Recent fetch and two-agent workflow
  agents/factory.py       News Analyst and Digest Editor
  tasks/factory.py        Sequential analysis and digest tasks
  tools/news.py           Last-24-hours Google News retrieval
frontend/templates/
  index.html              Home page and category controls
```

## Notes

- Internet access is required for Google News, Groq, and the frontend CDN assets.
- Summary accuracy depends on the fetched source descriptions and the language model. Open source links to read the complete reporting.
- The project is a prototype. It does not store a news archive, continuously monitor feeds, or independently fact-check articles.
