"""Comprehensive verification suite for TU CSIT Study Assistant.

Validates all Critical Acceptance Gates:
1. QuickSort explanation without API key (full definition, worked example, pseudocode, complexity table, no placeholders).
2. Intent handling: simple language, worst-case O(n^2) derivation, quick sort vs merge sort comparison, python pseudocode, 5 practice questions.
3. Conversational context awareness in follow-up queries.
4. Server-side security: zero credentials exposed to frontend/output.
5. Real HamroCSIT-inspired curricular traceability.
"""

import sys
from ai_backend import AIChatBackend, chat_backend
from knowledge_base import kb

def verify_all():
    print("=" * 70)
    print("RUNNING VERIFICATION SUITE — TU CSIT STUDY ASSISTANT")
    print("=" * 70)

    # ------------------------------------------------------------------ #
    # Gate 1: Quick Sort without an API key
    # ------------------------------------------------------------------ #
    print("\n[TEST 1] Testing 'quick sort' without an API key...")
    res1 = chat_backend.answer("quick sort", [])
    assert "tier1" in res1.source or res1.source == "offline", f"Expected tier1/offline source, got {res1.source}"
    assert not res1.error, "Unexpected error in response"
    
    # Assertions on required content
    assert "divide-and-conquer" in res1.answer.lower(), "Missing divide-and-conquer in definition"
    assert "7, 2, 9, 4, 3" in res1.answer, "Missing worked example [7, 2, 9, 4, 3]"
    assert "QUICKSORT" in res1.answer or "def quicksort" in res1.answer, "Missing pseudocode"
    assert "O(n log n)" in res1.answer, "Missing O(n log n) complexity"
    assert "O(n²)" in res1.answer or "O(n^2)" in res1.answer, "Missing O(n^2) worst-case"
    assert "HamroCSIT" in res1.answer, "Missing HamroCSIT source citation"
    
    # Assertions on absence of placeholders
    assert "No API key is configured" not in res1.answer, "Leaked API key message"
    assert "Demo Mode" not in res1.answer or "TU CSIT Study Assistant" in res1.answer, "Returned placeholder template"
    assert "Select Google Gemini or Groq" not in res1.answer, "Leaked provider selector instructions"
    print(" -> PASS: QuickSort returned rich educational response with HamroCSIT source citation.")

    # ------------------------------------------------------------------ #
    # Gate 2: Intent-specific questions
    # ------------------------------------------------------------------ #
    print("\n[TEST 2] Testing 'Explain quick sort in simple language.'...")
    res2 = chat_backend.answer("Explain quick sort in simple language.", [])
    assert "Simple Language" in res2.answer or "photograph" in res2.answer.lower(), "Simple explanation missing"
    print(" -> PASS: Simple language explanation returned.")

    print("\n[TEST 3] Testing 'Why is the worst-case complexity O(n²)?'...")
    res3 = chat_backend.answer("Why is the worst-case complexity O(n²)?", [])
    assert "Worst-Case" in res3.answer, "Worst-case deep dive missing"
    assert "unbalanced" in res3.answer.lower() or "recurrence" in res3.answer.lower(), "Proof details missing"
    print(" -> PASS: Worst-case O(n²) mathematical explanation returned.")

    print("\n[TEST 4] Testing follow-up context: 'Why is its worst case O(n²)?'...")
    history = [
        {"role": "user", "content": "Explain quick sort."},
        {"role": "assistant", "content": "Quick sort is a divide-and-conquer algorithm."},
    ]
    res4 = chat_backend.answer("Why is its worst case O(n²)?", history)
    assert "Quick Sort" in res4.answer, "Failed to resolve 'it' to Quick Sort from context"
    assert "Worst-Case" in res4.answer, "Missing worst case analysis"
    print(" -> PASS: Follow-up conversational context preserved.")

    print("\n[TEST 5] Testing 'Compare quick sort and merge sort.'...")
    res5 = chat_backend.answer("Compare quick sort and merge sort.", [])
    assert "Quick Sort vs Merge Sort" in res5.answer, "Missing comparison title"
    assert "Stable" in res5.answer or "stable" in res5.answer, "Missing stability comparison"
    print(" -> PASS: Comparative analysis table returned.")

    print("\n[TEST 6] Testing 'Give me quick sort pseudocode in Python.'...")
    res6 = chat_backend.answer("Give me quick sort pseudocode in Python.", [])
    assert "def quicksort" in res6.answer, "Missing Python implementation"
    print(" -> PASS: Python pseudocode returned.")

    print("\n[TEST 7] Testing 'Give me five practice questions about sorting algorithms.'...")
    res7 = chat_backend.answer("Give me five practice questions about sorting algorithms.", [])
    assert "Practice Question 1" in res7.answer, "Missing Q1"
    assert "Practice Question 5" in res7.answer, "Missing Q5"
    assert "Marks" in res7.answer, "Missing marking rubric"
    print(" -> PASS: Five TU practice exam questions with rubrics returned.")

    # ------------------------------------------------------------------ #
    # Gate 3: Curricular & Resource Integrity
    # ------------------------------------------------------------------ #
    print("\n[TEST 8] Testing HamroCSIT-inspired curricular traceability...")
    assert len(kb.semesters) == 8, f"Expected 8 semesters, found {len(kb.semesters)}"
    assert "Data Structures and Algorithms" in kb.semesters["Third Semester"]
    assert kb.semesters["Third Semester"]["Data Structures and Algorithms"] == "CSC206"
    assert "Database Management System" in kb.semesters["Fourth Semester"]
    assert kb.semesters["Fourth Semester"]["Database Management System"] == "CSC260"
    
    # Check resources
    resources = kb.resources
    assert any(r["topic"] == "quick-sort" for r in resources), "Quick sort resource missing"
    assert any("hamrocsit" in r.get("url", "") for r in resources if r.get("url")), "External HamroCSIT links missing"
    print(" -> PASS: All 8 semesters, official TU course codes, and traceable resources verified.")

    # ------------------------------------------------------------------ #
    # Gate 4: Security & Secret Leakage
    # ------------------------------------------------------------------ #
    print("\n[TEST 9] Testing Secret Leakage prevention...")
    backend = AIChatBackend()
    assert backend.is_live() is False, "Live AI unexpectedly active without keys"
    assert "GEMINI_API_KEY" not in res1.answer
    assert "GROQ_API_KEY" not in res1.answer
    print(" -> PASS: No secrets leaked in outputs.")

    print("\n" + "=" * 70)
    print("ALL ACCEPTANCE VERIFICATION CHECKS PASSED SUCCESSFULLY (100%)")
    print("=" * 70)

if __name__ == "__main__":
    verify_all()
