"""Fold the legacy flat note store into the per-subject files the site reads.

The front end only ever fetches data/notes/<subject>.json, so a note that only
exists in data/chapter_notes.json is invisible to students. This script merges
that flat store into the per-subject files and prefers the longer note when a
chapter already has one, because the imported hamrocsit material and the AI
drafts do not have the same depth.

    python merge_notes.py           # merge and report
    python merge_notes.py --dry     # report only, write nothing
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTES_DIR = ROOT / "data" / "notes"
STUDY = ROOT / "data" / "study.json"
FLAT = ROOT / "data" / "chapter_notes.json"


def word_count(text: object) -> int:
    return len(str(text or "").split())


def read_flat() -> dict[tuple[str, str], str]:
    if not FLAT.exists():
        return {}
    raw = json.loads(FLAT.read_text(encoding="utf-8"))
    notes: dict[tuple[str, str], str] = {}
    for key, value in raw.items():
        if not isinstance(value, str) or not value.strip():
            continue
        if "/" not in key:
            continue
        subject_slug, chapter_slug = key.split("/", 1)
        notes[(subject_slug, chapter_slug)] = value.strip()
    return notes


def read_subject_files() -> dict[tuple[str, str], str]:
    notes: dict[tuple[str, str], str] = {}
    if not NOTES_DIR.exists():
        return notes
    for path in sorted(NOTES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for chapter_slug, value in data.items():
            if isinstance(value, str) and value.strip():
                notes[(path.stem, chapter_slug)] = value.strip()
    return notes


def syllabus_chapters() -> list[tuple[str, str]]:
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    chapters = []
    for semester in study["semesters"]:
        for subject in semester["subjects"]:
            for chapter in subject["chapters"]:
                chapters.append((subject["slug"], chapter["slug"]))
    return chapters


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="report without writing")
    args = parser.parse_args()

    flat = read_flat()
    have = read_subject_files()
    before = len(have)

    added = 0
    upgraded = 0
    for key, note in flat.items():
        current = have.get(key)
        if current is None:
            have[key] = note
            added += 1
        elif word_count(note) > word_count(current) * 1.25:
            # A much longer draft is better than a stub, but never replace a
            # real imported note with a slightly padded one.
            have[key] = note
            upgraded += 1

    chapters = syllabus_chapters()
    covered = [chapter for chapter in chapters if chapter in have]
    missing = [chapter for chapter in chapters if chapter not in have]

    print(f"notes before:   {before}")
    print(f"added:          {added}")
    print(f"upgraded:       {upgraded}")
    print(f"notes after:    {len(have)}")
    print(f"chapters:       {len(chapters)}")
    print(f"covered:        {len(covered)}")
    print(f"still missing:  {len(missing)}")
    if missing:
        from collections import Counter

        for subject_slug, count in Counter(s for s, _ in missing).most_common():
            print(f"  {subject_slug}: {count}")

    if args.dry:
        return 0

    by_subject: dict[str, dict[str, str]] = {}
    for (subject_slug, chapter_slug), note in have.items():
        by_subject.setdefault(subject_slug, {})[chapter_slug] = note

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    for subject_slug, notes in by_subject.items():
        path = NOTES_DIR / f"{subject_slug}.json"
        path.write_text(
            json.dumps(notes, ensure_ascii=False, indent=0, sort_keys=True),
            encoding="utf-8",
        )
    print(f"wrote {len(by_subject)} subject files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
