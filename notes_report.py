"""Report how many syllabus chapters already have a study note."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTES = ROOT / "data" / "notes"
STUDY = ROOT / "data" / "study.json"

study = json.loads(STUDY.read_text(encoding="utf-8"))
all_chapters = set()
for sem in study["semesters"]:
    for subject in sem["subjects"]:
        for chapter in subject["chapters"]:
            all_chapters.add((subject["slug"], chapter["slug"]))

have = set()
words = 0
for path in NOTES.glob("*.json"):
    subject_slug = path.stem
    notes = json.loads(path.read_text(encoding="utf-8"))
    for key, value in notes.items():
        have.add((subject_slug, key))
        words += len(str(value).split())

missing = all_chapters - have
print(f"chapters total: {len(all_chapters)}")
print(f"with a note:    {len(have)}")
print(f"missing:        {len(missing)}")
print(f"total words:    {words}")
