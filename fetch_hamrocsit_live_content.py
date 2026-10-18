"""Fetches real past questions and notices from HamroCSIT WordPress REST API."""

import urllib.request
import json
import time
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# 1. Load categories
with open('hamrocsit_categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

with open('hamrocsit_master_database.json', 'r', encoding='utf-8') as f:
    master_db = json.load(f)

# 2. Fetch notices
notices = []
try:
    print("Fetching notices...")
    url = "https://hamrocsit.com/wp-json/wp/v2/notice?per_page=20"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        n_data = json.loads(resp.read().decode('utf-8'))
        for item in n_data:
            notices.append({
                "id": item.get("id"),
                "date": item.get("date", "")[:10],
                "title": item.get("title", {}).get("rendered", ""),
                "link": item.get("link", "")
            })
    print(f"Fetched {len(notices)} notices.")
except Exception as e:
    print(f"Error fetching notices: {e}")

# 3. Fetch past questions for each subject
questions_by_subject = {}

for sem_slug, sem_data in master_db.get("semesters", {}).items():
    for sub in sem_data.get("subjects", []):
        sub_slug = sub.get("slug")
        cat_info = categories.get(sub_slug)
        if not cat_info:
            continue
        cat_id = cat_info.get("id")
        q_url = f"https://hamrocsit.com/wp-json/wp/v2/question?categories={cat_id}&per_page=6"
        try:
            req = urllib.request.Request(q_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                q_list = json.loads(resp.read().decode('utf-8'))
                sub_questions = []
                for q in q_list:
                    raw_title = q.get("title", {}).get("rendered", "")
                    clean_title = BeautifulSoup(raw_title, "html.parser").get_text().strip()
                    sub_questions.append({
                        "id": q.get("id"),
                        "title": clean_title,
                        "link": q.get("link", ""),
                        "date": q.get("date", "")[:10]
                    })
                if sub_questions:
                    questions_by_subject[sub_slug] = sub_questions
                    print(f"[{sub.get('name')}] Fetched {len(sub_questions)} questions.")
        except Exception as e:
            print(f"Error for {sub_slug}: {e}")
        time.sleep(0.15)

payload = {
    "notices": notices,
    "questions_by_subject": questions_by_subject,
    "total_subjects_with_questions": len(questions_by_subject),
    "total_questions_indexed": sum(len(q) for q in questions_by_subject.values())
}

with open("hamrocsit_live_content.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print(f"Done! Saved {payload['total_questions_indexed']} questions across {payload['total_subjects_with_questions']} subjects and {len(notices)} notices.")
