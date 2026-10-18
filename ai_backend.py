"""Secure AI backend for the TU BSc CSIT Study Assistant.

Handles model selection, server-side credential management, and graceful offline fallback.
Provider secrets are read strictly from server-side environment variables and are never
returned to the client or embedded in client bundles. The student-facing UI never sees
raw developer configuration, API key input fields, or raw tracebacks.
"""

import os
from typing import List, Optional

from knowledge_base import kb


class AIChatResult:
    def __init__(
        self,
        answer: str,
        source: str,  # 'offline', 'gemini', 'groq', 'error'
        grounded_in_upload: bool = False,
        error: bool = False,
    ):
        self.answer = answer
        self.source = source
        self.grounded_in_upload = grounded_in_upload
        self.error = error


class AIChatBackend:
    """
    Server-side AI chat backend.

    Responsibilities:
      - Route to live AI providers (Google Gemini / Groq) using server-side env vars only.
      - Seamlessly fall back to the curated offline knowledge base when no provider is
        configured or if the live provider encounters rate limits or connection errors.
      - Never expose provider secrets, internal exceptions, or environment variable names.
      - Maintain conversational context for follow-up questions.
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.preferred_provider = os.getenv("CSIT_AI_PROVIDER", "").lower()
        self._effective_provider = self._resolve_provider()

    def reload_config(self):
        """Reload configuration from environment variables."""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.preferred_provider = os.getenv("CSIT_AI_PROVIDER", "").lower()
        self._effective_provider = self._resolve_provider()

    def _resolve_provider(self) -> str:
        if self.preferred_provider == "gemini" and self.gemini_api_key:
            return "gemini"
        if self.preferred_provider == "groq" and self.groq_api_key:
            return "groq"
        # Auto-detect if preference not explicitly set
        if self.gemini_api_key:
            return "gemini"
        if self.groq_api_key:
            return "groq"
        return "offline"

    def is_live(self) -> bool:
        return self._effective_provider in ("gemini", "groq")

    def provider_status_label(self) -> str:
        if self._effective_provider == "gemini":
            return "Google Gemini (Server-side)"
        if self._effective_provider == "groq":
            return "Groq Llama 3 (Server-side)"
        return "Offline Knowledge Engine (Active)"

    def answer(
        self,
        question: str,
        conversation_history: Optional[List[dict]] = None,
        uploaded_context: Optional[str] = None,
        uploaded_pages: Optional[list] = None,
        subject: str = "General CSIT",
    ) -> AIChatResult:
        if not question or not question.strip():
            return AIChatResult(
                "Please type a question before submitting.", source="error", error=True
            )

        question = question.strip()
        history = conversation_history or []

        # ------------------------------------------------------------------ #
        # TIER 1: Search Local HamroCSIT Learning Content First
        # ------------------------------------------------------------------ #
        if uploaded_context and any(
            w in question.lower()
            for w in ("uploaded", "notes", "lecture", "pdf", "page", "slide", "chapter in my")
        ):
            return self._offline_from_notes(question, uploaded_context, uploaded_pages)

        topic = kb.resolve_topic_from_context(question, history)
        is_curriculum_query = bool(topic) or any(
            w in question.lower()
            for w in (
                "practice question", "exam question", "sorting", "sort",
                "vs", "compare", "difference between", "how it works",
                "pseudocode", "complexity", "worst case", "worst-case",
                "normalization", "acid", "process", "thread", "deadlock",
                "tcp", "udp", "http"
            )
        )

        if is_curriculum_query:
            answer_text = kb.answer_query(
                question,
                history=history,
                subject=subject,
                uploaded_context=uploaded_context,
            )
            return AIChatResult(
                answer=answer_text,
                source="tier1_course_content",
                grounded_in_upload=bool(uploaded_context),
            )

        # ------------------------------------------------------------------ #
        # TIER 2: External AI Fallback when Content is Outside Course Notes
        # ------------------------------------------------------------------ #
        prefix = "> 🤖 *Notice: No sufficiently relevant answer was found in the available local HamroCSIT course notes, so here is a general AI-generated explanation.*\n\n"

        if self._effective_provider == "gemini":
            res = self._call_gemini(
                question, history, uploaded_context, uploaded_pages, subject=subject
            )
            if not res.error:
                res.answer = prefix + res.answer
                res.source = "tier2_external_ai"
                return res

        elif self._effective_provider == "groq":
            res = self._call_groq(
                question, history, uploaded_context, uploaded_pages, subject=subject
            )
            if not res.error:
                res.answer = prefix + res.answer
                res.source = "tier2_external_ai"
                return res

        # Tier 2 Fallback when no cloud provider credentials are set
        fallback_text = kb._format_general_fallback(question)
        return AIChatResult(
            answer=fallback_text,
            source="tier2_general_ai",
            grounded_in_upload=bool(uploaded_context),
        )

    def generate_exam_prep(
        self,
        subject: str = "Data Structures and Algorithms",
        num_questions: int = 5,
        uploaded_context: Optional[str] = None,
        uploaded_pages: Optional[list] = None,
    ) -> str:
        """Generates TU-style practice examination questions with rubrics and model answers."""
        num_questions = max(3, min(8, int(num_questions)))

        if self._effective_provider == "gemini":
            try:
                from google import genai

                client = genai.Client(api_key=self.gemini_api_key)
                prompt = (
                    f"You are a Tribhuvan University BSc CSIT professor for {subject}. "
                    f"Create a practice exam paper with exactly {num_questions} questions, "
                    f"including model answers, mark distributions (e.g. [6 Marks]), and step-by-step solutions.\n\n"
                    f"Context:\n{uploaded_context[:8000] if uploaded_context else 'Standard TU CSIT Syllabus'}"
                )
                resp = client.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt
                )
                if resp.text:
                    return resp.text + "\n\n---\n*Generated by Google Gemini (Server-side)*"
            except Exception:
                pass

        if self._effective_provider == "groq":
            try:
                from groq import Groq

                client = Groq(api_key=self.groq_api_key)
                prompt = (
                    f"You are a Tribhuvan University BSc CSIT professor for {subject}. "
                    f"Create a practice exam paper with exactly {num_questions} questions, "
                    f"including model answers, mark distributions, and step-by-step solutions."
                )
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                if chat.choices[0].message.content:
                    return chat.choices[0].message.content + "\n\n---\n*Generated by Groq (Server-side)*"
            except Exception:
                pass

        # Offline exam generator
        return kb._generate_sorting_practice_questions()

    def generate_flashcards(
        self,
        subject: str = "Data Structures and Algorithms",
        uploaded_context: Optional[str] = None,
    ) -> str:
        """Generates rapid revision notes and flashcards."""
        lines = [
            f"# Rapid Revision Flashcards — {subject}",
            "",
            "**Curated TU BSc CSIT Flashcards**",
            "",
            "### Flashcard 1: Quick Sort Complexity",
            "**Q:** What is the average and worst-case time complexity of Quick Sort?",
            "**A:** Average case is O(n log n). Worst case is O(n²) when the pivot chosen is consistently the extreme (smallest/largest) element.",
            "",
            "### Flashcard 2: Merge Sort Stability",
            "**Q:** Why is Merge Sort preferred when stability is required in sorting?",
            "**A:** Merge Sort maintains the original relative order of records with equal keys during the merge step, unlike standard in-place Quick Sort.",
            "",
            "### Flashcard 3: Binary Search Prerequisite",
            "**Q:** What is the fundamental condition required before performing Binary Search?",
            "**A:** The target collection or array must be sorted in ascending or descending order.",
            "",
            "### Flashcard 4: Database ACID Properties",
            "**Q:** Which ACID property ensures committed data survives a sudden power outage?",
            "**A:** Durability (guaranteed by write-ahead logging to non-volatile disk).",
            "",
            "### Flashcard 5: Process vs Thread",
            "**Q:** Why is context switching between threads faster than between processes?",
            "**A:** Threads share the same virtual memory space, so page tables and TLB caches do not need to be flushed on context switch.",
            "",
            "---",
            "*TU CSIT Study Assistant · Offline Revision Bank*",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Live Providers (Server-side Only)
    # ------------------------------------------------------------------ #
    def _call_gemini(
        self,
        question: str,
        history: List[dict],
        context: Optional[str],
        pages: Optional[list],
        subject: str,
    ) -> AIChatResult:
        try:
            from google import genai

            client = genai.Client(api_key=self.gemini_api_key)
            system_prompt = (
                f"You are a friendly, patient BSc CSIT tutor at Tribhuvan University teaching {subject}. "
                "Explain concepts clearly for university students with examples, pseudocode, and complexity analysis. "
                "Format in clean GitHub-style Markdown."
            )
            history_prompt = ""
            if history:
                history_prompt = "CONVERSATION HISTORY:\n" + "\n".join(
                    f"{m.get('role', 'user').upper()}: {m.get('content', '')}"
                    for m in history[-5:]
                ) + "\n\n"

            context_prompt = ""
            if context:
                context_prompt = f"UPLOADED NOTES CONTEXT:\n{context[:7000]}\n\n"

            prompt = f"{system_prompt}\n\n{context_prompt}{history_prompt}STUDENT QUESTION:\n{question}"
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            text = response.text or ""
            text += "\n\n---\n*Answer generated by Google Gemini (Server-side AI)*"
            return AIChatResult(answer=text, source="gemini", grounded_in_upload=bool(context))
        except Exception:
            # Fall back safely without leaking secrets or errors
            return AIChatResult(answer="", source="error", error=True)

    def _call_groq(
        self,
        question: str,
        history: List[dict],
        context: Optional[str],
        pages: Optional[list],
        subject: str,
    ) -> AIChatResult:
        try:
            from groq import Groq

            client = Groq(api_key=self.groq_api_key)
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"You are an expert TU BSc CSIT academic tutor in {subject}. "
                        "Provide comprehensive, student-friendly explanations with worked examples, "
                        "pseudocode, and time/space complexity analysis."
                    ),
                }
            ]
            for m in history[-4:]:
                messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})
            user_content = question
            if context:
                user_content = f"Context from notes:\n{context[:6000]}\n\nQuestion:\n{question}"
            messages.append({"role": "user", "content": user_content})

            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
            )
            text = chat.choices[0].message.content or ""
            text += "\n\n---\n*Answer generated by Groq (Server-side AI)*"
            return AIChatResult(answer=text, source="groq", grounded_in_upload=bool(context))
        except Exception:
            return AIChatResult(answer="", source="error", error=True)

    def _offline_from_notes(
        self, question: str, context: str, pages: Optional[list]
    ) -> AIChatResult:
        """Best-effort relevance extraction from uploaded document in offline mode."""
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
            "# Answer Grounded in Your Uploaded Notes",
            "",
            "Here are the most relevant sections identified from your uploaded document:",
        ]
        found = False
        for overlap, page_num, text in matches[:3]:
            snippet = text[:800].strip()
            page_label = f"Page {page_num}" if page_num else "Document Section"
            lines += [
                "",
                f"### 📄 {page_label}",
                f"```text\n{snippet}\n```",
            ]
            found = True

        if not found:
            lines.append("\nNo exact keyword match was found in the uploaded text.")

        lines += [
            "",
            "---",
            "*TU CSIT Study Assistant · Document Retrieval*",
        ]
        return AIChatResult(
            answer="\n".join(lines),
            source="offline",
            grounded_in_upload=True,
        )


# Singleton server-side backend instance
chat_backend = AIChatBackend()
