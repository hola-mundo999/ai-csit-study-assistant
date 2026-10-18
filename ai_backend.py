"""Secure AI backend for TU BSc CSIT Pulse.

Handles multi-model selection (OpenAI ChatGPT, Google Gemini, Groq Llama 3, and Local Universal Engine),
custom answer length modes (Very Short, Short, Long, Very Long), server-side credential management,
and seamless universal offline fallback.
"""

import os
from typing import List, Optional

from knowledge_base import kb


class AIChatResult:
    def __init__(
        self,
        answer: str,
        source: str,  # 'offline', 'gemini', 'groq', 'openai', 'tier1_course_content', 'tier2_external_ai', 'tier2_general_ai', 'error'
        grounded_in_upload: bool = False,
        error: bool = False,
    ):
        self.answer = answer
        self.source = source
        self.grounded_in_upload = grounded_in_upload
        self.error = error


class AIChatBackend:
    """
    Server-side AI chat backend for CSIT Pulse.

    Responsibilities:
      - Multi-provider support: OpenAI (GPT-4o mini), Google Gemini, Groq (Llama 3).
      - Multi-length modes: very_short, short, long, very_long.
      - Seamlessly answer ANY university question using local curated knowledge
        or external AI models when configured.
      - Never expose provider secrets, internal exceptions, or environment variables.
      - Maintain conversational context for follow-up questions.
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.preferred_provider = os.getenv("CSIT_AI_PROVIDER", "").lower()
        self._effective_provider = self._resolve_provider()

    def reload_config(self):
        """Reload configuration from environment variables."""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.preferred_provider = os.getenv("CSIT_AI_PROVIDER", "").lower()
        self._effective_provider = self._resolve_provider()

    def _resolve_provider(self) -> str:
        if self.preferred_provider == "openai" and self.openai_api_key:
            return "openai"
        if self.preferred_provider == "gemini" and self.gemini_api_key:
            return "gemini"
        if self.preferred_provider == "groq" and self.groq_api_key:
            return "groq"
        # Auto-detect if preference not explicitly set
        if self.openai_api_key:
            return "openai"
        if self.gemini_api_key:
            return "gemini"
        if self.groq_api_key:
            return "groq"
        return "offline"

    def is_live(self) -> bool:
        return self._effective_provider in ("openai", "gemini", "groq")

    def provider_status_label(self) -> str:
        if self._effective_provider == "openai":
            return "OpenAI ChatGPT (Server-side)"
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
        length_mode: str = "long",
        model_provider: str = "auto",
        custom_api_key: Optional[str] = None,
    ) -> AIChatResult:
        if not question or not question.strip():
            return AIChatResult(
                "Please type a question before submitting.", source="error", error=True
            )

        question = question.strip()
        history = conversation_history or []
        length_mode = (length_mode or "long").lower()
        provider_choice = (model_provider or "auto").lower()

        # ------------------------------------------------------------------ #
        # TIER 1: Search Uploaded Notes if explicitly asked about documents
        # ------------------------------------------------------------------ #
        if uploaded_context and any(
            w in question.lower()
            for w in ("uploaded", "notes", "lecture", "pdf", "page", "slide", "chapter in my")
        ):
            return self._offline_from_notes(question, uploaded_context, uploaded_pages)

        # ------------------------------------------------------------------ #
        # Check Local Topic Resolution First
        # ------------------------------------------------------------------ #
        topic = kb.resolve_topic_from_context(question, history)
        is_curriculum_query = bool(topic) or any(
            w in question.lower()
            for w in (
                "practice question", "exam question", "sorting", "sort",
                "vs", "compare", "difference between", "how it works",
                "pseudocode", "complexity", "worst case", "worst-case",
                "normalization", "acid", "process", "thread", "deadlock",
                "tcp", "udp", "http", "dijkstra", "avl", "heap", "bfs", "dfs",
                "paging", "virtual memory", "scheduling", "osi", "oop", "dfa",
                "nfa", "turing", "a*", "8085", "concurrency", "sdlc", "rsa"
            )
        )

        # If user explicitly requests an external AI provider OR has a custom key
        force_external = provider_choice in ("openai", "gemini", "groq") or bool(custom_api_key)

        # If curriculum match and not forcing external AI, prioritize verified local curriculum notes
        if is_curriculum_query and not force_external and self._effective_provider == "offline":
            answer_text = kb.answer_query(
                question,
                history=history,
                subject=subject,
                uploaded_context=uploaded_context,
                length_mode=length_mode,
            )
            return AIChatResult(
                answer=answer_text,
                source="tier1_course_content",
                grounded_in_upload=bool(uploaded_context),
            )

        # ------------------------------------------------------------------ #
        # TIER 2: Live AI Providers (OpenAI, Gemini, Groq)
        # ------------------------------------------------------------------ #
        active_provider = provider_choice if provider_choice != "auto" else self._effective_provider

        # 1. Try OpenAI
        if active_provider == "openai" or (provider_choice == "auto" and (custom_api_key or self.openai_api_key)):
            key = custom_api_key or self.openai_api_key
            if key:
                res = self._call_openai(
                    question, history, uploaded_context, uploaded_pages, subject=subject,
                    length_mode=length_mode, api_key=key
                )
                if not res.error:
                    return res

        # 2. Try Gemini
        if active_provider == "gemini" or (provider_choice == "auto" and (custom_api_key or self.gemini_api_key)):
            key = custom_api_key or self.gemini_api_key
            if key:
                res = self._call_gemini(
                    question, history, uploaded_context, uploaded_pages, subject=subject,
                    length_mode=length_mode, api_key=key
                )
                if not res.error:
                    return res

        # 3. Try Groq
        if active_provider == "groq" or (provider_choice == "auto" and (custom_api_key or self.groq_api_key)):
            key = custom_api_key or self.groq_api_key
            if key:
                res = self._call_groq(
                    question, history, uploaded_context, uploaded_pages, subject=subject,
                    length_mode=length_mode, api_key=key
                )
                if not res.error:
                    return res

        # ------------------------------------------------------------------ #
        # TIER 3: Universal Local Academic Knowledge Engine Fallback
        # ------------------------------------------------------------------ #
        # Handles ANY question across all subjects in the chosen length mode
        answer_text = kb.answer_query(
            question,
            history=history,
            subject=subject,
            uploaded_context=uploaded_context,
            length_mode=length_mode,
        )

        source_label = "tier1_course_content" if is_curriculum_query else "tier2_general_ai"
        return AIChatResult(
            answer=answer_text,
            source=source_label,
            grounded_in_upload=bool(uploaded_context),
        )

    def _build_system_prompt(self, subject: str, length_mode: str) -> str:
        length_instructions = {
            "very_short": "Keep the answer VERY SHORT and concise (under 70 words, 1-3 sentences or crisp bullet points). Give the direct definition, primary formula or complexity, and key takeaway.",
            "short": "Provide a SHORT, focused academic response (~150 words, 1-2 compact paragraphs) covering the definition, working mechanism, and essential formula/complexity.",
            "long": "Provide a COMPREHENSIVE university-level answer (~400 words) with structured sections: 1) Definition, 2) Step-by-Step Working Mechanism, 3) Example / Code Snippet, 4) Complexity Analysis, and 5) TU Board Exam Tips.",
            "very_long": "Provide a MASTER ACADEMIC STUDY GUIDE (~850+ words) tailored for Tribhuvan University BSc CSIT board examinations. Include: 1) Formal Theoretical Foundations, 2) Step-by-Step Mechanism & Architecture, 3) Full Runnable Code / Pseudocode, 4) Asymptotic Complexity Proof, 5) TU Board Exam Marking Scheme & Common Pitfalls, and 6) Three Self-Test Practice Questions with Rubrics.",
        }
        instruction = length_instructions.get(length_mode.lower(), length_instructions["long"])
        return (
            f"You are an expert Tribhuvan University (TU) BSc CSIT academic professor teaching {subject}. "
            f"Provide student-friendly, precise, mathematically sound explanations. "
            f"Strictly adhere to the following length requirement: {instruction} "
            f"Format using clean GitHub-style Markdown."
        )

    # ------------------------------------------------------------------ #
    # Live Provider Calls
    # ------------------------------------------------------------------ #
    def _call_openai(
        self,
        question: str,
        history: List[dict],
        context: Optional[str],
        pages: Optional[list],
        subject: str,
        length_mode: str = "long",
        api_key: Optional[str] = None,
    ) -> AIChatResult:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key or self.openai_api_key)
            system_prompt = self._build_system_prompt(subject, length_mode)
            messages = [{"role": "system", "content": system_prompt}]

            for m in history[-4:]:
                messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})

            user_content = question
            if context:
                user_content = f"CONTEXT FROM LECTURE NOTES:\n{context[:6000]}\n\nQUESTION:\n{question}"
            messages.append({"role": "user", "content": user_content})

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
            )
            text = response.choices[0].message.content or ""
            text += f"\n\n---\n*Answer generated by OpenAI ChatGPT (GPT-4o mini) · Mode: {length_mode.title()}*"
            return AIChatResult(answer=text, source="openai", grounded_in_upload=bool(context))
        except Exception:
            return AIChatResult(answer="", source="error", error=True)

    def _call_gemini(
        self,
        question: str,
        history: List[dict],
        context: Optional[str],
        pages: Optional[list],
        subject: str,
        length_mode: str = "long",
        api_key: Optional[str] = None,
    ) -> AIChatResult:
        try:
            from google import genai

            client = genai.Client(api_key=api_key or self.gemini_api_key)
            system_prompt = self._build_system_prompt(subject, length_mode)

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
            text += f"\n\n---\n*Answer generated by Google Gemini (2.5 Flash) · Mode: {length_mode.title()}*"
            return AIChatResult(answer=text, source="gemini", grounded_in_upload=bool(context))
        except Exception:
            return AIChatResult(answer="", source="error", error=True)

    def _call_groq(
        self,
        question: str,
        history: List[dict],
        context: Optional[str],
        pages: Optional[list],
        subject: str,
        length_mode: str = "long",
        api_key: Optional[str] = None,
    ) -> AIChatResult:
        try:
            from groq import Groq

            client = Groq(api_key=api_key or self.groq_api_key)
            system_prompt = self._build_system_prompt(subject, length_mode)
            messages = [{"role": "system", "content": system_prompt}]

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
            text += f"\n\n---\n*Answer generated by Groq (Llama 3.3 70B) · Mode: {length_mode.title()}*"
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
            "*TU CSIT Pulse · Document Retrieval*",
        ]
        return AIChatResult(
            answer="\n".join(lines),
            source="offline",
            grounded_in_upload=True,
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

        # 1. Try OpenAI if configured
        if self._effective_provider == "openai" or self.openai_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                prompt = (
                    f"You are a Tribhuvan University BSc CSIT professor for {subject}. "
                    f"Create a practice exam paper with exactly {num_questions} questions, "
                    f"including model answers, mark distributions (e.g. [6 Marks]), and step-by-step solutions.\n\n"
                    f"Context:\n{uploaded_context[:8000] if uploaded_context else 'Standard TU CSIT Syllabus'}"
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                if resp.choices[0].message.content:
                    return resp.choices[0].message.content + "\n\n---\n*Generated by OpenAI ChatGPT (Server-side)*"
            except Exception:
                pass

        # 2. Try Gemini
        if self._effective_provider == "gemini" or self.gemini_api_key:
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

        # 3. Try Groq
        if self._effective_provider == "groq" or self.groq_api_key:
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
            "*TU CSIT Pulse · Offline Revision Bank*",
        ]
        return "\n".join(lines)


# Singleton server-side backend instance
chat_backend = AIChatBackend()
