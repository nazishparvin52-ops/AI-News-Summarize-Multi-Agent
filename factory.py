from crewai import Task


def create_news_tasks(category, analyst, editor):
    source_records = "{article_records}"

    analysis_task = Task(
        description=(
            f"Review the recent {category} news records below. Identify the "
            "main points and any common theme. Use only the records provided. "
            "Do not invent facts, dates, sources, or events.\n\n"
            f"ARTICLE RECORDS (JSON):\n{source_records}"
        ),
        agent=analyst,
        expected_output="Brief fact-grounded analyst notes about the supplied articles.",
    )

    digest_task = Task(
        description=(
            f"Create a reader-friendly {category} news digest from the analyst "
            "notes in the prior task context. "
            "Use this exact structure:\n\n"
            "HEADLINES:\n- one bullet for each available article\n\n"
            "SUMMARY:\nOne concise paragraph based only on the records.\n\n"
            "Do not create an ARTICLES section. The application displays the "
            "original source records separately.\n\n"
            "If there are no records, say so clearly. Do not fabricate stories "
            "or claim that an article is newer than the supplied published date."
        ),
        agent=editor,
        context=[analysis_task],
        expected_output="HEADLINES and SUMMARY in the requested format.",
    )
    return analysis_task, digest_task
