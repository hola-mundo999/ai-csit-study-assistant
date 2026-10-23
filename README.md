# CSIT Pulse

A free study desk for **Tribhuvan University BSc CSIT**: all eight semesters, 66 subjects, 375 chapters, a searchable bank of past board questions, and an AI tutor that answers the question you actually asked, without an account or an API key.

Built by [Samyog Sapkota](https://github.com/hola-mundo999), BSc CSIT at Prime College.

## What is inside

- **Curriculum**: every semester with official course codes and each subject's chapters. Clicking a chapter opens its saved note inline, with worked key points, complexity and a button to ask a follow-up.
- **Past questions**: 278 questions from the public question archive, filterable by subject and searchable by keyword. Each one solves itself inline, streamed, from the model.
- **Tutor**: four answer depths, from a 70 word definition to a full exam guide. Tokens stream into the page as they arrive, conversation context is kept, and answers are cached in the browser for a week.

## How the tutor works

The page calls `https://text.pollinations.ai/openai`, an OpenAI compatible endpoint that needs no key and no signup, directly from the browser. That means:

- Each visitor uses their own quota instead of sharing one server IP.
- No serverless cold start sits between the question and the first token.
- Answers stream as they are written, so the first words show up in about a second.
- The endpoint is rate limited to roughly one reply every 30 seconds per IP. When that happens the page shows a countdown and retries once, then offers a retry button. It never substitutes a different answer.

For CSIT topics that exist in `data/topics.json`, a short reference block (definition, mechanism, complexity) is attached to the prompt so the answer is grounded in the syllabus rather than guessed.

Nothing is sent to a server of ours. There is no function to deploy, so there is no cold start and nothing to keep warm.

## Tech stack

Static HTML, CSS and vanilla JavaScript. No build step, no framework, no backend.

- `data/study.json`: 66 subjects, 375 chapters, 278 questions (76 KB).
- `data/topics.json`: 26 study notes used as model context (27 KB).
- `build_study_data.py`: regenerates `study.json` from the curriculum and question scrapes.

## Run locally

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. Everything works, including the tutor, because the model is called from the browser.

## Rebuild the study data

```bash
python build_study_data.py
```

## Deploy

```bash
vercel --prod
```

`vercel.json` marks the project as a static site and caches `data/` for an hour. No environment variables are needed.

## The Streamlit version

The original Streamlit host is still in the repo for local use:

```bash
pip install -r requirements-streamlit.txt
streamlit run app.py
```

It is excluded from the Vercel deployment.

## Tests

```bash
pip install -r requirements-streamlit.txt
pytest
```

33 tests cover the knowledge base, topic routing, answer length modes and the question bank.

## License

MIT.
