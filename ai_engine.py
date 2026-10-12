import os
import json
from typing import Optional, Generator


class AIEngine:
    def __init__(self, provider: str = "demo", api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("API_KEY")

    def answer_question(self, question: str, context: str, subject: str = "General CSIT") -> str:
        """
        Answers a user question based strictly on the uploaded lecture context.
        """
        system_prompt = f"""
You are an expert BSc CSIT academic tutor assisting a student at Tribhuvan University.
Subject: {subject}.

Your goal is to answer the student's question clearly, academically, and accurately based on the provided lecture notes.
Rules:
1. Always ground your explanation in the lecture content provided.
2. If code examples clarify the answer, write clean C, C++, or Python code with inline comments.
3. Highlight key definitions, time complexities (Big-O), and architectural concepts.
4. If the provided notes do not contain the answer, state that clearly and provide general CSIT knowledge.
"""
        user_prompt = f"""
### LECTURE NOTES CONTEXT:
{context[:12000]}

### STUDENT QUESTION:
{question}
"""
        return self._generate(system_prompt, user_prompt)

    def generate_exam_prep(self, context: str, subject: str = "General CSIT", num_questions: int = 5) -> str:
        """
        Generates Tribhuvan University (TU) exam-style practice questions with model answers.
        """
        system_prompt = f"""
You are a senior BSc CSIT professor at Prime College designing a practice exam sheet for the subject: {subject}.
Rules:
1. Generate {num_questions} high-yield exam questions based on the uploaded lecture notes.
2. Include a mix of:
   - Conceptual Definitions (Short questions)
   - Analytical & Coding questions (with sample C++ or Python code)
   - Long architectural / algorithm analysis questions
3. For each question, provide a detailed 'Model Answer' and 'Mark Allocation / Key Points'.
Format in clean Markdown with clear headings and bullet points.
"""
        user_prompt = f"""
### LECTURE NOTES CONTENT:
{context[:12000]}

Please generate the practice exam sheet now.
"""
        return self._generate(system_prompt, user_prompt)

    def generate_summary_flashcards(self, context: str, subject: str = "General CSIT") -> str:
        """
        Generates rapid revision notes, key concepts, formulas, and flashcards.
        """
        system_prompt = f"""
You are an AI study coach helping a BSc CSIT student prepare for final exams in {subject}.
From the provided lecture notes:
1. Summarize the Core Concepts in concise bullet points.
2. Extract Key Definitions & Formulas.
3. List important Time & Space Complexities (if applicable).
4. Create 5 Revision Flashcards formatted as 'Q: ... | A: ...'.
"""
        user_prompt = f"""
### LECTURE NOTES:
{context[:12000]}
"""
        return self._generate(system_prompt, user_prompt)

    def _generate(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "gemini":
            return self._call_gemini(system_prompt, user_prompt)
        elif self.provider == "groq":
            return self._call_groq(system_prompt, user_prompt)
        else:
            return self._mock_demo_response(user_prompt)

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}",
            )
            return response.text
        except Exception as e:
            return f"❌ Gemini API Error: {str(e)}\n\nPlease ensure your Gemini API key is valid, or switch to 'Demo Mode' in the sidebar."

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
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"❌ Groq API Error: {str(e)}\n\nPlease ensure your Groq API key is valid, or switch to 'Demo Mode' in the sidebar."

    def _mock_demo_response(self, user_prompt: str) -> str:
        return """### 🎓 [Demo Mode Response]
*You are currently running in **Demo Mode** without an active API key. To enable live AI, choose **Gemini** or **Groq** in the sidebar and paste your free key!*

#### Sample CSIT Concept Breakdown:
- **Topic Context**: Binary Trees & Traversal Techniques in Data Structures & Algorithms.
- **Key Definition**: A binary tree is a hierarchical data structure in which each node has at most two children, referred to as the left child and right child.
- **Traversals**:
  1. **In-order (Left, Root, Right)**: Produces sorted order for Binary Search Trees (BST).
  2. **Pre-order (Root, Left, Right)**: Useful for creating node copies.
  3. **Post-order (Left, Right, Root)**: Useful for bottom-up deletion.
- **Time Complexity**:
  - Search / Insert / Delete in balanced BST: $\\mathcal{O}(\\log n)$
  - Worst case (skewed tree): $\\mathcal{O}(n)$

```cpp
// C++ Node Representation
struct Node {
    int data;
    Node* left;
    Node* right;
    Node(int val) : data(val), left(nullptr), right(nullptr) {}
};
```
"""
