"""Import the real study material from hamrocsit.com.

hamrocsit publishes every chapter two ways:

  * an HTML note at  https://hamrocsit.com/note/<subject>/<chapter>/
    which carries the actual text for most chapters, and
  * a password protected PDF, whose text cannot be read.

This script reads the HTML note, converts it to GitHub flavoured Markdown and
writes one file per subject:

    data/notes/<subject_slug>.json   -> { chapter_slug: markdown }

It never overwrites a chapter that already has a note, so re-running only fills
gaps. Chapters whose HTML page holds nothing but the PDF viewer keep whatever
note the generator already produced for them.

    python import_hamrocsit.py                 # everything missing
    python import_hamrocsit.py --limit 20      # a quick batch
    python import_hamrocsit.py --workers 8     # concurrency
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parent
STUDY = ROOT / "data" / "study.json"
NOTES_DIR = ROOT / "data" / "notes"
LOCK = threading.Lock()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 30

# Chrome inside the note container, dropped by class rather than by matching
# text. A text marker cut one chapter down to its first paragraph, because the
# promo banner sits in the middle of the note, not after it.
CHROME_CLASSES = (
    "chp_app_promo_banner",
    "related-link-post",
    "paginate_button",
    "pdf-toolbar",
    "pdfjs-viewer",
    "comments",
    "comment-respond",
    "post-share",
    "wp-block-buttons",
)
MIN_WORDS = 120


def slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").strip().lower())
    return text.strip("-")


def is_chrome(tag: Tag) -> bool:
    classes = " ".join(tag.get("class") or [])
    if any(marker in classes for marker in CHROME_CLASSES):
        return True
    if tag.get("id") and any(marker in tag["id"] for marker in CHROME_CLASSES):
        return True
    return False


def clean_html(fragment: Tag) -> str:
    """Turn one HTML block into markdown text."""
    for bad in fragment(["script", "style", "iframe", "noscript", "svg", "form"]):
        bad.decompose()

    out: list[str] = []
    for child in fragment.children:
        if not isinstance(child, Tag):
            text = re.sub(r"\s+", " ", str(child)).strip()
            if text:
                out.append(text)
            continue

        if is_chrome(child):
            continue

        name = child.name
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = min(4, int(name[1]))
            heading = child.get_text(" ", strip=True)
            if heading:
                out.append(f"{'#' * level} {heading}")
        elif name in ("ul", "ol"):
            for i, li in enumerate(child.find_all("li", recursive=False), 1):
                item = li.get_text(" ", strip=True)
                if not item:
                    continue
                bullet = f"{i}. " if name == "ol" else "- "
                out.append(bullet + item)
        elif name in ("pre", "code"):
            code = child.get_text("", strip=False).strip()
            if code:
                out.append(f"```\n{code}\n```")
        elif name == "table":
            out.append(render_table(child))
        elif name == "p":
            para = child.get_text(" ", strip=True)
            if para:
                out.append(para)
        elif name in ("div", "section", "article", "blockquote", "figure"):
            if is_chrome(child):
                continue
            nested = clean_html(child)
            if nested:
                out.append(nested)
        else:
            text = child.get_text(" ", strip=True)
            if text:
                out.append(text)

    return "\n\n".join(out)


def render_table(table: Tag) -> str:
    """Render an HTML table as a GitHub flavoured Markdown table."""
    rows = table.find_all("tr")
    grid: list[list[str]] = []
    for row in rows:
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["th", "td"])]
        if any(cells):
            grid.append(cells)
    if len(grid) < 2:
        return ""

    width = max(len(r) for r in grid)
    grid = [r + [""] * (width - len(r)) for r in grid]

    def line(cells: list[str]) -> str:
        return "| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |"

    header, body = grid[0], grid[1:]
    parts = [line(header), "| " + " | ".join(["---"] * width) + " |"]
    parts.extend(line(r) for r in body)
    return "\n".join(parts)


def stop_at(text: str) -> str:
    """Trim trailing site chrome that survived the class filter."""
    for marker in ("Previous Chapter", "Load More Comments", "Please login to comment"):
        position = text.find(marker)
        if position > 0:
            text = text[:position]
    return text.strip()


def fetch_note(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    container = (
        soup.select_one(".contents")
        or soup.select_one("article")
        or soup.select_one(".entry-content")
        or soup.select_one("main")
    )
    if container is None:
        return ""

    markdown = clean_html(container)
    markdown = stop_at(markdown)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    return markdown


def subject_file(slug: str) -> Path:
    return NOTES_DIR / f"{slug}.json"


def load_subject(slug: str) -> dict:
    path = subject_file(slug)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def save_subject(slug: str, notes: dict) -> None:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    subject_file(slug).write_text(
        json.dumps(notes, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8"
    )


def collect(study: dict, limit: int) -> list[dict]:
    queue: list[dict] = []
    for sem in study["semesters"]:
        for subject in sem["subjects"]:
            existing = load_subject(subject["slug"])
            for chapter in subject["chapters"]:
                if existing.get(chapter["slug"]):
                    continue
                if not chapter.get("url"):
                    continue
                queue.append(
                    {
                        "subject_slug": subject["slug"],
                        "chapter_slug": chapter["slug"],
                        "url": chapter["url"],
                    }
                )
    return queue[:limit] if limit else queue


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="stop after this many chapters")
    parser.add_argument("--workers", type=int, default=8, help="parallel requests")
    args = parser.parse_args()

    study = json.loads(STUDY.read_text(encoding="utf-8"))
    queue = collect(study, args.limit)
    print(f"{len(queue)} chapters to import, {args.workers} workers", flush=True)

    added = 0
    skipped = 0
    failed = 0

    def work(item: dict) -> tuple[dict, str, str]:
        try:
            return item, fetch_note(item["url"]), ""
        except Exception as exc:  # noqa: BLE001 - report and move on
            return item, "", str(exc)[:120]

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(work, item) for item in queue]
        for index, future in enumerate(as_completed(futures), 1):
            item, markdown, error = future.result()
            if error:
                failed += 1
                print(f"[{index}/{len(queue)}] FAIL {item['chapter_slug']}: {error}", flush=True)
                continue
            if len(markdown.split()) < MIN_WORDS:
                skipped += 1
                continue
            with LOCK:
                notes = load_subject(item["subject_slug"])
                if notes.get(item["chapter_slug"]):
                    skipped += 1
                    continue
                notes[item["chapter_slug"]] = markdown
                save_subject(item["subject_slug"], notes)
                added += 1
            print(f"[{index}/{len(queue)}] {item['subject_slug']}/{item['chapter_slug']} {len(markdown.split())} words", flush=True)

    print(f"added {added}, already had {skipped}, failed {failed}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
