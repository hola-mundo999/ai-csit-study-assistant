# CSIT Pulse

A free study desk for **Tribhuvan University BSc CSIT**: all eight semesters, 66 subjects, 375 chapters, a searchable bank of past board questions, and an AI tutor that answers any computer science question without an account or an API key.

Built by [Samyog Sapkota](https://github.com/hola-mundo999), BSc CSIT at Prime College.

## What is inside

- **Curriculum**: every semester with official course codes, and each subject's chapters. Clicking a chapter sends it straight to the tutor.
- **Past questions**: 278 questions collected from the public question archive, filterable by subject and searchable by keyword, each with a one click worked solution.
- **Tutor**: four answer depths, from a 70 word definition to a full exam guide with code, complexity and practice questions. Conversation context is kept, and every answer can be copied.

## How the tutor stays free

The browser talks to one serverless function, `api/tutor.py`, which tries providers in order and always returns something:

1. **Groq** when the deployment has `GROQ_API_KEY` set (free tier, the fastest option, optional).
2. **Pollinations** text API, an OpenAI compatible endpoint that needs no key and no signup.
3. **The bundled curriculum engine** in `knowledge_base.py`, which answers offline and covers the core CSIT topics.

Students never see or supply a key. Answers are cached for three hours per warm instance, and a light per IP rate limit keeps the free endpoints healthy. Long dashes are stripped from every answer.

## Tech stack

- Static HTML, CSS and vanilla JavaScript. No build step, no framework.
- `api/tutor.py`, a Python serverless function for Vercel.
- `data/study.json`, generated from the curriculum and question scrapes.

## Run locally

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`. The curriculum and questions load from the static JSON. The tutor needs the function, so run the full stack with Vercel:

```bash
npm i -g vercel
vercel dev
```

Python functions in `vercel dev` need a Unix host; on Windows use WSL or test the handler directly.

## Rebuild the study data

The payload is generated from `hamrocsit_master_database.json` and `hamrocsit_live_content.json`:

```bash
python build_study_data.py
```

This writes `data/study.json` (about 76 KB) with 66 subjects, 375 chapters and 278 questions.

## Deploy

```bash
vercel --prod
```

The project is configured in `vercel.json` (no framework, 45 second function budget). `requirements.txt` contains only what the function imports. The Streamlit host needs `requirements-streamlit.txt` instead.

Optional: add `GROQ_API_KEY` in the Vercel project settings for faster answers. Everything works without it.

## The Streamlit version

The original Streamlit hosts are still in the repo for local use:

```bash
pip install -r requirements-streamlit.txt
streamlit run app.py
```

They are excluded from the Vercel deployment.

## Tests

```bash
pip install -r requirements-streamlit.txt
pytest
```

33 tests cover the knowledge base, topic routing, answer length modes and the question bank.

## License

MIT.
