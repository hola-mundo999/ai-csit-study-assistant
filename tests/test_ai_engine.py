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
# AI engine — Educational offline mode (no API keys required)
# --------------------------------------------------------------------- #
@pytest.fixture
def engine():
    return AIEngine(provider="demo", api_key=None)


def test_demo_answer_is_deterministic(engine):
    r1 = engine.answer_question("What is Big-O complexity?", "context", subject="Data Structures & Algorithms")
    r2 = engine.answer_question("What is Big-O complexity?", "context", subject="Data Structures & Algorithms")
    assert r1 == r2
    assert len(r1) > 50


def test_demo_answer_rejects_empty_question(engine):
    assert engine.answer_question("", "context") == "Please ask a question before submitting."
    assert engine.answer_question("   ", "context") == "Please ask a question before submitting."


def test_demo_answer_varies_by_keyword(engine):
    complexity = engine.answer_question("What is the time complexity of binary search?", "context")
    code = engine.answer_question("Write a C++ function to reverse a linked list", "context")
    assert complexity != code


def test_demo_exam_prep_contains_questions(engine):
    sheet = engine.generate_exam_prep("context", subject="Algorithms", num_questions=5)
    assert "Practice Question" in sheet or "Question" in sheet
    assert "Mark" in sheet or "Solution" in sheet


def test_demo_flashcards_contains_structure(engine):
    summary = engine.generate_summary_flashcards("context", subject="DBMS")
    assert "Flashcard" in summary or "Revision" in summary


def test_unknown_provider_falls_back_gracefully():
    engine = AIEngine(provider="weird_provider", api_key=None)
    res = engine.answer_question("quick sort", "context")
    assert "Quick Sort" in res
    assert "No API key is configured" not in res


# --------------------------------------------------------------------- #
# Critical Acceptance Tests: QuickSort & Intent Handling
# --------------------------------------------------------------------- #
def test_quicksort_regression_no_placeholder(engine):
    """Test 1: QuickSort must return a real educational explanation without placeholders."""
    res = engine.answer_question("quick sort", "")
    # Must explain the algorithm
    assert "divide-and-conquer" in res.lower() or "partition" in res.lower()
    # Must include example
    assert "7, 2, 9, 4, 3" in res or "example" in res.lower()
    # Must include pseudocode or code
    assert "QUICKSORT" in res or "def quicksort" in res
    # Must include complexity
    assert "O(n log n)" in res
    assert "O(n²)" in res or "O(n^2)" in res
    # Must NOT contain developer-oriented placeholder text
    assert "No API key is configured" not in res
    assert "Demo Mode Active" not in res
    assert "Upload a lecture PDF in the sidebar so answers are drawn" not in res


def test_quicksort_simple_language(engine):
    """Test: Explain in simple language adapts response."""
    res = engine.answer_question("Explain quick sort in simple language.", "")
    assert "Simple Language" in res or "photograph" in res.lower() or "benchmark" in res.lower()


def test_quicksort_worst_case_explanation(engine):
    """Test: Explaining worst case time complexity."""
    res = engine.answer_question("Why is the worst-case complexity O(n²)?", "")
    assert "Worst-Case" in res
    assert "O(n²)" in res or "O(n^2)" in res
    assert "unbalanced" in res.lower() or "recurrence" in res.lower() or "pivot" in res.lower()


def test_quicksort_followup_context(engine):
    """Test: Follow-up question uses context from conversation history."""
    history = [
        {"role": "user", "content": "Explain quick sort."},
        {"role": "assistant", "content": "Quick sort is a divide-and-conquer algorithm."},
    ]
    res = engine.answer_question("Why is its worst case O(n²)?", history=history)
    assert "Quick Sort" in res
    assert "Worst-Case" in res


def test_compare_quick_and_merge_sort(engine):
    """Test: Comparing quick sort and merge sort."""
    res = engine.answer_question("Compare quick sort and merge sort.", "")
    assert "Quick Sort vs Merge Sort" in res or "Comparison" in res
    assert "Merge Sort" in res
    assert "stable" in res.lower()


def test_sorting_practice_questions(engine):
    """Test: Practice questions about sorting algorithms."""
    res = engine.answer_question("Give me five practice questions about sorting algorithms.", "")
    assert "Practice Question 1" in res
    assert "Practice Question 5" in res
    assert "Marks" in res


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
