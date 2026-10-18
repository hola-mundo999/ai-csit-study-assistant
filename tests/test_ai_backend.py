"""Unit and integration tests for server-side AIChatBackend."""

import os
import pytest

from ai_backend import AIChatBackend, chat_backend


def test_backend_defaults_to_offline_when_no_keys():
    # Ensure test environment has no keys
    b = AIChatBackend()
    assert b.is_live() is False
    assert "Offline" in b.provider_status_label()


def test_backend_answers_quicksort_thoroughly():
    res = chat_backend.answer("quick sort", [])
    assert res.source == "tier1_course_content"
    assert res.error is False
    # Check required educational content
    assert "divide-and-conquer" in res.answer.lower()
    assert "7, 2, 9, 4, 3" in res.answer
    assert "QUICKSORT" in res.answer or "quicksort" in res.answer
    assert "O(n log n)" in res.answer
    assert "O(n²)" in res.answer or "O(n^2)" in res.answer
    assert "No API key is configured" not in res.answer
    assert "Demo Mode Active" not in res.answer
    assert "HamroCSIT" in res.answer


def test_backend_intent_simple_language():
    res = chat_backend.answer("Explain quick sort in simple language.", [])
    assert "Simple Language" in res.answer or "photograph" in res.answer.lower()
    assert res.source == "tier1_course_content"


def test_backend_tier2_fallback_when_outside_curriculum():
    res = chat_backend.answer("Explain quantum annealing in superconducting circuits", [])
    assert "tier2" in res.source
    assert "Notice" in res.answer
    assert "No sufficiently relevant answer was found in the available local HamroCSIT course notes" in res.answer


def test_backend_intent_worst_case():
    res = chat_backend.answer("Why is the worst-case complexity O(n²)?", [])
    assert "Worst-Case" in res.answer
    assert "unbalanced" in res.answer.lower() or "recurrence" in res.answer.lower()


def test_backend_intent_comparison():
    res = chat_backend.answer("Compare quick sort and merge sort.", [])
    assert "Quick Sort vs Merge Sort" in res.answer
    assert "Stable" in res.answer or "stable" in res.answer


def test_backend_intent_code():
    res = chat_backend.answer("Give me quick sort pseudocode in Python.", [])
    assert "def quicksort" in res.answer
    assert "partition" in res.answer


def test_backend_intent_five_practice_questions():
    res = chat_backend.answer("Give me five practice questions about sorting algorithms.", [])
    assert "Practice Question 1" in res.answer
    assert "Practice Question 5" in res.answer
    assert "Marks" in res.answer


def test_backend_followup_preserves_conversation_context():
    history = [
        {"role": "user", "content": "Explain quick sort."},
        {"role": "assistant", "content": "Quick sort is a divide-and-conquer algorithm."},
    ]
    res = chat_backend.answer("Why is its worst case O(n²)?", history)
    assert "Quick Sort" in res.answer
    assert "Worst-Case" in res.answer


def test_backend_no_secrets_leaked_in_output():
    res = chat_backend.answer("quick sort", [])
    assert "GEMINI_API_KEY" not in res.answer
    assert "GROQ_API_KEY" not in res.answer
    assert "api_key" not in res.answer.lower() or "api key" not in res.answer.lower()


def test_backend_empty_query():
    res = chat_backend.answer("", [])
    assert res.error is True
    assert "Please type" in res.answer


def test_backend_generate_exam_prep_offline():
    sheet = chat_backend.generate_exam_prep("Data Structures and Algorithms", num_questions=5)
    assert "Practice Question" in sheet
    assert "Marks" in sheet


def test_backend_generate_flashcards_offline():
    cards = chat_backend.generate_flashcards("Data Structures and Algorithms")
    assert "Flashcard" in cards
    assert "Quick Sort" in cards
