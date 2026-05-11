"""
fetch_byline.py
---------------
Pass 2 — Search Trove for articles bylined 'Keith Dunstan' in The Bulletin.

This pass catches articles where Keith wrote under his real name rather than
the 'Batman' pen name. Results will overlap with fetch_batman.py — run
deduplicate.py after both passes to merge and remove duplicates.

Usage:
    python fetch_byline.py

Output:
    trove/output/<slug>.md for each new article found
    trove/output/fetch_byline_results.csv  (log of all results)
"""

import os
import re
import csv
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TROVE_API_KEY")
if not API_KEY:
    raise SystemExit("ERROR: TROVE_API_KEY not set. Copy .env.example to .env and add your key.")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATE_FROM = "1950-01-01"   # wider range for byline search — he may predate Batman column
DATE_TO   = "1984-12-31"

BASE_URL = "https://api.trove.nla.gov.au/v3/result"

SEARCH_TERMS = [
    "Keith Dunstan",
]

PARAMS_BASE = {
    "key": API_KEY,
    "category": "magazine",
    "encoding": "json",
    "bulkHarvest": "true",
    "l-title": "The Bulletin",
    "l-artType": "article",
    "include": "articleText",
    "n": 100,
}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[''']", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80]


def parse_date(date_str):
    if not date_str:
        return ""
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(date_str[:len(fmt.replace("%Y", "0000").replace("%m", "00").replace("%d", "00"))], fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str[:10]


def build_markdown(article):
    title = article.get("title", "Untitled").strip()
    date  = parse_date(article.get("date", ""))
    url   = article.get("troveUrl", "") or f"https://nla.gov.au/{article.get('id', '')}"
    text  = ""

    article_text_obj = article.get("articleText")
    if isinstance(article_text_obj, dict):
        text = article_text_obj.get("value", "")
    elif isinstance(article_text_obj, str):
        text = article_text_obj

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    issue_date = date or "unknown date"

    md = f"""---
title: "{title}"
date: {date}
summary: "[Review and complete — article retrieved from Trove]"
categories:
  - The Bulletin
tags: []
---

{text if text else "[Article text not available via API — visit Trove link below to transcribe manually]"}

<hr>

*Source: [{title}]({url}), The Bulletin, {issue_date}. Retrieved via the National Library of Australia's Trove database.*
"""
    return md.strip()


def fetch_articles(search_term):
    articles = []
    params = dict(PARAMS_BASE)
    params["q"] = f'"{search_term}" date:[{DATE_FROM} TO {DATE_TO}]'
    params["s"] = "*"

    page = 1
    while True:
        print(f"  Fetching page {page} for: {search_term!r}")
        try:
            resp = requests.get(BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  ERROR: {e}")
            break

        data = resp.json()
        results = data.get("category", [{}])[0].get("records", {})
        items = results.get("article", [])

        if not items:
            break

        articles.extend(items)
        print(f"  Got {len(items)} articles (total so far: {len(articles)})")

        next_start = results.get("nextStart")
        if not next_start or len(items) < params["n"]:
            break

        params["s"] = next_start
        page += 1
        time.sleep(0.5)

    return articles


def main():
    all_articles = {}
    log_rows = []

    for term in SEARCH_TERMS:
        print(f"\nSearching for: {term!r}")
        found = fetch_articles(term)
        for article in found:
            aid = article.get("id", "")
            if aid and aid not in all_articles:
                all_articles[aid] = article

    print(f"\nTotal unique articles found: {len(all_articles)}")

    for aid, article in all_articles.items():
        title = article.get("title", "Untitled").strip()
        date  = parse_date(article.get("date", ""))
        url   = article.get("troveUrl", "") or f"https://nla.gov.au/{aid}"
        slug  = slugify(title) or slugify(aid)
        filename = f"{date}-{slug}.md" if date else f"{slug}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            print(f"  SKIP (exists): {filename}")
            log_rows.append([aid, title, date, url, filename, "skipped"])
            continue

        md = build_markdown(article)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"  WRITTEN: {filename}")
        log_rows.append([aid, title, date, url, filename, "written"])

    csv_path = os.path.join(OUTPUT_DIR, "fetch_byline_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["trove_id", "title", "date", "url", "filename", "status"])
        writer.writerows(log_rows)

    print(f"\nDone. Results log: {csv_path}")


if __name__ == "__main__":
    main()
