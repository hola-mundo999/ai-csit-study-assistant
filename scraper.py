import urllib.request, json, time
from bs4 import BeautifulSoup

with open('hamrocsit_catalog_raw.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

detailed_catalog = {}
headers = {'User-Agent': 'Mozilla/5.0'}

for sem, subjects in catalog.items():
    detailed_catalog[sem] = []
    print(f'Processing {sem}...')
    for sub in subjects:
        url = sub['url']
        try:
            req = urllib.request.Request(url, headers=headers)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract chapters
            chapters = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/note/' in href:
                    text = a.get_text().strip()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    title = lines[0] if lines else ''
                    if title and title not in ['Read Note', 'Read More', 'Home', 'Share'] and not any(c['title'] == title for c in chapters):
                        chapters.append({'title': title, 'url': href})
            
            # Extract description
            desc = ''
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc and meta_desc.get('content'):
                desc = meta_desc['content'].strip()
            
            sub_data = {
                'name': sub['name'],
                'code': sub['code'],
                'url': sub['url'],
                'description': desc,
                'chapters': chapters
            }
            detailed_catalog[sem].append(sub_data)
            print(f"  {sub['name']} ({sub['code']}): {len(chapters)} chapters")
        except Exception as e:
            print(f"  Failed {sub['name']}: {e}")
            detailed_catalog[sem].append({
                'name': sub['name'],
                'code': sub['code'],
                'url': sub['url'],
                'description': '',
                'chapters': []
            })
        time.sleep(0.2)

with open('hamrocsit_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(detailed_catalog, f, indent=2)
print('Done dumping detailed catalog.')
