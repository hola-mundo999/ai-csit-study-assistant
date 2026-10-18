import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0'}

# 1. Fetch categories
url = 'https://hamrocsit.com/wp-json/wp/v2/categories?per_page=100'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        cats = json.loads(resp.read().decode('utf-8'))
        print(f"Total categories: {len(cats)}")
        for c in cats[:20]:
            print(f"ID {c['id']}: {c['name']} (slug: {c['slug']}, count: {c['count']})")
except Exception as e:
    print("Error fetching categories:", e)
