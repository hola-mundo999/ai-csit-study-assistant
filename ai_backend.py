"""Secure AI backend for the CSIT Study Assistant.

Handles model selection and credentials entirely server-side. Provider secrets are
read from environment variables only and are never returned to the frontend. The
student-facing UI never sees an API key input, provider selector, or any raw
exception.
"""

import os
from typing import Optional, Tuple

from knowledge_base import kb


class AIChatResult:
    def __init__(
        self,
        answer: str,
        source: str,
        grounded_in_upload: bool = False,
        error: bool = False,
    ):
        self.answer = answer
        self.source = source  # 'offline', 'gemini', 'groq', 'error'
        self.grounded_in_upload = grounded_in_upload
        self.error = error


class AIChatBackend:
    """
    Server-side AI chat backend.

    Responsibilities:
      - Route to the configured provider (Gemini / Groq) using server-side env vars.
      - Fall back to the offline knowledge base when no provider is configured or
        when the provider is unavailable.
      - Never leak provider credentials, raw exceptions, or env-var names to the UI.
      - Keep conversation context for follow-up questions.
    """

    def __init__(self):
        self.provider = os.getenv("CSIT_AI_PROVIDER", "offline").lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self._effective_provider = self._resolve_provider()

    def _resolve_provider(self) -> str:
        if self.provider == "gemini" and self.gemini_api_key:
            return "gemini"
        if self.provider == "groq" and self.groq_api_key:
            return "groq"
        return "offline"

    def is_live(self) -> bool:
        return self._effective_provider in ("gemini", "groq")

    def configured_provider_label(self) -> Optional[str]:
        labels = {"gemini": "Google Gemini", "groq": "Groq"}
        return labels.get(self._effective_provider)

    def answer(
        self,
        question: str,
        conversation_history: list,
        uploaded_context: Optional[str] = None,
        uploaded_pages: Optional[list] = None,
    ) -> AIChatResult:
        if not question or not question.strip():
            return AIChatResult(
                "Please type a question.", source="error", error=True
            )

        question = question.strip()

        # 1. Try offline knowledge base first for common CSIT topics.
        topic = kb.search_topics(question)
        topic = topic[0] if topic else None
        if topic:
            answer = self._format_topic(topic, uploaded_context=uploaded_context)
            return AIChatResult(
                answer=answer,
                source="offline",
                grounded_in_upload=bool(uploaded_context),
            )

        # 2. If the user uploaded notes, ground the answer in them via the live
        #    provider (or offline keyword matching if provider unavailable).
        if uploaded_context:
            if self._effective_provider == "gemini":
                return self._call_gemini(
                    question, conversation_history, uploaded_context, uploaded_pages
                )
            if self._effective_provider == "groq":
                return self._call_groq(
                    question, conversation_history, uploaded_context, uploaded_pages
                )
            # No provider: answer from uploaded notes using simple keyword matching.
            return self._offline_from_notes(
                question, uploaded_context, uploaded_pages
            )

        # 3. No topic match and no upload: try live provider if configured.
        if self._effective_provider == "gemini":
            return self._call_gemini(question, conversation_history)
        if self._effective_provider == "groq":
            return self._call_groq(question, conversation_history)

        # 4. Final fallback: honest, useful offline response.
        return AIChatResult(
            answer=self._offline_general(question),
            source="offline",
        )

    # ------------------------------------------------------------------ #
    # Offline topic formatting
    # ------------------------------------------------------------------ #
    def _format_topic(self, topic, uploaded_context: Optional[str] = None) -> str:
        lines = [
            f"# {topic.title}",
            "",
            f"**Subject:** {topic.subject}  ·  **Semester:** {topic.semester}",
            "",
            "## Definition",
            topic.definition,
        ]

        if topic.how_it_works:
            lines += ["", "## How It Works"]
            for step in topic.how_it_works:
                lines.append(f"- {step}")

        if topic.example:
            lines += ["", "## Worked Example"]
            lines.append(f"```text\n{topic.example}\n```")

        if topic.pseudocode:
            lines += ["", "## Pseudocode"]
            lines.append(f"```text\n{topic.pseudocode}\n```")

        if topic.code:
            lines += ["", "## Code Example (Python)"]
            lines.append(f"```python\n{topic.code}\n```")

        if topic.complexity:
            lines += ["", "## Complexity"]
            lines.append("| Case | Time Complexity |")
            lines.append("|------|-----------------|")
            for case, comp in topic.complexity.items():
                lines.append(f"| {case} | {comp} |")
            if topic.space_complexity:
                lines.append("")
                lines.append(f"**Space:** {topic.space_complexity}")

        if topic.properties:
            lines += ["", "## Key Points"]
            for prop in topic.properties:
                lines.append(f"- {prop}")

        if topic.exam_points:
            lines += ["", "## Exam Preparation"]
            for point in topic.exam_points:
                lines.append(f"- {point}")

        if topic.practice_question:
            lines += ["", "## Practice Question"]
            lines.append(topic.practice_question)
            lines.append("")
            lines.append("> **Suggested answer:** " + (topic.practice_answer or "Try it yourself first, then check your notes."))

        if topic.related:
            lines += ["", "## Related Topics"]
            lines.append(", ".join(topic.related))

        if uploaded_context:
            lines += [
                "",
                "---",
                "Note: Your uploaded notes were detected, but this topic explanation "
                "comes from the built-in study guide. For answers grounded specifically "
                "in your notes, configure a live AI provider (server-side).",
            ]

        lines += [
            "",
            "---",
            "_TU CSIT Study Assistant · Built-in study guide (no API key required)_",
        ]
        return "\n".join(lines)

    def _offline_from_notes(
        self, question: str, context: str, pages: Optional[list]
    ) -> AIChatResult:
        """Best-effort answer grounded in uploaded notes without a live provider."""
        import re

        q_tokens = set(t for t in re.findall(r"[a-z0-9]+", question.lower()) if len(t) > 2)
        matches = []
        if pages:
            for page in pages:
                text = page.get("text", "")
                page_tokens = set(t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2)
                overlap = len(q_tokens & page_tokens)
                if overlap:
                    matches.append((overlap, page.get("page_num"), text))
        else:
            matches.append((len(q_tokens), None, context))

        matches.sort(key=lambda x: x[0], reverse=True)

        lines = [
            "# Answer (from your uploaded notes)",
            "",
            "No live AI provider is configured, so here is the most relevant passage "
            "from your uploaded document:",
        ]
        shown = False
        for overlap, page_num, text in matches[:3]:
            snippet = text[:900]
            lines += [
                "",
                f"### {'[Page %d] ' % page_num if page_num else ''}Relevant passage",
                f"```text\n{snippet}\n```",
            ]
            shown = True
        if not shown:
            lines.append("")
            lines.append("No relevant passage was found in your uploaded notes.")

        lines += [
            "",
            "To get AI-generated explanations from your notes, configure a live "
            "provider (Gemini or Groq) via server-side environment variables.",
        ]
        return AIChatResult(
            answer="\n".join(lines),
            source="offline",
            grounded_in_upload=True,
        )

    def _offline_general(self, question: str) -> str:
        return (
            "# I can help with CSIT topics\n\n"
            "I don't have a specific explanation for that topic in the built-in "
            "study guide yet, and no live AI provider is configured.\n\n"
            "Try asking about one of these instead: Quick Sort, Merge Sort, Binary "
            "Search, Big-O Notation, Linked List, Stack, Queue, Database "
            "Normalization, ACID Properties, Process vs Thread, Deadlock, TCP vs "
            "UDP, HTTP GET vs POST.\n\n"
            "You can also browse Notes & Resources or upload your lecture notes.\n"
        )

    # ------------------------------------------------------------------ #
    # Live providers (server-side only; credentials never leave this module)
    # ------------------------------------------------------------------ #
    def _call_gemini(
        self,
        question: str,
        conversation_history: list,
        context: Optional[str] = None,
        pages: Optional[list] = None,
    ) -> AIChatResult:
        try:
            from google import genai

            if not self.gemini_api_key:
                return AIChatResult(
                    answer=self._offline_general(question),
                    source="offline",
                )

            client = genai.Client(api_key=self.gemini_api_key)

            system_prompt = self._gemini_system_prompt(context is not None)
            user_prompt = self._gemini_user_prompt(
                question, context, pages, conversation_history
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}",
            )
            text = response.text or ""

            if context:
                text += (
                    "\n\n---\n\n*Grounded in your uploaded notes. "
                    "Answer generated by Google Gemini (server-side).*"  # noqa: E501
                )
            else:
                text += (
                    "\n\n---\n\n*Answer generated by Google Gemini (server-side).*"  # noqa: E501
                )

            return AIChatResult(
                answer=text,
                source="gemini",
                grounded_in_upload=bool(context),
            )
        except Exception:
            # Never leak raw exceptions to the student.
            if context:
                return self._offline_from_notes(question, context, pages)
            return AIChatResult(
                answer=self._offline_general(question),
                source="offline",
            )

    def _call_groq(
        self,
        question: str,
        conversation_history: list,
        context: Optional[str] = None,
        pages: Optional[list] = None,
    ) -> AIChatResult:
        try:
            from groq import Groq

            if not self.groq_api_key:
                return AIChatResult(
                    answer=self._offline_general(question),
                    source="offline",
                )

            client = Groq(api_key=self.groq_api_key)

            messages = [{"role": "system", "content": self._groq_system_prompt(context is not None)}]
            for role, content in conversation_history[-6:]:
                messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": self._groq_user_prompt(question, context)})

            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
            )
            text = chat.choices[0].message.content or ""

            if context:
                text += (
                    "\n\n---\n\n*Grounded in your uploaded notes. "
                    "Answer generated by Groq (server-side).*"
                )
            else:
                text += "\n\n---\n\n*Answer generated by Groq (server-side).*"

            return AIChatResult(
                answer=text,
                source="groq",
                grounded_in_upload=bool(context),
            )
        except Exception:
            if context:
                return self._offline_from_notes(question, context, pages)
            return AIChatResult(
                answer=self._offline_general(question),
                source="offline",
            )

    # ------------------------------------------------------------------ #
    # Prompts (no secrets included)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _gemini_system_prompt(has_context: bool) -> str:
        source_rule = (
            "Base your answer on the provided lecture notes and cite page numbers "
            "(e.g., [Page 3]) where relevant."
        ) if has_context else (
            "Answer from general CSIT knowledge. Be clear when the built-in guide "
            "does not cover a topic."
        )
        return (
            "You are a friendly, patient BSc CSIT tutor at Tribhuvan University. "
            "Explain concepts clearly for university students. "
            f"{source_rule} "
            "Use Markdown. Include examples, pseudocode, and complexity where useful. "
            "Keep answers concise but complete."
        )

    @staticmethod
    def _gemini_user_prompt(
        question: str,
        context: Optional[str],
        pages: Optional[list],
        history: list,
    ) -> str:
        context_block = ""
        if context:
            page_refs = ", ".join(str(p["page_num"]) for p in pages) if pages else "unknown"
            context_block = (
                f"\n\nLECTURE NOTES (pages: {page_refs}):\n{context}\n"
            )
        history_block = ""
        if history:
            history_block = "\n\nPREVIOUS CONVERSATION:\n" + "\n".join(
                f"{role}: {content}" for role, content in history[-6:]
            )
        return (
            "STUDENT QUESTION:\n" + question + context_block + history_block +
            "\n\nNow answer the student's question."
        )

    @staticmethod
    def _groq_system_prompt(has_context: bool) -> str:
        return AIChatBackend._gemini_system_prompt(has_context)

    @staticmethod
    def _groq_user_prompt(question: str, context: Optional[str]) -> str:
        return AIChatBackend._gemini_user_prompt(question, context, None, [])


# Module-level singleton (server-side)
chat_backend = AIChatBackend()
