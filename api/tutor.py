"""Vercel serverless function: the CSIT Pulse tutor.

POST /api/tutor
  { "question": str, "length": "very_short|short|long|very_long",
    "history": [{ "role": "user"|"assistant", "content": str }] }
  -> { "answer": str, "source": "online"|"local", "engine": str }

No student ever supplies an API key. The function tries, in order:

  1. Groq, when the deployment owner has set GROQ_API_KEY (free tier, very fast).
  2. Pollinations text API, which serves an OpenAI-compatible model with no key
     and no signup.
  3. The curated local curriculum engine bundled with this repo, which always
     answers, even offline.

Every answer is normalised to strip long dashes.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from email.utils import formatdate
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional, Tuple

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from knowledge_base import kb  # noqa: E402

LENGTHS = ("very_short", "short", "long", "very_long")

LENGTH_RULES = {
    "very_short": (
        "Answer in under 70 words. Give the direct definition, the key formula or "
        "complexity, and one takeaway. No headings, no code unless essential."
    ),
    "short": (
        "Answer in about 150 words: definition, how it works, and the essential "
        "formula or complexity. At most one short code block."
    ),
    "long": (
        "Answer in about 400 words with short sections: definition, step by step "
        "mechanism, a small worked example or code snippet, complexity analysis, "
        "and one exam tip."
    ),
    "very_long": (
        "Write a full study guide of roughly 800 words for a Tribhuvan University "
        "BSc CSIT board exam: theory, step by step mechanism, runnable code or "
        "pseudocode, complexity analysis, common mistakes, and three practice "
        "questions with short model answers."
    ),
}

SYSTEM_PROMPT = (
    "You are a precise computer science professor for Tribhuvan University BSc CSIT "
    "students. Answer the question directly in the first sentence, then explain. "
    "Use GitHub flavoured Markdown with short paragraphs, and fenced code blocks with "
    "a language tag when code helps. Never use em dashes or en dashes, use a comma or "
    "the word 'to' instead. Never invent citations, exam dates or syllabus numbers. "
    "If a question is outside computer science, still answer it accurately and briefly."
)

MAX_QUESTION = 4000
MAX_HISTORY = 6
CACHE_TTL = 3 * 60 * 60
CACHE_LIMIT = 160
RATE_WINDOW = 60
RATE_LIMIT = 24

_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_HITS: Dict[str, List[float]] = {}


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def clean(text: str) -> str:
    """Strip long dashes and stray spaces, per house style."""
    if not text:
        return ""
    text = re.sub(r"\s*[\u2014\u2013]\s*", ", ", text)
    text = re.sub(r"[\u2010\u2011\u2012\u2015\u2212\u2043]", "-", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r",\s*([.;:!?])", r"\1", text)
    return text.strip()


def cache_key(question: str, length: str) -> str:
    return re.sub(r"\s+", " ", f"{length}::{question.lower()}").strip()


def cache_get(key: str) -> Optional[Dict[str, Any]]:
    hit = _CACHE.get(key)
    if not hit:
        return None
    stamp, payload = hit
    if time.time() - stamp > CACHE_TTL:
        _CACHE.pop(key, None)
        return None
    return payload


def cache_put(key: str, payload: Dict[str, Any]) -> None:
    if len(_CACHE) >= CACHE_LIMIT:
        oldest = min(_CACHE, key=lambda k: _CACHE[k][0])
        _CACHE.pop(oldest, None)
    _CACHE[key] = (time.time(), payload)


def rate_ok(ip: str) -> bool:
    now = time.time()
    window = [t for t in _HITS.get(ip, []) if now - t < RATE_WINDOW]
    if len(window) >= RATE_LIMIT:
        _HITS[ip] = window
        return False
    window.append(now)
    _HITS[ip] = window
    if len(_HITS) > 800:
        for stale in [k for k, v in _HITS.items() if not v or now - v[-1] > RATE_WINDOW]:
            _HITS.pop(stale, None)
    return True


def messages_for(question: str, length: str, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT} {LENGTH_RULES.get(length, LENGTH_RULES['short'])}"}]
    for item in history[-MAX_HISTORY:]:
        role = item.get("role", "user")
        content = str(item.get("content", ""))[:2000]
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question})
    return messages


# --------------------------------------------------------------------------- #
# Providers
# --------------------------------------------------------------------------- #
def ask_groq(question: str, length: str, history: List[Dict[str, str]]) -> Optional[str]:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "messages": messages_for(question, length, history),
                "temperature": 0.3,
                "max_tokens": 2600,
            },
            timeout=(6, 24),
        )
        if response.status_code != 200:
            return None
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        return text if text and text.strip() else None
    except Exception:
        return None


def ask_pollinations(question: str, length: str, history: List[Dict[str, str]]) -> Optional[str]:
    try:
        response = requests.post(
            "https://text.pollinations.ai/openai",
            headers={
                "Content-Type": "application/json",
                "Referer": os.getenv("APP_ORIGIN", "https://csit-pulse.vercel.app"),
            },
            json={
                "model": "openai",
                "messages": messages_for(question, length, history),
                "temperature": 0.3,
                "max_tokens": 3000,
                "private": True,
            },
            timeout=(8, 26),
        )
        if response.status_code != 200:
            return None
        data = response.json()
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        return text if text.strip() else None
    except Exception:
        return None


def local_answer(question: str, length: str, history: List[Dict[str, str]]) -> str:
    try:
        return kb.answer_query(question, history=history, length_mode=length)
    except Exception as exc:  # pragma: no cover - defensive
        return (
            "The tutor is having trouble with that question right now. "
            "Try rephrasing it, or open a chapter from the Curriculum tab."
        )


def answer(question: str, length: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    key = cache_key(question, length)
    cached = cache_get(key)
    if cached:
        return {**cached, "cached": True}

    text = ask_groq(question, length, history)
    if text:
        result = {"answer": clean(text), "source": "online", "engine": "Groq Llama 3.3"}
        cache_put(key, result)
        return result

    text = ask_pollinations(question, length, history)
    if text:
        result = {"answer": clean(text), "source": "online", "engine": "Pollinations"}
        cache_put(key, result)
        return result

    result = {
        "answer": clean(local_answer(question, length, history)),
        "source": "local",
        "engine": "Curriculum engine",
    }
    return result


# --------------------------------------------------------------------------- #
# HTTP entry point
# --------------------------------------------------------------------------- #
def json_response(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Date", formatdate(usegmt=True))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):  # noqa: N801 - Vercel's required name
    server_version = "csit-pulse/1.0"

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > 12000:
            json_response(self, 400, {"error": "Send a JSON body with a question."})
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            json_response(self, 400, {"error": "That request was not valid JSON."})
            return

        question = str(payload.get("question") or "").strip()[:MAX_QUESTION]
        if not question:
            json_response(self, 400, {"error": "Type a question first."})
            return

        mode = str(payload.get("length") or "short").lower()
        if mode not in LENGTHS:
            mode = "short"

        history = payload.get("history")
        if not isinstance(history, list):
            history = []

        ip = (self.headers.get("x-forwarded-for") or "local").split(",")[0].strip()
        if not rate_ok(ip):
            json_response(self, 429, {"error": "Too many questions at once. Wait a minute and try again."})
            return

        try:
            result = answer(question, mode, history)
        except Exception:
            json_response(self, 500, {"error": "The tutor could not answer that. Try again."})
            return

        json_response(self, 200, {**result, "length": mode})

    def do_GET(self) -> None:  # noqa: N802
        json_response(
            self,
            200,
            {
                "status": "ok",
                "usage": "POST {question, length, history}",
                "online": bool(os.getenv("GROQ_API_KEY")) or True,
            },
        )

    def log_message(self, fmt: str, *args: Any) -> None:  # keep logs quiet
        return
