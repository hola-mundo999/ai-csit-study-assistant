"""Write a real study note for every chapter in the syllabus.

HamroCSIT publishes each chapter as a password protected PDF, so their text
cannot be imported. This script asks the free model for a short, original note
per chapter instead, and writes one file per subject:

    data/notes/<subject_slug>.json   -> { chapter_slug: markdown }

The browser fetches only the subject it is looking at, so a phone that opens
one subject downloads one small file.

It is resumable and parallel:

    python generate_chapter_notes.py                  # every missing chapter
    python generate_chapter_notes.py --limit 10       # a quick batch
    python generate_chapter_notes.py --sem third      # one semester
    python generate_chapter_notes.py --workers 8      # concurrency

Existing notes are never overwritten, so re-running only fills gaps.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
STUDY = ROOT / "data" / "study.json"
NOTES_DIR = ROOT / "data" / "notes"
ENDPOINT = "https://ai-csit-study-assistant.vercel.app/api/chat"
# The edge proxy shares one IP with every visitor, so a long batch burns its
# quota out. --direct talks to the provider from this machine instead, which
# has a quota of its own.
DIRECT_ENDPOINT = "https://text.pollinations.ai/openai"
DIRECT = False
LOCK = threading.Lock()

SYSTEM = (
    "You are a Tribhuvan University BSc CSIT lecturer. Write a study note for the "
    "chapter a student asked about. Be accurate and specific to the chapter, never "
    "generic and never about a similar topic. Format in GitHub flavoured Markdown: "
    "one short definition line, then '## Key points' with 4 to 6 bullets, then "
    "'## Example' with 6 to 10 lines of code or a worked trace, then '## Exam focus' "
    "with 2 likely questions and a one line answer each. Keep it under 300 words. "
    "Never use em dashes or en dashes, use a comma or the word 'to' instead. "
    "Never invent TU exam dates, question numbers, page numbers or citations."
)


def clean(text: str) -> str:
    """Strip long dashes, per house style."""
    text = re.sub(r"\s*[\u2014\u2013]\s*", ", ", text or "")
    text = re.sub(r"[\u2010\u2011\u2012\u2015\u2212\u2043]", "-", text)
    return text.strip()


# The free provider allows a handful of requests per minute per IP. Six workers
# with no gap between them spent the whole allowance in seconds and most notes
# came back as a rate limit, so pace the workers instead.
THROTTLE_SECONDS = 2.5
_last_request = [0.0]
_throttle_lock = threading.Lock()


def wait_turn() -> None:
    while True:
        with _throttle_lock:
            gap = time.time() - _last_request[0]
            if gap >= THROTTLE_SECONDS:
                _last_request[0] = time.time()
                return
        time.sleep(0.15)


def ask(question: str, retries: int = 3) -> str:
    """Stream an answer from the model and return its text."""
    delay = 25
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    payload = (
        {
            "model": "openai",
            "messages": messages,
            "stream": True,
            "temperature": 0.35,
            "max_tokens": 900,
            "private": True,
            "reasoning_effort": "low",
        }
        if DIRECT
        else {"max_tokens": 900, "messages": messages}
    )
    url = DIRECT_ENDPOINT if DIRECT else ENDPOINT
    for attempt in range(retries):
        try:
            wait_turn()
            with requests.post(
                url,
                json=payload,
                stream=True,
                timeout=120,
            ) as response:
                if response.status_code != 200:
                    body = response.content.decode("utf-8", "replace")
                    # The provider says either "wait N seconds" or "Retry after Ns".
                    wait = re.search(r"(?:wait|retry after)\s+(\d+)", body or "", re.I)
                    if response.status_code in (402, 429, 504):
                        pause = int(wait.group(1)) + 1 if wait else delay
                        print(f"    HTTP {response.status_code}, backing off {pause}s", flush=True)
                        time.sleep(pause)
                        delay *= 2
                        continue
                    raise RuntimeError(f"HTTP {response.status_code}")
                parts: list[str] = []
                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data:"):
                        continue
                    try:
                        delta = json.loads(line[5:].strip())["choices"][0].get("delta") or {}
                    except (ValueError, KeyError, IndexError):
                        continue
                    parts.append(delta.get("content") or "")
                answer = clean("".join(parts)).strip()
                if answer:
                    return answer
                print("    empty answer from the model", flush=True)
                raise RuntimeError("empty answer")
        except Exception as exc:  # noqa: BLE001 - report, back off, retry
            print(f"    retry after {exc}", flush=True)
            time.sleep(delay)
            delay *= 2
    return ""


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


def collect(study: dict, sem_filter: str) -> list[dict]:
    queue = []
    for sem in study["semesters"]:
        if sem_filter and sem["slug"] != sem_filter:
            continue
        for subject in sem["subjects"]:
            existing = load_subject(subject["slug"])
            for chapter in subject["chapters"]:
                if existing.get(chapter["slug"]):
                    continue
                queue.append(
                    {
                        "subject_slug": subject["slug"],
                        "chapter_slug": chapter["slug"],
                        "subject": subject["name"],
                        "code": subject["code"],
                        "semester": sem["title"],
                        "title": chapter["title"],
                    }
                )
    return queue


def main() -> int:
    global THROTTLE_SECONDS, DIRECT

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="stop after this many notes")
    parser.add_argument("--sem", default="", help="only this semester, e.g. third")
    parser.add_argument("--workers", type=int, default=6, help="parallel requests")
    parser.add_argument(
        "--direct",
        action="store_true",
        help="call the provider directly instead of through the deployed proxy",
    )
    parser.add_argument(
        "--throttle",
        type=float,
        default=THROTTLE_SECONDS,
        help="seconds to wait between provider requests",
    )
    args = parser.parse_args()
    THROTTLE_SECONDS = max(0.0, args.throttle)
    DIRECT = args.direct

    study = json.loads(STUDY.read_text(encoding="utf-8"))
    queue = collect(study, args.sem)
    if args.limit:
        queue = queue[: args.limit]

    print(f"{len(queue)} chapters still need a note, {args.workers} workers", flush=True)

    def work(item: dict) -> tuple[str, str]:
        prompt = (
            f"Chapter: {item['title']}\n"
            f"Course: {item['subject']} ({item['code']})\n"
            f"Semester: {item['semester']}\n\n"
            "Write the note now."
        )
        return item["key"], item["subject_slug"], ask(prompt)

    for item in queue:
        item["key"] = item["chapter_slug"]

    written = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(work, item) for item in queue]
        for index, future in enumerate(as_completed(futures), 1):
            key, subject_slug, answer = future.result()
            if not answer:
                continue
            with LOCK:
                notes = load_subject(subject_slug)
                if notes.get(key):
                    continue
                notes[key] = answer
                save_subject(subject_slug, notes)
                written += 1
            print(f"[{index}/{len(queue)}] {subject_slug}/{key} {len(answer.split())} words", flush=True)

    print(f"added {written} notes", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
