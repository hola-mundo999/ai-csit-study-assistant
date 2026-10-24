"""Build the static study payload used by the web app.

Reads the committed curriculum and question scrapes and writes a single compact
JSON file that the browser fetches directly. Run after refreshing the scrapes:

    python build_study_data.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "hamrocsit_master_database.json"
LIVE = ROOT / "hamrocsit_live_content.json"
OUT = ROOT / "data" / "study.json"

ORDER = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight"]


def clean(text: str) -> str:
    """Normalise scraped copy: collapse whitespace, replace long dashes."""
    text = " ".join((text or "").split())
    for dash in ("\u2014", "\u2013"):
        text = text.replace(f" {dash} ", ", ").replace(dash, "-")
    return text.strip()


def main() -> None:
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    live = json.loads(LIVE.read_text(encoding="utf-8"))

    raw_sems = master.get("semesters", {})
    semesters = []
    subjects_total = 0
    chapters_total = 0
    # slug -> (subject name, course code) for labelling questions
    by_slug: dict[str, tuple[str, str]] = {}

    for key in ORDER:
        sem = raw_sems.get(key)
        if not sem:
            continue
        subjects = []
        for subj in sem.get("subjects", []):
            chapters = [
                {
                    "title": clean(ch.get("title", "")),
                    "slug": ch.get("chapter_slug", ""),
                    "url": ch.get("url", ""),
                }
                for ch in subj.get("chapters", [])
                if clean(ch.get("title", ""))
            ]
            name = clean(subj.get("name", ""))
            code = clean(subj.get("code", ""))
            subjects.append(
                {
                    "name": name,
                    "code": code,
                    "slug": subj.get("mapped_notes_slug") or subj.get("slug", ""),
                    "chapters": chapters,
                }
            )
            by_slug[subj.get("mapped_notes_slug") or subj.get("slug", "")] = (name, code)
            by_slug[subj.get("slug", "")] = (name, code)
            subjects_total += 1
            chapters_total += len(chapters)
        semesters.append(
            {
                "slug": key,
                "title": clean(sem.get("title", key.title())),
                "description": clean(sem.get("description", "")),
                "subjects": subjects,
            }
        )

    questions = []
    for slug, items in live.get("questions_by_subject", {}).items():
        subject, code = by_slug.get(slug, (slug.upper(), ""))
        for item in items:
            date = str(item.get("date", ""))
            questions.append(
                {
                    "subject": subject,
                    "code": code,
                    "title": clean(item.get("title", "")),
                    "year": date[:4],
                    "date": date,
                }
            )
    questions.sort(key=lambda q: (q["date"], q["title"]), reverse=True)

    payload = {
        "semesters": semesters,
        "questions": [q for q in questions if q["title"]],
        "totals": {
            "subjects": subjects_total,
            "chapters": chapters_total,
            "questions": len([q for q in questions if q["title"]]),
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(
        f"wrote {OUT.relative_to(ROOT)} "
        f"({OUT.stat().st_size / 1024:.0f} KB, "
        f"{subjects_total} subjects, {chapters_total} chapters, {payload['totals']['questions']} questions)"
    )


if __name__ == "__main__":
    main()
