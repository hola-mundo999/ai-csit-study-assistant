import os
import re
from typing import Optional

from pdf_processor import chunk_text


class AIEngine:
    """
    Academic Q&A engine for BSc CSIT lecture notes.

    Routes generation between Google Gemini, Groq, and a built-in deterministic
    Demo Mode that requires no API key. All providers are grounded in the
    uploaded lecture context; Demo Mode responses are generated from the
    question and subject so students can explore the app offline.
    """

    DEMO_TOPICS = {
        "complexity": (
            "Time & Space Complexity",
            "Big-O notation describes the worst-case growth of an algorithm's "
            "running time or memory usage as the input size grows.",
        ),
        "code": (
            "Code Example",
            "Below is a clean, commented implementation you can adapt for your "
            "CSIT lab assignments.",
        ),
        "definition": (
            "Key Definition",
            "Here is the precise academic definition used in TU BSc CSIT courses.",
        ),
    }

    def __init__(self, provider: str = "demo", api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def answer_question(
        self,
        question: str,
        context: str,
        subject: str = "General CSIT",
        pages: Optional[list] = None,
    ) -> str:
        """
        Answers a student question strictly grounded in the lecture context.

        Parameters
        ----------
        question : str
            The student's question.
        context : str
            Raw extracted text from the uploaded document.
        subject : str
            Current CSIT subject context.
        pages : list of dict, optional
            Per-page text extracted from the PDF, used for page citations.
        """
        if not question or not question.strip():
            return "Please ask a question before submitting."

        relevant_context, sources = self._select_relevant_context(
            question, context, pages
        )

        if self.provider == "gemini":
            return self._call_gemini(
                self._qa_system_prompt(subject, bool(sources)),
                self._qa_user_prompt(question, relevant_context, sources),
            )
        if self.provider == "groq":
            return self._call_groq(
                self._qa_system_prompt(subject, bool(sources)),
                self._qa_user_prompt(question, relevant_context, sources),
            )
        return self._demo_answer(question, relevant_context, subject, sources)

    def generate_exam_prep(
        self,
        context: str,
        subject: str = "General CSIT",
        num_questions: int = 5,
        pages: Optional[list] = None,
    ) -> str:
        """Generates TU-style practice questions with model answers and rubrics."""
        num_questions = max(3, min(10, int(num_questions)))
        relevant_context, sources = self._select_relevant_context(
            "exam paper generation", context, pages, max_chars=10000
        )

        system_prompt = f"""
You are a senior BSc CSIT professor at Prime College designing a practice exam
sheet for the subject: {subject}.

Rules:
1. Generate exactly {num_questions} high-yield exam questions based strictly on
   the lecture notes provided below.
2. Include a mix of:
   - Conceptual definition questions
   - Analytical questions
   - Coding questions (sample C++, C, or Python code with comments)
   - Long algorithm / architecture analysis questions
3. For every question include:
   - A detailed "Model Answer"
   - "Mark Allocation / Key Points" showing how marks are distributed
4. Where the notes support it, cite the page number the material came from.
Format in clean Markdown with clear headings and bullet points.
"""
        user_prompt = f"""
### LECTURE NOTES CONTENT (with page references):
{relevant_context}

### SOURCE PAGES:
{", ".join(str(p) for p in sources) if sources else "Not available (no document uploaded)"}

### NUMBER OF QUESTIONS:
{num_questions}

Please generate the practice exam sheet now.
"""
        if self.provider == "gemini":
            return self._call_gemini(system_prompt, user_prompt)
        if self.provider == "groq":
            return self._call_groq(system_prompt, user_prompt)
        return self._demo_exam_prep(subject, num_questions)

    def generate_summary_flashcards(
        self,
        context: str,
        subject: str = "General CSIT",
        pages: Optional[list] = None,
    ) -> str:
        """Generates rapid revision notes, definitions, formulas, and flashcards."""
        relevant_context, sources = self._select_relevant_context(
            "revision summary", context, pages, max_chars=10000
        )

        system_prompt = f"""
You are an AI study coach helping a BSc CSIT student prepare for final exams in
{subject}. From the provided lecture notes:

1. Summarize the Core Concepts in concise bullet points.
2. Extract Key Definitions & Formulas.
3. List important Time & Space Complexities (if applicable).
4. Create 5 Revision Flashcards formatted as 'Q: ... | A: ...'.
5. Where helpful, reference the page number the material came from.
"""
        user_prompt = f"""
### LECTURE NOTES (with page references):
{relevant_context}

### SOURCE PAGES:
{", ".join(str(p) for p in sources) if sources else "Not available (no document uploaded)"}

SUBJECT: {subject}
"""
        if self.provider == "gemini":
            return self._call_gemini(system_prompt, user_prompt)
        if self.provider == "groq":
            return self._call_groq(system_prompt, user_prompt)
        return self._demo_flashcards(subject)

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
        """
        Selects the most relevant portions of the document for the question.

        Splits the document into overlapping chunks (one per page when page
        data is available), scores each chunk by keyword overlap with the
        question, and returns the top chunks within the character budget,
        annotated with page numbers for citations.

        Returns (context_string, list_of_page_numbers).
        """
        query_tokens = set(self._tokenize(question))
        if not query_tokens:
            return context[:max_chars], []

        chunk_entries = []  # (chunk_text, page_num_or_None)

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
            # Slight boost for chunks containing multiple distinct query terms
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
                # First relevant chunk alone exceeds the budget: truncate it.
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
    # Providers
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
            return (
                f"❌ Gemini API Error: {e}\n\n"
                "Check your API key in the sidebar, or switch to Demo Mode."
            )

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
            return (
                f"❌ Groq API Error: {e}\n\n"
                "Check your API key in the sidebar, or switch to Demo Mode."
            )

    # ------------------------------------------------------------------ #
    # Demo Mode (deterministic, no API key required)
    # ------------------------------------------------------------------ #
    def _demo_answer(self, question: str, context: str, subject: str, sources: list) -> str:
        q_lower = question.lower()
        topic_key = "definition"
        if any(k in q_lower for k in ("complexity", "big-o", "time ", "space ", "o(")):
            topic_key = "complexity"
        elif any(k in q_lower for k in ("code", "implement", "write a", "program", "function")):
            topic_key = "code"

        topic_title, topic_body = self.DEMO_TOPICS[topic_key]

        lines = [
            "### 🎓 [Demo Mode]",
            "",
            "*No API key is configured. This is a deterministic preview response "
            "grounded in CSIT fundamentals. Select **Google Gemini** or **Groq** "
            "in the sidebar and paste your free key for live, context-aware AI.*",
            "",
            f"#### {topic_title}",
            topic_body,
            "",
            "**Your question:** " + question,
            "",
            "#### Subject context",
            f"- **Subject:** {subject}",
        ]

        if sources:
            lines.append(f"- **Source pages referenced:** {', '.join(map(str, sources))}")
        lines.append(
            "- **Note:** Upload a lecture PDF in the sidebar so answers are drawn "
            "from your actual course material."
        )

        if topic_key == "code":
            lines += [
                "",
                "```cpp",
                "// Example: Binary Search (C++)",
                "int binarySearch(int arr[], int n, int target) {",
                "    int left = 0, right = n - 1;",
                "    while (left <= right) {",
                "        int mid = left + (right - left) / 2;",
                "        if (arr[mid] == target) return mid;",
                "        if (arr[mid] < target) left = mid + 1;",
                "        else right = mid - 1;",
                "    }",
                "    return -1; // not found",
                "}",
                "```",
                "",
                "Time Complexity: O(log n) · Space Complexity: O(1)",
            ]

        lines += ["", "---", "*TU CSIT Study Assistant · Demo Mode*"]

        return "\n".join(lines)

    def _demo_exam_prep(self, subject: str, num_questions: int) -> str:
        questions = [
            {
                "q": "Define Abstract Data Type (ADT) with an example.",
                "a": "An ADT is a mathematical model for data types where the data type is defined by its behavior from the point of view of a user, specifically in terms of possible values, possible operations on data of this type, and the behavior of these operations. Example: Stack (push, pop, peek).",
                "marks": "5 marks",
            },
            {
                "q": "Explain Binary Search with time complexity analysis.",
                "a": "Binary Search works on a sorted array by repeatedly dividing the search interval in half. Compare the target with the middle element and eliminate half the search space each step. Time Complexity: O(log n); Space Complexity: O(1) iterative.",
                "marks": "7 marks",
            },
            {
                "q": "Write a C++ function to insert a node at the end of a singly linked list.",
                "a": "```cpp\nstruct Node { int data; Node* next; };\nvoid insertAtEnd(Node*& head, int value) {\n    Node* newNode = new Node{value, nullptr};\n    if (!head) { head = newNode; return; }\n    Node* temp = head;\n    while (temp->next) temp = temp->next;\n    temp->next = newNode;\n}\n```",
                "marks": "8 marks",
            },
        ]

        lines = [
            f"### 🎓 [Demo Mode] TU-Style Practice Exam Sheet — {subject}",
            "",
            "*Live AI exam generation requires a Gemini or Groq API key. The questions "
            "below are CSIT-aligned samples for self-practice.*",
            "",
        ]

        for i, item in enumerate(questions[:num_questions], 1):
            lines += [
                f"### Question {i} [{item['marks']}]",
                "",
                item["q"],
                "",
                "**Model Answer:**",
                item["a"],
                "",
            ]

        lines += ["---", "*TU CSIT Study Assistant · Demo Mode*"]

        return "\n".join(lines)

    def _demo_flashcards(self, subject: str) -> str:
        cards = [
            ("What is a binary tree?", "A hierarchical data structure where each node has at most two children: left and right."),
            ("BST in-order traversal output?", "Produces nodes in ascending/sorted order."),
            ("Balanced BST search complexity?", "O(log n); worst case (skewed) O(n)."),
            ("Primary purpose of normalization in DBMS?", "Reduce data redundancy and improve data integrity."),
            ("TCP vs UDP key difference?", "TCP is connection-oriented and reliable; UDP is connectionless and faster."),
        ]
        lines = [
            f"### ⚡ [Demo Mode] Rapid Revision — {subject}",
            "",
            "*Live summarization requires a Gemini or Groq API key. Flashcards below "
            "cover core CSIT fundamentals.*",
            "",
            "### Core Concepts",
            "- Data Structures: organization of data for efficient access and modification.",
            "- Algorithms: step-by-step procedures for solving computational problems.",
            "- Database Management: structured storage, retrieval, and integrity of data.",
            "- Operating Systems: resource management between hardware and applications.",
            "- Computer Networks: data exchange between computing devices.",
            "",
            "### Key Definitions & Formulas",
            "- **Big-O Notation**: upper bound on algorithm growth rate.",
            "- **Recursion**: a function that calls itself with a base case.",
            "- **ACID Properties**: Atomicity, Consistency, Isolation, Durability.",
            "",
            "### Revision Flashcards",
        ]
        for i, (q, a) in enumerate(cards, 1):
            lines.append(f"{i}. Q: {q} | A: {a}")

        lines += ["", "---", "*TU CSIT Study Assistant · Demo Mode*"]

        return "\n".join(lines)

    def _qa_system_prompt(self, subject: str, has_sources: bool) -> str:
        source_rule = (
            "Cite the page number in brackets (e.g., [Page 3]) whenever you use "
            "material from a specific page."
        ) if has_sources else (
            "No document has been uploaded yet; answer from general CSIT knowledge "
            "and clearly say so."
        )
        return f"""
You are an expert BSc CSIT academic tutor assisting a student at Tribhuvan
University. Subject: {subject}.

Rules:
1. Answer clearly, academically, and accurately, grounded in the lecture notes.
2. {source_rule}
3. If code examples clarify the answer, write clean C, C++, or Python code with inline comments.
4. Highlight key definitions, time complexities (Big-O), and architectural concepts.
5. If the provided notes do not contain the answer, say so and offer general CSIT knowledge.
"""

    def _qa_user_prompt(self, question: str, context: str, sources: list) -> str:
        return f"""
### LECTURE NOTES CONTEXT:
{context}

### SOURCE PAGES:
{", ".join(map(str, sources)) if sources else "None"}

### STUDENT QUESTION:
{question}
"""
