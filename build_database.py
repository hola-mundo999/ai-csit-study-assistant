"""Compiles the complete HamroCSIT catalog and chapter notes database."""

import json

with open('hamrocsit_catalog_raw.json', 'r', encoding='utf-8') as f:
    raw_catalog = json.load(f)

with open('hamrocsit_notes_sitemap_inventory.json', 'r', encoding='utf-8') as f:
    notes_inventory = json.load(f)

# Group notes by subject_slug
notes_by_subject = {}
for n in notes_inventory:
    notes_by_subject.setdefault(n['subject_slug'], []).append(n)

# Mapping of catalog URL slugs to sitemap subject slugs
slug_map = {
    'iit': 'iit',
    'c-program': 'c-program',
    'dl': 'dl',
    'math-i': 'math-i',
    'physics': 'physics',
    'ds': 'ds',
    'oops': 'oops',
    'microprocessor': 'microprocessor',
    'mathii': 'mathii',
    'stat-i': 'stat-i',
    'dsa': 'dsa',
    'csc207': 'csc207',
    'csc208': 'csc208',
    'csc209': 'csc209',
    'stat-ii': 'stat-ii',
    'toc': 'toc',
    'cn': 'cn',
    'dbms': 'dbms',
    'os': 'os',
    'ai': 'ai',
    'daa': 'daa',
    'sad': 'sad',
    'cryptography': 'cryptography',
    'web-tech': 'web-tech',
    'sm': 'sm',
    'image-processing': 'fifth',
    'multimedia': 'multimedia',
    'seit': 'seit',
    'se': 'se',
    'cdc': 'cdc',
    'e-governance': 'e-governance',
    'ncc': 'ncc',
    'e-commerce': 'e-commerce',
    'tw': 'tw',
    'advanced-java': 'advanced-java',
    'data-mining': 'data-mining',
    'pom': 'pom',
    'database-administrator': 'database-administrator',
    'digital-system-design': 'digital-system-design',
    'information-retrieval': 'information-retrieval',
    'international-marketing': 'international-marketing',
    'network-security': 'network-security',
    'software-project-management': 'software-project-management',
    'advanced-database': 'advanced-database',
    'internship': 'internship',
    'decision-support-system-and-expert-system': 'decision-support-system-and-expert-system',
    'international-business-management': 'international-business-management',
    'introduction-to-cloud-computing': 'introduction-to-cloud-computing',
}

sem_names = {
    'first': 'First Semester',
    'second': 'Second Semester',
    'third': 'Third Semester',
    'fourth': 'Fourth Semester',
    'fifth': 'Fifth Semester',
    'sixth': 'Sixth Semester',
    'seventh': 'Seventh Semester',
    'eight': 'Eighth Semester',
}

sem_descriptions = {
    'first': 'First semester in B.Sc. CSIT helps to create the fundamental foundation of technology, electronic circuits, programming, and arithmetic to urge you started with the journey of B.Sc. CSIT.',
    'second': 'The second semester of B.Sc. CSIT focuses on elementary ideas of object-oriented programming approach, problem-solving, and advanced ideas of electronic circuits and boards.',
    'third': 'The third semester of B.Sc. CSIT focuses on the foundation of information structures, mathematical modeling, the design of computers, ideas of graphics, and applied mathematics measures together with hypotheses and varied tests.',
    'fourth': 'Fourth semester of B.Sc. CSIT introduces state machines and their languages, the conception of the pc networks and operating systems, the inspiration of the database management system and a glimpse of underlying principles of artificial intelligence.',
    'fifth': 'Fifth semester of B.Sc. CSIT is an introduction to basic components of design and analysis of pc algorithms, software development cycle, underlying principles and design of cryptosystems, modeling and simulation of various kinds of systems, elementary ideas of web development, multimedia, and image processing.',
    'sixth': 'Sixth Semester of B.Sc. CSIT focuses on developing ideas of software package cycles and testing, style of the compiler, e-governance, .NET framework, technical writing, hardware design, e-commerce, automation, and artificial intelligence.',
    'seventh': 'B. Sc. CSIT of Seventh Semester focuses on advance java programming. This semester also focus on Data warehouse, Data Mining and Network Security.',
    'eight': 'The Eight Semester of B. Sc. CSIT focus on advance database management systems and Networking. In this Semester, Student can implement their knowledge to solve real world problems.',
}

database = {
    'semesters': {},
    'total_subjects': 0,
    'total_chapters': 0,
}

total_subs = 0
total_chaps = 0

for sem_slug, subjects in raw_catalog.items():
    sem_title = sem_names.get(sem_slug, sem_slug.title() + ' Semester')
    sem_obj = {
        'slug': sem_slug,
        'title': sem_title,
        'description': sem_descriptions.get(sem_slug, ''),
        'subjects': []
    }
    
    for sub in subjects:
        total_subs += 1
        sub_url = sub['url']
        # Extract slug from url
        sub_slug = sub_url.strip('/').split('/')[-1]
        mapped_slug = slug_map.get(sub_slug, sub_slug)
        chapters = notes_by_subject.get(mapped_slug, [])
        total_chaps += len(chapters)
        
        sub_obj = {
            'name': sub['name'],
            'code': sub['code'],
            'url': sub['url'],
            'slug': sub_slug,
            'mapped_notes_slug': mapped_slug,
            'chapter_count': len(chapters),
            'chapters': chapters
        }
        sem_obj['subjects'].append(sub_obj)
        
    database['semesters'][sem_slug] = sem_obj

database['total_subjects'] = total_subs
database['total_chapters'] = total_chaps

print(f"Compiled database: {len(database['semesters'])} semesters, {total_subs} subjects, {total_chaps} chapters indexed.")

with open('hamrocsit_master_database.json', 'w', encoding='utf-8') as f:
    json.dump(database, f, indent=2)

print("Saved hamrocsit_master_database.json successfully.")
