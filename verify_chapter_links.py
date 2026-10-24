"""Check every chapter link in study.json against hamrocsit.

A chapter URL that resolves to a different subject is worse than no URL: the
student clicks "Official study material" and lands somewhere unrelated. This
script fetches each link, compares the page title with the chapter title, and
writes data/chapter_links.json with the verdict so build_study_data can drop or
repair the bad ones.

    python verify_chapter_links.py            # check everything, write report
    python verify_chapter_links.py --limit 40
"""
from __future__ import annotations

import argparse
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
STUDY = ROOT / "data" / "study.json"
OUT = ROOT / "data" / "chapter_links.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0 Safari/537.36"}
LOCK = threading.Lock()

STOP = {
    "and", "the", "for", "with", "from", "introduction", "basic", "basics", "of", "in",
    "to", "a", "an", "data", "system", "management", "computer", "unit",
}


def words(text: str) -> set[str]:
    return {
        w
        for w in re.split(r"[^a-z0-9]+", (text or "").lower())
        if len(w) > 3 and w not in STOP
    }


def check(item: dict) -> dict:
    url = item["url"]
    record = {
        "subject": item["subject_slug"],
        "chapter": item["chapter_slug"],
        "url": url,
    }
    try:
        response = requests.get(url, timeout=25, headers=HEADERS, allow_redirects=True)
        record["status"] = response.status_code
        record["final_url"] = response.url
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        record["title"] = title[:160]
        page_words = words(title)
        chapter_words = words(item["title"])
        subject_words = words(item["subject_name"])
        record["overlap"] = sorted(page_words & chapter_words)
        record["subject_overlap"] = sorted(page_words & subject_words)
        # A page is right when it names either the chapter or the subject. Many
        # chapters are literally called "Introduction", so the subject test is
        # what actually catches a link that points at another course.
        record["ok"] = bool(record["overlap"] or record["subject_overlap"])
    except Exception as exc:  # noqa: BLE001
        record["status"] = 0
        record["title"] = ""
        record["overlap"] = []
        record["subject_overlap"] = []
        record["ok"] = False
        record["error"] = str(exc)[:120]
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    study = json.loads(STUDY.read_text(encoding="utf-8"))
    queue = []
    for semester in study["semesters"]:
        for subject in semester["subjects"]:
            for chapter in subject["chapters"]:
                if not chapter.get("url"):
                    continue
                queue.append(
                    {
                        "subject_slug": subject["slug"],
                        "chapter_slug": chapter["slug"],
                        "title": chapter["title"],
                        "subject_name": subject["name"],
                        "url": chapter["url"],
                    }
                )
    if args.limit:
        queue = queue[: args.limit]

    print(f"checking {len(queue)} chapter links", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(check, item) for item in queue]
        for index, future in enumerate(as_completed(futures), 1):
            record = future.result()
            results.append(record)
            if not record["ok"]:
                print(f"[{index}/{len(queue)}] MISMATCH {record['url']} -> {record['title'][:70]}", flush=True)

    good = sum(1 for r in results if r["ok"])
    print(f"\nok: {good}, mismatched: {len(results) - good}")
    if not args.limit:
        OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
