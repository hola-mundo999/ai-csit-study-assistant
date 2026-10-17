import pytest

from ai_engine import AIEngine
from pdf_processor import chunk_text, extract_text_from_pdf


# --------------------------------------------------------------------- #
# PDF processor
# --------------------------------------------------------------------- #
def test_extract_empty_bytes_rejected():
    result = extract_text_from_pdf(b"")
    assert result["success"] is False
    assert result["error"]
    assert result["total_pages"] == 0


def test_chunk_text_splits_with_overlap():
    text = "x" * 1000
    chunks = chunk_text(text, chunk_size=400, overlap=50)
    assert len(chunks) == 3
    assert chunks[0] == chunks[1][:400]


def test_chunk_text_empty_returns_empty():
    assert chunk_text("") == []


def test_chunk_text_smaller_than_size():
    assert chunk_text("hello") == ["hello"]


# --------------------------------------------------------------------- #
# AI engine — Demo mode only (no API keys required)
# --------------------------------------------------------------------- #
@pytest.fixture
def engine():
    return AIEngine(provider="demo", api_key=None)


def test_demo_answer_is_deterministic(engine):
    r1 = engine.answer_question("What is Big-O complexity?", "context", subject="Data Structures & Algorithms")
    r2 = engine.answer_question("What is Big-O complexity?", "context", subject="Data Structures & Algorithms")
    assert r1 == r2
    assert len(r1) > 50


def test_demo_answer_mentions_demo_mode(engine):
    response = engine.answer_question("Tell me about trees", "context")
    assert "Demo Mode" in response


def test_demo_answer_rejects_empty_question(engine):
    assert engine.answer_question("", "context") == "Please ask a question before submitting."
    assert engine.answer_question("   ", "context") == "Please ask a question before submitting."


def test_demo_answer_varies_by_keyword(engine):
    complexity = engine.answer_question("What is the time complexity of binary search?", "context")
    code = engine.answer_question("Write a C++ function to reverse a linked list", "context")
    assert complexity != code


def test_demo_exam_prep_respects_num_questions(engine):
    sheet = engine.generate_exam_prep("context", subject="Algorithms", num_questions=3)
    assert "Question 1" in sheet
    assert "Question 4" not in sheet


def test_demo_flashcards_contains_structure(engine):
    summary = engine.generate_summary_flashcards("context", subject="DBMS")
    assert "Flashcards" in summary or "Core Concepts" in summary


def test_demo_routes_unknown_provider_falls_back_to_demo():
    engine = AIEngine(provider="weird_provider", api_key=None)
    assert "Demo Mode" in engine.answer_question("hello", "context")


# --------------------------------------------------------------------- #
# Context selection / page citations
# --------------------------------------------------------------------- #
def test_select_context_uses_pages(engine):
    pages = [
        {"page_num": 1, "text": "Binary Search is an O(log n) searching algorithm on sorted arrays."},
        {"page_num": 2, "text": "Breadth First Search uses a queue to traverse graphs level by level."},
    ]
    context, sources = engine._select_relevant_context("binary search time complexity", "", pages)
    assert "Page 1" in context
    assert 1 in sources


def test_select_context_ignores_irrelevant_pages(engine):
    pages = [
        {"page_num": 1, "text": "Binary Search is an O(log n) searching algorithm on sorted arrays."},
        {"page_num": 2, "text": "Unrelated cooking recipes for pasta and pizza."},
    ]
    context, sources = engine._select_relevant_context("binary search", "", pages)
    assert "Page 1" in context
    assert "Page 2" not in context


def test_select_context_falls_back_to_raw_text(engine):
    context, sources = engine._select_relevant_context("anything", "Raw document text about algorithms.", None)
    assert "Raw document text" in context
    assert sources == []


def test_select_context_respects_char_budget(engine):
    pages = [
        {"page_num": i, "text": f"Page {i} content about algorithms and data structures. " * 60}
        for i in range(1, 6)
    ]
    context, _ = engine._select_relevant_context("algorithms", "", pages, max_chars=500)
    assert len(context) <= 500
