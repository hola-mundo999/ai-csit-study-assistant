"""Academic Q&A engine for BSc CSIT lecture notes and syllabus concepts.

Integrates server-side LLM providers (Google Gemini / Groq) with the rich offline
knowledge base so students receive comprehensive educational answers even when no
external AI credentials are configured.
"""

import os
import re
from typing import Optional

from ai_backend import chat_backend
from knowledge_base import kb
from pdf_processor import chunk_text


class AIEngine:
    """
    Academic Q&A engine for BSc CSIT lecture notes.

    Routes generation between Google Gemini, Groq, and a built-in deterministic
    offline knowledge engine. All providers ground answers in uploaded lecture context
    when provided. When offline, answers are drawn from curated TU BSc CSIT study material.
    """

    def __init__(self, provider: str = "demo", api_key: Optional[str] = None):
        self.provider = (provider or "demo").lower()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")

    def answer_question(
        self,
        question: str,
        context: str = "",
        subject: str = "General CSIT",
        pages: Optional[list] = None,
        history: Optional[list] = None,
    ) -> str:
        """
        Answers a student question academically and thoroughly.
        """
        if not question or not question.strip():
            return "Please ask a question before submitting."

        question = question.strip()
        relevant_context, sources = self._select_relevant_context(question, context, pages)

        # If live provider is requested and key exists
        if "gemini" in self.provider and self.api_key:
            res = self._call_gemini(
                self._qa_system_prompt(subject, bool(sources)),
                self._qa_user_prompt(question, relevant_context, sources),
            )
            if not res.startswith("❌"):
                return res

        if "groq" in self.provider and self.api_key:
            res = self._call_groq(
                self._qa_system_prompt(subject, bool(sources)),
                self._qa_user_prompt(question, relevant_context, sources),
            )
            if not res.startswith("❌"):
                return res

        # Offline educational engine
        return self._demo_answer(question, relevant_context, subject, sources, history=history)

    def generate_exam_prep(
        self,
        context: str = "",
        subject: str = "General CSIT",
        num_questions: int = 5,
        pages: Optional[list] = None,
    ) -> str:
        """Generates TU-style practice questions with model answers and rubrics."""
        num_questions = max(3, min(8, int(num_questions)))
        relevant_context, sources = self._select_relevant_context(
            "exam paper generation", context, pages, max_chars=10000
        )

        if "gemini" in self.provider and self.api_key:
            system_prompt = f"You are a senior BSc CSIT professor designing a practice exam sheet for {subject}."
            user_prompt = f"Generate {num_questions} practice questions with model answers and marks."
            res = self._call_gemini(system_prompt, user_prompt)
            if not res.startswith("❌"):
                return res

        if "groq" in self.provider and self.api_key:
            system_prompt = f"You are a senior BSc CSIT professor designing a practice exam sheet for {subject}."
            user_prompt = f"Generate {num_questions} practice questions with model answers and marks."
            res = self._call_groq(system_prompt, user_prompt)
            if not res.startswith("❌"):
                return res

        return chat_backend.generate_exam_prep(
            subject=subject, num_questions=num_questions, uploaded_context=relevant_context
        )

    def generate_summary_flashcards(
        self,
        context: str = "",
        subject: str = "General CSIT",
        pages: Optional[list] = None,
    ) -> str:
        """Generates rapid revision notes, definitions, formulas, and flashcards."""
        relevant_context, sources = self._select_relevant_context(
            "revision summary", context, pages, max_chars=10000
        )

        if "gemini" in self.provider and self.api_key:
            system_prompt = f"You are an AI study coach for BSc CSIT in {subject}."
            user_prompt = "Generate revision flashcards and core concept summary."
            res = self._call_gemini(system_prompt, user_prompt)
            if not res.startswith("❌"):
                return res

        return chat_backend.generate_flashcards(subject=subject, uploaded_context=relevant_context)

    # ------------------------------------------------------------------ #
    # Context selection (relevance scoring + page citations)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _tokenize(text: str) -> list:
        return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2]

    def _select_relevant_context(
        self,
        question: str,
        context: str,
        pages: Optional[list],
        max_chars: int = 9000,
    ) -> tuple:
        query_tokens = set(self._tokenize(question))
        if not query_tokens:
            return context[:max_chars], []

        chunk_entries = []

        if pages:
            for page in pages:
                page_text = page.get("text") or ""
                page_num = page.get("page_num")
                for chunk in chunk_text(page_text, chunk_size=900, overlap=100):
                    if chunk.strip():
                        chunk_entries.append((chunk, page_num))
        else:
            chunk_entries.append((context, None))

        scored = []
        for chunk_text_val, page_num in chunk_entries:
            chunk_tokens = set(self._tokenize(chunk_text_val))
            if not chunk_tokens:
                continue
            overlap = len(query_tokens & chunk_tokens)
            score = overlap / max(1, len(query_tokens))
            score += 0.1 * min(1.0, overlap / max(1, len(query_tokens)))
            scored.append((score, chunk_text_val, page_num))

        scored.sort(key=lambda entry: entry[0], reverse=True)

        selected = []
        selected_pages = []
        used = 0
        for score, chunk_text_val, page_num in scored:
            if score <= 0:
                continue
            prefix = f"[Page {page_num}] " if page_num is not None else ""
            entry = prefix + chunk_text_val
            if used + len(entry) > max_chars:
                if selected:
                    break
                selected.append(entry[:max_chars])
                if page_num is not None:
                    selected_pages.append(page_num)
                break
            selected.append(entry)
            if page_num is not None and page_num not in selected_pages:
                selected_pages.append(page_num)
            used += len(entry)

        if not selected:
            return context[:max_chars], []

        return "\n\n---\n\n".join(selected), sorted(selected_pages)

    # ------------------------------------------------------------------ #
    # Prompts
    # ------------------------------------------------------------------ #
    def _qa_system_prompt(self, subject: str, has_sources: bool) -> str:
        return (
            f"You are a helpful, expert BSc CSIT professor at Tribhuvan University for {subject}. "
            "Explain concepts accurately, provide step-by-step algorithms, worked examples, and complexity."
        )

    def _qa_user_prompt(self, question: str, context: str, sources: list) -> str:
        ctx_part = f"\n\nCONTEXT:\n{context}\n\nSOURCES: {sources}" if context else ""
        return f"QUESTION:\n{question}{ctx_part}"

    # ------------------------------------------------------------------ #
    # Provider Implementations
    # ------------------------------------------------------------------ #
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}",
            )
            return response.text or ""
        except Exception as e:
            return f"❌ Gemini API Error: {e}"

    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        try:
            from groq import Groq

            client = Groq(api_key=self.api_key)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
            )
            return chat_completion.choices[0].message.content or ""
        except Exception as e:
            return f"❌ Groq API Error: {e}"

    # ------------------------------------------------------------------ #
    # Offline Educational Response
    # ------------------------------------------------------------------ #
    def _demo_answer(
        self,
        question: str,
        context: str,
        subject: str,
        sources: list,
        history: Optional[list] = None,
    ) -> str:
        # Use knowledge_base engine for rich, intent-specific answer
        answer = kb.answer_query(
            question, history=history, subject=subject, uploaded_context=context
        )
        if sources:
            answer += f"\n\n*Referenced source pages: {', '.join(map(str, sources))}*"
        return answer
