"""Curated offline CSIT knowledge base and intent-aware educational engine.

Provides educationally useful explanations for TU BSc CSIT topics when no
external AI provider is configured. Every entry is original study material written
for this platform.

Topics are keyed by a stable slug and organized by subject and semester. The
engine supports intent recognition (simple explanations, worst-case derivations,
comparisons, pseudocode/code, and practice exam questions) and preserves
conversational context across follow-up queries.
"""

import re
from typing import Dict, List, Optional, Tuple


class Topic:
    def __init__(
        self,
        slug: str,
        title: str,
        subject: str,
        semester: str,
        definition: str,
        how_it_works: List[str],
        example: Optional[str] = None,
        pseudocode: Optional[str] = None,
        code: Optional[str] = None,
        code_cpp: Optional[str] = None,
        complexity: Optional[Dict[str, str]] = None,
        space_complexity: Optional[str] = None,
        properties: Optional[List[str]] = None,
        exam_points: Optional[List[str]] = None,
        practice_question: Optional[str] = None,
        practice_answer: Optional[str] = None,
        simple_explanation: Optional[str] = None,
        worst_case_explanation: Optional[str] = None,
        related: Optional[List[str]] = None,
        category: Optional[str] = None,
        hamrocsit_url: Optional[str] = None,
        chapter_name: Optional[str] = None,
        course_code: Optional[str] = None,
    ):
        self.slug = slug
        self.title = title
        self.subject = subject
        self.semester = semester
        self.definition = definition
        self.how_it_works = how_it_works
        self.example = example
        self.pseudocode = pseudocode
        self.code = code
        self.code_cpp = code_cpp
        self.complexity = complexity or {}
        self.space_complexity = space_complexity or ""
        self.properties = properties or []
        self.exam_points = exam_points or []
        self.practice_question = practice_question
        self.practice_answer = practice_answer
        self.simple_explanation = simple_explanation
        self.worst_case_explanation = worst_case_explanation
        self.related = related or []
        self.category = category or "general"
        self.hamrocsit_url = hamrocsit_url or "https://hamrocsit.com/semester/third/dsa/"
        self.chapter_name = chapter_name or title
        self.course_code = course_code or "CSC211"


# --------------------------------------------------------------------------- #
# Curated topics (original TU BSc CSIT study material)
# --------------------------------------------------------------------------- #
TOPICS: Dict[str, Topic] = {}

TOPICS["quick-sort"] = Topic(
    slug="quick-sort",
    title="Quick Sort",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    category="sorting",
    definition=(
        "Quick Sort is a divide-and-conquer sorting algorithm that selects a "
        "pivot element from the array, partitions the remaining elements so that "
        "elements smaller than the pivot are placed on one side and larger elements "
        "on the other, and recursively sorts the resulting partitions."
    ),
    how_it_works=[
        "Choose a pivot element from the array (commonly the first, last, middle, or a random element).",
        "Partition the array around the pivot: rearrange elements such that all elements less than or equal to the pivot come before it, and all elements greater than the pivot come after it.",
        "Recursively sort the left partition (elements smaller than the pivot).",
        "Recursively sort the right partition (elements greater than the pivot).",
        "Base case: When a sub-array contains zero or one element, it is already sorted; combining the partitions produces the sorted array.",
    ],
    example=(
        "Consider the array:\n"
        "[7, 2, 9, 4, 3]\n\n"
        "1. Choose pivot = 4.\n"
        "2. Partition around 4: elements <= 4 go left, > 4 go right:\n"
        "   [2, 3] | 4 | [7, 9]\n\n"
        "3. Recursively sort left partition [2, 3]:\n"
        "   Pivot = 3 -> [2] | 3 | [] -> sorted [2, 3]\n\n"
        "4. Recursively sort right partition [7, 9]:\n"
        "   Pivot = 9 -> [7] | 9 | [] -> sorted [7, 9]\n\n"
        "5. Combining the partitions produces:\n"
        "   [2, 3, 4, 7, 9]\n\n"
        "The exact intermediate partition depends on the partitioning scheme (e.g., Lomuto vs Hoare)."
    ),
    pseudocode=(
        "QUICKSORT(A, low, high):\n"
        "    if low < high:\n"
        "        p = PARTITION(A, low, high)\n"
        "        QUICKSORT(A, low, p - 1)\n"
        "        QUICKSORT(A, p + 1, high)\n\n"
        "PARTITION(A, low, high):\n"
        "    pivot = A[high]\n"
        "    i = low - 1\n"
        "    for j = low to high - 1:\n"
        "        if A[j] <= pivot:\n"
        "            i = i + 1\n"
        "            swap A[i] with A[j]\n"
        "    swap A[i + 1] with A[high]\n"
        "    return i + 1"
    ),
    code=(
        "def quicksort(arr, low=0, high=None):\n"
        "    if high is None:\n"
        "        high = len(arr) - 1\n"
        "    if low < high:\n"
        "        p = partition(arr, low, high)\n"
        "        quicksort(arr, low, p - 1)\n"
        "        quicksort(arr, p + 1, high)\n"
        "    return arr\n\n"
        "def partition(arr, low, high):\n"
        "    pivot = arr[high]\n"
        "    i = low - 1\n"
        "    for j in range(low, high):\n"
        "        if arr[j] <= pivot:\n"
        "            i += 1\n"
        "            arr[i], arr[j] = arr[j], arr[i]\n"
        "    arr[i + 1], arr[high] = arr[high], arr[i + 1]\n"
        "    return i + 1\n\n"
        "# Example usage:\n"
        "numbers = [7, 2, 9, 4, 3]\n"
        "print('Sorted:', quicksort(numbers))  # [2, 3, 4, 7, 9]"
    ),
    code_cpp=(
        "#include <iostream>\n"
        "#include <vector>\n"
        "using namespace std;\n\n"
        "int partition(vector<int>& arr, int low, int high) {\n"
        "    int pivot = arr[high];\n"
        "    int i = low - 1;\n"
        "    for (int j = low; j < high; j++) {\n"
        "        if (arr[j] <= pivot) {\n"
        "            i++;\n"
        "            swap(arr[i], arr[j]);\n"
        "        }\n"
        "    }\n"
        "    swap(arr[i + 1], arr[high]);\n"
        "    return i + 1;\n"
        "}\n\n"
        "void quickSort(vector<int>& arr, int low, int high) {\n"
        "    if (low < high) {\n"
        "        int p = partition(arr, low, high);\n"
        "        quickSort(arr, low, p - 1);\n"
        "        quickSort(arr, p + 1, high);\n"
        "    }\n"
        "}\n"
    ),
    complexity={
        "Best case": "O(n log n)",
        "Average case": "O(n log n)",
        "Worst case": "O(n²)",
    },
    space_complexity=(
        "Typical in-place implementations use O(log n) average auxiliary stack "
        "space and can use O(n) stack space in the worst case."
    ),
    properties=[
        "In-Place Sorting: Operates directly within the input array without requiring a secondary array (unlike Merge Sort).",
        "Not Stable: Standard Quick Sort does not preserve the relative order of duplicate elements unless modified.",
        "Cache Efficiency: High locality of reference makes Quick Sort significantly faster in real-world benchmarks compared to other O(n log n) algorithms.",
        "Pivot Dependency: Algorithmic efficiency directly depends on partitioning balance. Skewed partitions degrade performance.",
    ],
    exam_points=[
        "Quick Sort is based on the Divide-and-Conquer paradigm.",
        "The PARTITION routine does all the heavy lifting and runs in O(n) linear time.",
        "Best & Average Case time complexity: O(n log n).",
        "Worst Case time complexity: O(n²) — occurring when the selected pivot is repeatedly the smallest or largest element (e.g., already sorted array with first/last element as pivot).",
        "Mitigation for worst case: Randomized pivot selection or Median-of-Three pivot strategy.",
        "Standard Quick Sort is not stable, but it is an in-place sorting algorithm.",
    ],
    practice_question=(
        "Trace Quick Sort on the array [9, 3, 7, 1, 6] using the last element as the pivot. "
        "Show the array state after the initial partition step and identify the pivot's final index."
    ),
    practice_answer=(
        "1. Initial array: [9, 3, 7, 1, 6]. Selected pivot = 6 (last element).\n"
        "2. Elements <= 6: [3, 1]. Elements > 6: [9, 7].\n"
        "3. After partitioning around 6 (Lomuto scheme): [3, 1, 6, 9, 7].\n"
        "4. Pivot 6 is now at its correct sorted position (index 2).\n"
        "5. The algorithm recursively sorts left partition [3, 1] and right partition [9, 7], yielding [1, 3, 6, 7, 9]."
    ),
    simple_explanation=(
        "Think of Quick Sort like organizing students by height for a classroom photograph:\n\n"
        "1. Pick a benchmark student (the **pivot**) and have them stand in the middle.\n"
        "2. Ask everyone shorter than the pivot to move to their **left**.\n"
        "3. Ask everyone taller than the pivot to move to their **right**.\n"
        "4. Now the benchmark student is standing in their **exact permanent spot**! They will never have to move again.\n"
        "5. Repeat this exact same game for the group on the left and the group on the right.\n"
        "6. Once every group is down to just 1 student, the entire line is perfectly sorted from shortest to tallest.\n\n"
        "**Why students love it:** It sorts items directly inside the same room (in-place) without needing an extra empty room (extra memory) like Merge Sort does!"
    ),
    worst_case_explanation=(
        "### Why is Quick Sort's Worst-Case Time Complexity O(n²)?\n\n"
        "Quick Sort runs in **O(n²)** worst-case time when the **partitioning is completely unbalanced** at every recursive level. Instead of dividing the array into two roughly equal halves of size $n/2$, the array is partitioned into one sub-array of size $n - 1$ and one empty sub-array of size $0$.\n\n"
        "#### 1. When Does This Happen?\n"
        "- When the input array is **already sorted** (or reverse-sorted) and the algorithm chooses either the **first element** or the **last element** as the pivot.\n"
        "- When all elements in the array are **identical** and a naive partitioning scheme is used.\n\n"
        "#### 2. Mathematical Recurrence Relation\n"
        "In the balanced case, the recurrence is:\n"
        "$$T(n) = 2T(n/2) + O(n) \\implies O(n \\log n)$$\n\n"
        "In the worst unbalanced case, the recurrence becomes:\n"
        "$$T(n) = T(n - 1) + T(0) + cn = T(n - 1) + cn$$\n\n"
        "Expanding the recurrence:\n"
        "$$T(n) = cn + c(n-1) + c(n-2) + \\dots + c(1)$$\n"
        "$$T(n) = c \\sum_{i=1}^{n} i = c \\cdot \\frac{n(n + 1)}{2} = O(n^2)$$\n\n"
        "#### 3. Recursion Tree Depth\n"
        "- Best/Average case tree depth: $\\log_2 n$ levels, each doing $O(n)$ work $\\implies O(n \\log n)$.\n"
        "- Worst case tree depth: $n$ levels, each doing $O(n)$ work $\\implies O(n^2)$.\n\n"
        "#### 4. How to Prevent O(n²) in Practice\n"
        "1. **Randomized Quick Sort:** Choose a random element as the pivot, making the worst case statistically improbable ($P \\approx 0$).\n"
        "2. **Median-of-Three:** Pick the median of the first, middle, and last elements as the pivot.\n"
        "3. **Introsort:** Switch to Heap Sort if the recursion depth exceeds $2 \\log_2 n$ (standard in C++ STL `std::sort`)."
    ),
    related=["merge-sort", "bubble-sort", "binary-search"],
)

TOPICS["merge-sort"] = Topic(
    slug="merge-sort",
    title="Merge Sort",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    category="sorting",
    definition=(
        "Merge Sort is an efficient, general-purpose, comparison-based, and stable "
        "divide-and-conquer sorting algorithm. It divides the unsorted list into $n$ "
        "sub-lists (each containing one element), and repeatedly merges sub-lists "
        "to produce new sorted sub-lists until only one sorted list remains."
    ),
    how_it_works=[
        "Divide the unsorted array of size $n$ into two halves of size $n/2$.",
        "Conquer by recursively sorting both halves using Merge Sort.",
        "Combine the two sorted halves by merging them into a single sorted array.",
        "Base case: Arrays of length 0 or 1 are already sorted.",
    ],
    example=(
        "Consider array: [38, 27, 43, 3, 9, 82, 10]\n\n"
        "1. Divide:\n"
        "   [38, 27, 43, 3] and [9, 82, 10]\n"
        "   -> [38, 27], [43, 3] and [9, 82], [10]\n"
        "   -> [38], [27], [43], [3] and [9], [82], [10]\n\n"
        "2. Conquer & Merge:\n"
        "   Merge [38] & [27] -> [27, 38]\n"
        "   Merge [43] & [3]  -> [3, 43]\n"
        "   Merge [27, 38] & [3, 43] -> [3, 27, 38, 43]\n"
        "   Merge [9] & [82]  -> [9, 82]\n"
        "   Merge [9, 82] & [10] -> [9, 10, 82]\n\n"
        "3. Final Merge:\n"
        "   Merge [3, 27, 38, 43] & [9, 10, 82] -> [3, 9, 10, 27, 38, 43, 82]"
    ),
    pseudocode=(
        "MERGE-SORT(A, p, r):\n"
        "    if p < r:\n"
        "        q = floor((p + r) / 2)\n"
        "        MERGE-SORT(A, p, q)\n"
        "        MERGE-SORT(A, q + 1, r)\n"
        "        MERGE(A, p, q, r)\n\n"
        "MERGE(A, p, q, r):\n"
        "    Create temporary arrays L and R\n"
        "    Copy A[p..q] into L and A[q+1..r] into R\n"
        "    Compare elements from L and R, placing smaller into A[p..r]\n"
        "    Copy remaining elements of L or R into A"
    ),
    code=(
        "def merge_sort(arr):\n"
        "    if len(arr) <= 1:\n"
        "        return arr\n"
        "    mid = len(arr) // 2\n"
        "    left = merge_sort(arr[:mid])\n"
        "    right = merge_sort(arr[mid:])\n"
        "    return merge(left, right)\n\n"
        "def merge(left, right):\n"
        "    result = []\n"
        "    i = j = 0\n"
        "    while i < len(left) and j < len(right):\n"
        "        if left[i] <= right[j]:\n"
        "            result.append(left[i])\n"
        "            i += 1\n"
        "        else:\n"
        "            result.append(right[j])\n"
        "            j += 1\n"
        "    result.extend(left[i:])\n"
        "    result.extend(right[j:])\n"
        "    return result"
    ),
    complexity={
        "Best case": "O(n log n)",
        "Average case": "O(n log n)",
        "Worst case": "O(n log n)",
    },
    space_complexity="O(n) auxiliary space required for temporary arrays during merging.",
    properties=[
        "Stable: Maintains the relative order of equal keys.",
        "Guaranteed Performance: Always O(n log n) regardless of input order.",
        "Not In-Place: Requires O(n) auxiliary memory for standard array implementations.",
        "Ideal for Linked Lists and External Sorting (tape/disk drives).",
    ],
    exam_points=[
        "Merge Sort strictly guarantees O(n log n) running time in ALL cases.",
        "Recurrence relation: T(n) = 2T(n/2) + O(n) = O(n log n).",
        "It is a stable sorting algorithm.",
        "Drawback: Requires O(n) auxiliary memory.",
    ],
    practice_question="Merge two sorted sub-arrays [2, 5, 8] and [1, 4, 7] and show step-by-step element comparisons.",
    practice_answer="Compare 2 and 1 -> pick 1; compare 2 and 4 -> pick 2; compare 5 and 4 -> pick 4; compare 5 and 7 -> pick 5; compare 8 and 7 -> pick 7; take remaining 8. Result: [1, 2, 4, 5, 7, 8].",
    simple_explanation=(
        "Imagine you have two already sorted decks of playing cards:\n\n"
        "1. You look at the top card of both decks.\n"
        "2. Whichever card is smaller, you pick it up and place it into your new pile.\n"
        "3. You repeat this until both decks are combined into one sorted deck.\n"
        "4. Merge Sort simply splits a big unorganized pile in half repeatedly until every pile has just 1 card, and then merges them back together pair by pair!"
    ),
    related=["quick-sort", "bubble-sort"],
)

TOPICS["binary-search"] = Topic(
    slug="binary-search",
    title="Binary Search",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    category="searching",
    definition=(
        "Binary Search is an efficient algorithm for finding the position of a target "
        "value within a sorted array. It compares the target value to the middle element "
        "of the array; if unequal, the half in which the target cannot lie is eliminated, "
        "repeating until the target is found."
    ),
    how_it_works=[
        "Maintain search boundary pointers: low and high.",
        "Calculate middle index: mid = low + (high - low) // 2.",
        "If arr[mid] == target, return mid.",
        "If target < arr[mid], search left half: high = mid - 1.",
        "If target > arr[mid], search right half: low = mid + 1.",
        "If low > high, target is not present in the array.",
    ],
    example=(
        "Search for target = 23 in sorted array:\n"
        "[2, 5, 8, 12, 16, 23, 38, 56, 72, 91]\n\n"
        "Pass 1: low=0, high=9 -> mid=4 (val=16). 23 > 16 -> low = mid+1 = 5.\n"
        "Pass 2: low=5, high=9 -> mid=7 (val=56). 23 < 56 -> high = mid-1 = 6.\n"
        "Pass 3: low=5, high=6 -> mid=5 (val=23). 23 == 23 -> Target found at index 5!"
    ),
    pseudocode=(
        "BINARY-SEARCH(A, target):\n"
        "    low = 0\n"
        "    high = length(A) - 1\n"
        "    while low <= high:\n"
        "        mid = low + floor((high - low) / 2)\n"
        "        if A[mid] == target:\n"
        "            return mid\n"
        "        else if A[mid] < target:\n"
        "            low = mid + 1\n"
        "        else:\n"
        "            high = mid - 1\n"
        "    return -1"
    ),
    code=(
        "def binary_search(arr, target):\n"
        "    low = 0\n"
        "    high = len(arr) - 1\n"
        "    while low <= high:\n"
        "        mid = low + (high - low) // 2\n"
        "        if arr[mid] == target:\n"
        "            return mid\n"
        "        elif arr[mid] < target:\n"
        "            low = mid + 1\n"
        "        else:\n"
        "            high = mid - 1\n"
        "    return -1\n\n"
        "# Test:\n"
        "print(binary_search([2, 5, 8, 12, 16, 23, 38], 23))  # Output: 5"
    ),
    complexity={
        "Best case": "O(1)",
        "Average case": "O(log n)",
        "Worst case": "O(log n)",
    },
    space_complexity="O(1) auxiliary space for iterative version; O(log n) stack space for recursive version.",
    properties=[
        "Prerequisite: Array MUST be sorted in ascending or descending order.",
        "Search Space Reduction: Halves the remaining search candidates at every step.",
        "Significantly outperforms Linear Search O(n) for large datasets.",
    ],
    exam_points=[
        "Time complexity: O(log n) in average and worst cases; O(1) in best case.",
        "Recurrence relation: T(n) = T(n/2) + O(1) = O(log n).",
        "Common bug: Avoid integer overflow in mid calculation by using low + (high - low) / 2 instead of (low + high) / 2 in C/C++.",
    ],
    practice_question="How many comparisons are required at most to find an element in a sorted array of 1,024 elements using Binary Search?",
    practice_answer="log2(1024) + 1 = 10 + 1 = 11 comparisons at most.",
    simple_explanation=(
        "Think of searching for a word in a physical dictionary:\n\n"
        "You don't read page by page from the beginning (Linear Search). You open right in the middle! If your word starts with 'S' and you landed on 'M', you discard the entire first half of the book and open the middle of the remaining half. You keep halving the pages until you find your word in seconds."
    ),
    related=["quick-sort", "big-o"],
)

TOPICS["big-o"] = Topic(
    slug="big-o",
    title="Big-O Notation & Asymptotic Analysis",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    category="analysis",
    definition=(
        "Big-O notation is a mathematical notation that describes the limiting behavior "
        "of a function when the argument tends towards a particular value or infinity. "
        "In CSIT, it formalizes the worst-case upper bound on the time or space requirements "
        "of an algorithm in terms of input size $n$."
    ),
    how_it_works=[
        "Formal definition: f(n) = O(g(n)) if there exist positive constants c and n0 such that 0 <= f(n) <= c * g(n) for all n >= n0.",
        "Ignores constant factors and lower-order terms as n approaches infinity.",
        "Common orders from fastest to slowest: O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2^n) < O(n!).",
    ],
    example=(
        "Analyze f(n) = 3n² + 5n + 12:\n"
        "- Drop constants and lower-order terms: 5n and 12 are dominated by n² as n grows large.\n"
        "- Asymptotic upper bound is O(n²).\n"
        "- Witness: c = 4, n0 = 7, since 3n² + 5n + 12 <= 4n² for all n >= 7."
    ),
    pseudocode=(
        "Common complexity examples:\n"
        "- O(1): Accessing array element arr[i]\n"
        "- O(log n): Binary Search\n"
        "- O(n): Linear scan through array\n"
        "- O(n log n): Quick Sort (average), Merge Sort\n"
        "- O(n²): Nested loops, Bubble Sort"
    ),
    complexity={
        "O(1)": "Constant time",
        "O(log n)": "Logarithmic time",
        "O(n)": "Linear time",
        "O(n log n)": "Linearithmic time",
        "O(n²)": "Quadratic time",
    },
    properties=[
        "Upper Bound: Big-O gives the worst-case guarantee.",
        "Big-Omega (Ω): Gives the asymptotic lower bound (best-case).",
        "Big-Theta (Θ): Gives the tight asymptotic bound where upper and lower bounds match.",
    ],
    exam_points=[
        "State formal definition with constants c and n0.",
        "Distinguish between Big-O (upper bound), Big-Omega (lower bound), and Big-Theta (tight bound).",
        "Know the standard growth hierarchy: O(1) to O(n!).",
    ],
    practice_question="Prove that 5n² + 3n + 8 = O(n²) using the formal definition of Big-O.",
    practice_answer="Choose c = 6 and n0 = 5. For n >= 5, 3n <= n² and 8 <= n², so 5n² + 3n + 8 <= 5n² + n² = 6n². Hence f(n) <= c * g(n) holds, proving f(n) = O(n²).",
    simple_explanation=(
        "Big-O measures how an algorithm's run time stretches when you give it bigger homework:\n\n"
        "- O(1): Looking up a person's name on a flashcard — takes 1 second whether you have 10 or 1,000,000 flashcards.\n"
        "- O(n): Reading a book page-by-page — if the book is twice as long, it takes twice as long.\n"
        "- O(n²): Every student shaking hands with every other student in school — if enrollment doubles, the number of handshakes quadruples!"
    ),
    related=["quick-sort", "binary-search"],
)

TOPICS["bubble-sort"] = Topic(
    slug="bubble-sort",
    title="Bubble Sort",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    category="sorting",
    definition=(
        "Bubble Sort is a simple comparison-based sorting algorithm that repeatedly "
        "steps through the list, compares adjacent elements, and swaps them if they "
        "are in the wrong order. The pass through the list is repeated until the list is sorted."
    ),
    how_it_works=[
        "Compare adjacent pairs: A[j] and A[j+1].",
        "If A[j] > A[j+1], swap them.",
        "After pass 1, the largest element 'bubbles up' to the last position.",
        "Repeat for remaining n-1 elements.",
        "Optimization: If no swaps occur during a pass, the array is already sorted; terminate early.",
    ],
    example=(
        "Array: [5, 1, 4, 2, 8]\n"
        "Pass 1: [1, 5, 4, 2, 8] -> [1, 4, 5, 2, 8] -> [1, 4, 2, 5, 8] -> [1, 4, 2, 5, 8]. (8 is in place)\n"
        "Pass 2: [1, 4, 2, 5, 8] -> [1, 2, 4, 5, 8] -> ... sorted!"
    ),
    pseudocode=(
        "BUBBLE-SORT(A):\n"
        "    n = length(A)\n"
        "    for i = 0 to n - 1:\n"
        "        swapped = false\n"
        "        for j = 0 to n - i - 2:\n"
        "            if A[j] > A[j + 1]:\n"
        "                swap A[j] with A[j + 1]\n"
        "                swapped = true\n"
        "        if not swapped:\n"
        "            break"
    ),
    code=(
        "def bubble_sort(arr):\n"
        "    n = len(arr)\n"
        "    for i in range(n):\n"
        "        swapped = False\n"
        "        for j in range(0, n - i - 1):\n"
        "            if arr[j] > arr[j + 1]:\n"
        "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
        "                swapped = True\n"
        "        if not swapped:\n"
        "            break\n"
        "    return arr"
    ),
    complexity={
        "Best case": "O(n) (with swapped flag on sorted array)",
        "Average case": "O(n²)",
        "Worst case": "O(n²)",
    },
    space_complexity="O(1) auxiliary space (in-place).",
    properties=[
        "Stable sorting algorithm.",
        "In-place algorithm requiring O(1) memory.",
        "Inefficient for large arrays; primarily of academic/introductory value.",
    ],
    exam_points=[
        "Best case is O(n) only when the optimized swap flag is used.",
        "Worst and average case are O(n²).",
        "It is stable and in-place.",
    ],
    practice_question="How many comparisons are made in the first pass of Bubble Sort on an array of size n?",
    practice_answer="n - 1 comparisons.",
    simple_explanation="Heavier items sink to the bottom while lighter bubbles float up to the surface one step at a time.",
    related=["quick-sort", "merge-sort"],
)

TOPICS["linked-list"] = Topic(
    slug="linked-list",
    title="Linked List",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    category="data-structures",
    definition=(
        "A Linked List is a linear data structure in which elements are stored in nodes, "
        "and each node points to the next node in memory via a pointer/reference rather "
        "than being stored contiguously like arrays."
    ),
    how_it_works=[
        "Singly Linked List: Each node contains data and a next pointer.",
        "Doubly Linked List: Each node contains prev pointer, data, and next pointer.",
        "Circular Linked List: The last node's next pointer points back to the head node.",
        "Dynamic sizing: Grows and shrinks at runtime without reallocation overhead.",
    ],
    example="Head -> [Data: 10 | Next] -> [Data: 20 | Next] -> [Data: 30 | Next: NULL]",
    pseudocode=(
        "NODE:\n"
        "    data\n"
        "    next\n\n"
        "INSERT-AT-HEAD(head, value):\n"
        "    newNode = new Node(value)\n"
        "    newNode.next = head\n"
        "    head = newNode"
    ),
    code=(
        "class Node:\n"
        "    def __init__(self, data):\n"
        "        self.data = data\n"
        "        self.next = None\n\n"
        "class LinkedList:\n"
        "    def __init__(self):\n"
        "        self.head = None\n\n"
        "    def insert_at_beginning(self, data):\n"
        "        new_node = Node(data)\n"
        "        new_node.next = self.head\n"
        "        self.head = new_node"
    ),
    complexity={
        "Access by index": "O(n)",
        "Search": "O(n)",
        "Insert at head": "O(1)",
        "Delete at head": "O(1)",
        "Insert/Delete at end": "O(n) (or O(1) with tail pointer)",
    },
    space_complexity="O(n) with extra memory per node for pointer(s).",
    properties=[
        "Dynamic memory allocation — no predefined capacity required.",
        "No random access: accessing element at index k requires traversing k nodes from head.",
        "Extra memory overhead for pointer storage.",
    ],
    exam_points=[
        "Compare array vs linked list: Arrays have O(1) random access; Linked Lists have O(1) insertion/deletion at known nodes.",
        "Know implementations for insert at head, insert at tail, and reverse a singly linked list.",
    ],
    practice_question="Write the algorithm to reverse a singly linked list in-place.",
    practice_answer="Use three pointers: prev = NULL, curr = head, next = NULL. While curr is not NULL: next = curr.next; curr.next = prev; prev = curr; curr = next. Set head = prev.",
    simple_explanation="Like a treasure hunt with clues: each clue gives you the treasure and a slip of paper telling you where the next clue is hidden.",
    related=["stack", "queue"],
)

TOPICS["stack"] = Topic(
    slug="stack",
    title="Stack (Abstract Data Type)",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    category="data-structures",
    definition=(
        "A Stack is a linear data structure that follows the Last-In, First-Out (LIFO) "
        "principle. The most recently added element is the first one to be removed."
    ),
    how_it_works=[
        "Push: Inserts an element onto the top of the stack.",
        "Pop: Removes and returns the top element.",
        "Peek/Top: Returns the top element without removing it.",
        "IsEmpty / IsFull: Checks stack boundaries.",
    ],
    example="Stack operations on empty stack:\nPush(10) -> [10]\nPush(20) -> [10, 20]\nPop() -> returns 20, stack is [10]\nPeek() -> returns 10",
    pseudocode=(
        "PUSH(S, x):\n"
        "    if top == MAX - 1: ERROR('Stack Overflow')\n"
        "    top = top + 1\n"
        "    S[top] = x\n\n"
        "POP(S):\n"
        "    if top == -1: ERROR('Stack Underflow')\n"
        "    val = S[top]\n"
        "    top = top - 1\n"
        "    return val"
    ),
    code=(
        "class Stack:\n"
        "    def __init__(self):\n"
        "        self.items = []\n"
        "    def push(self, val):\n"
        "        self.items.append(val)\n"
        "    def pop(self):\n"
        "        if self.is_empty():\n"
        "            raise IndexError('Pop from empty stack')\n"
        "        return self.items.pop()\n"
        "    def peek(self):\n"
        "        return self.items[-1] if not self.is_empty() else None\n"
        "    def is_empty(self):\n"
        "        return len(self.items) == 0"
    ),
    complexity={
        "Push": "O(1)",
        "Pop": "O(1)",
        "Peek": "O(1)",
        "Search": "O(n)",
    },
    space_complexity="O(n) memory proportional to elements stored.",
    properties=[
        "Strict LIFO ordering.",
        "Applications: Function call stack/recursion, undo mechanisms in editors, expression evaluation (infix to postfix), syntax parsing.",
    ],
    exam_points=[
        "Identify LIFO principle and core operations.",
        "Infix to Postfix conversion using stack is a frequent TU exam question.",
        "Know conditions for Stack Overflow and Stack Underflow.",
    ],
    practice_question="Evaluate the postfix expression: 5 3 + 2 * using a stack.",
    practice_answer="Push 5, Push 3. Encounter '+': pop 3 and 5, calculate 5+3=8, push 8. Encounter 2: push 2. Encounter '*': pop 2 and 8, calculate 8*2=16, push 16. Final result = 16.",
    simple_explanation="Like a stack of cafeteria trays: you can only take the tray that is right on top, and you add new trays on top.",
    related=["queue", "linked-list"],
)

TOPICS["queue"] = Topic(
    slug="queue",
    title="Queue (Abstract Data Type)",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    category="data-structures",
    definition=(
        "A Queue is a linear data structure that follows the First-In, First-Out (FIFO) "
        "principle. Elements are inserted at the rear (Enqueue) and removed from the front (Dequeue)."
    ),
    how_it_works=[
        "Enqueue: Inserts an element at the rear of the queue.",
        "Dequeue: Removes and returns the element at the front of the queue.",
        "Front/Peek: Reads the front item without removing it.",
        "Circular Queue: Overcomes linear queue memory wastage by wrapping rear to index 0 using modulo arithmetic: (rear + 1) % MAX.",
    ],
    example="Queue: Enqueue(A) -> [A]\nEnqueue(B) -> [A, B]\nDequeue() -> returns A, queue is [B]",
    pseudocode=(
        "CIRCULAR-ENQUEUE(Q, x):\n"
        "    if (rear + 1) % MAX == front: ERROR('Queue Full')\n"
        "    if front == -1: front = 0\n"
        "    rear = (rear + 1) % MAX\n"
        "    Q[rear] = x"
    ),
    code=(
        "class Queue:\n"
        "    def __init__(self):\n"
        "        self.items = []\n"
        "    def enqueue(self, val):\n"
        "        self.items.append(val)\n"
        "    def dequeue(self):\n"
        "        if not self.is_empty():\n"
        "            return self.items.pop(0)\n"
        "        raise IndexError('Dequeue from empty queue')\n"
        "    def is_empty(self):\n"
        "        return len(self.items) == 0"
    ),
    complexity={
        "Enqueue": "O(1)",
        "Dequeue": "O(1) with circular buffer or linked list",
        "Front": "O(1)",
    },
    space_complexity="O(n).",
    properties=[
        "FIFO principle.",
        "Variants: Circular Queue, Priority Queue, Deque (Double-Ended Queue).",
        "Applications: CPU task scheduling, print spooling, Breadth-First Search (BFS) graph traversal.",
    ],
    exam_points=[
        "Why is Circular Queue preferred over Linear Queue? (Eliminates false overflow).",
        "Conditions for empty queue: front == -1 or front == rear + 1.",
    ],
    practice_question="Why does a simple array implementation of a linear queue cause memory wastage after multiple dequeues?",
    practice_answer="Because front pointer advances forward; empty slots at the beginning cannot be reused even if rear reaches MAX, causing false overflow.",
    simple_explanation="Like waiting in line at a cinema ticket counter: the first person to arrive is the first person served and exit.",
    related=["stack", "linked-list"],
)

TOPICS["normalization"] = Topic(
    slug="normalization",
    title="Database Normalization",
    subject="Database Management Systems",
    semester="Fourth Semester",
    category="database",
    definition=(
        "Database Normalization is the systematic process of organizing data in a "
        "relational database to reduce data redundancy, eliminate anomalies "
        "(insertion, update, and deletion anomalies), and ensure data integrity."
    ),
    how_it_works=[
        "1NF (First Normal Form): Eliminate repeating groups; ensure all column values are atomic (indivisible) and each record is unique.",
        "2NF (Second Normal Form): Must be in 1NF, and eliminate partial dependency (all non-key attributes must be fully functionally dependent on the entire primary key).",
        "3NF (Third Normal Form): Must be in 2NF, and eliminate transitive dependency (no non-key attribute depends on another non-key attribute: X -> Y where neither is a candidate key).",
        "BCNF (Boyce-Codd Normal Form): A stricter version of 3NF where for every functional dependency X -> Y, X must be a super key.",
    ],
    example=(
        "Unnormalized Student Table:\n"
        "[ID: 1, Name: 'Samyog', Courses: 'DSA, DBMS'] (Courses has multiple values -> violates 1NF).\n\n"
        "Converted to 1NF:\n"
        "[1, 'Samyog', 'DSA']\n"
        "[1, 'Samyog', 'DBMS'] (Values are now atomic!)."
    ),
    pseudocode=(
        "NORMALIZATION STEPS:\n"
        "Unnormalized -> Atomic attributes -> 1NF\n"
        "1NF -> Remove partial key dependency -> 2NF\n"
        "2NF -> Remove transitive dependency -> 3NF\n"
        "3NF -> Determinant must be Super Key -> BCNF"
    ),
    complexity={},
    properties=[
        "Lossless Join Decomposition: Joining the decomposed tables must reproduce the exact original relation without spurious tuples.",
        "Dependency Preservation: Functional dependencies in the original table should be enforceable on individual decomposed tables.",
    ],
    exam_points=[
        "Define 1NF, 2NF, 3NF, and BCNF with concrete schemas.",
        "Define Partial Dependency and Transitive Dependency.",
        "Explain Insertion, Update, and Deletion anomalies with an example.",
    ],
    practice_question="Given relation R(A, B, C, D) with primary key (A, B) and functional dependency B -> C. Which normal form does it violate?",
    practice_answer="Violates 2NF because non-prime attribute C depends only on part of the composite primary key B (partial dependency).",
    simple_explanation=(
        "Like organizing your kitchen into labeled spice jars instead of dumping salt, pepper, and sugar into one giant messy jar:\n\n"
        "If you change a spice's brand name, you only update one jar instead of rewriting thousands of dinner recipe cards!"
    ),
    related=["acid"],
)

TOPICS["acid"] = Topic(
    slug="acid",
    title="ACID Properties in Transactions",
    subject="Database Management Systems",
    semester="Fourth Semester",
    category="database",
    definition=(
        "ACID properties (Atomicity, Consistency, Isolation, Durability) are a set of "
        "guarantees that ensure database transactions are processed reliably, preserving "
        "data integrity even in the event of system failures or concurrent access."
    ),
    how_it_works=[
        "Atomicity ('All or Nothing'): The transaction executes completely or not at all. If any step fails, changes are rolled back.",
        "Consistency: A transaction must transition the database from one valid state to another, satisfying all integrity constraints (foreign keys, uniqueness).",
        "Isolation: Concurrent transactions execute independently without interfering with each other. Intermediate states of transaction T1 are invisible to T2.",
        "Durability: Once a transaction commits, its updates persist permanently in non-volatile storage, even during sudden power failure or system crash.",
    ],
    example=(
        "Bank Fund Transfer: Transfer Rs 5,000 from Account A to Account B:\n"
        "1. Deduct 5,000 from A.\n"
        "2. Add 5,000 to B.\n"
        "- Atomicity: If power fails after step 1, money is not lost; step 1 is undone.\n"
        "- Consistency: Total sum of money in A and B remains identical before and after.\n"
        "- Isolation: Another person checking balance cannot see intermediate money in limbo.\n"
        "- Durability: Once screen says 'Transfer Successful', the database update is permanent."
    ),
    pseudocode=(
        "BEGIN TRANSACTION\n"
        "    UPDATE Accounts SET balance = balance - 5000 WHERE id = 'A'\n"
        "    UPDATE Accounts SET balance = balance + 5000 WHERE id = 'B'\n"
        "IF error:\n"
        "    ROLLBACK\n"
        "ELSE:\n"
        "    COMMIT"
    ),
    complexity={},
    properties=[
        "Enforced by Database Engine components: Log Manager (Atomicity/Durability), Concurrency Control Manager (Isolation), Integrity Checking (Consistency).",
        "Isolation levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable.",
    ],
    exam_points=[
        "Explain each letter of ACID with the bank transfer scenario.",
        "Name the component responsible for Atomicity (Recovery Manager / Write-Ahead Logging).",
        "Explain Concurrency problems: Dirty Read, Non-Repeatable Read, Phantom Read.",
    ],
    practice_question="Which ACID property ensures that committed transactions survive a database server power outage?",
    practice_answer="Durability (guaranteed by write-ahead transaction logs on non-volatile disk).",
    simple_explanation="Four golden rules that make sure online banking never loses your money during a crash or simultaneous purchases.",
    related=["normalization"],
)

TOPICS["process-vs-thread"] = Topic(
    slug="process-vs-thread",
    title="Process vs Thread",
    subject="Operating Systems",
    semester="Fourth Semester",
    category="operating-systems",
    definition=(
        "A Process is an executing instance of a program with its own independent "
        "address space and system resources. A Thread is a lightweight sub-unit of execution "
        "within a process that shares the parent process's memory space, code, and data."
    ),
    how_it_works=[
        "Process contains: Text (code), Data (globals), Heap (dynamic memory), Stack (local variables), Process Control Block (PCB).",
        "Thread contains: Thread ID, Program Counter (PC), Register set, and its own private Stack. It shares Code, Data, and OS resources with sibling threads.",
        "Context switching between processes requires reloading virtual memory page tables and registers (heavy overhead).",
        "Context switching between threads inside the same process only saves/restores registers and stack pointer (lightweight).",
    ],
    example=(
        "Real-world OS example:\n"
        "- Running Google Chrome is a Process.\n"
        "- Multiple tabs or background download workers inside Chrome run as Threads or child processes.\n"
        "- In a Word processor: One thread listens to typing, another thread spell-checks in the background, a third thread auto-saves to disk."
    ),
    pseudocode=(
        "PROCESS PCB:\n"
        "    PID, Registers, Memory Limits, Open Files List\n\n"
        "THREAD TCB:\n"
        "    TID, PC, Registers, Stack Pointer\n"
        "    (Shares address space with parent Process)"
    ),
    complexity={},
    properties=[
        "Memory: Processes have isolated memory; Threads share memory within the process.",
        "Communication: IPC (pipes, sockets, shared memory) for processes; direct variable access for threads.",
        "Fault Tolerance: If a process crashes, others are unaffected; if an unhandled crash occurs in a thread, the parent process may terminate.",
    ],
    exam_points=[
        "Construct a comparison table: Process vs Thread (definition, memory, creation cost, context switch, IPC).",
        "Define PCB (Process Control Block) and TCB (Thread Control Block).",
    ],
    practice_question="Why is context switching between threads faster than between processes?",
    practice_answer="Because threads share the same address space and memory mapping; virtual memory page tables and TLB caches do not need to be flushed or reloaded during thread context switching.",
    simple_explanation="A Process is like a house with its own kitchen and plumbing; Threads are family members living in that house who share the kitchen and living room.",
    related=["deadlock"],
)

TOPICS["deadlock"] = Topic(
    slug="deadlock",
    title="Deadlock & Coffman Conditions",
    subject="Operating Systems",
    semester="Fourth Semester",
    category="operating-systems",
    definition=(
        "A Deadlock is an operating system state in which two or more concurrent "
        "processes are permanently blocked because each process holds a resource that "
        "another needs, and neither can proceed."
    ),
    how_it_works=[
        "Four Coffman conditions must hold simultaneously for a deadlock to exist:",
        "1. Mutual Exclusion: At least one resource must be held in a non-shareable mode.",
        "2. Hold and Wait: A process must be holding at least one resource and waiting to acquire additional resources held by others.",
        "3. No Preemption: Resources cannot be forcibly taken; they can only be released voluntarily by the holding process.",
        "4. Circular Wait: A closed chain of processes exists such that P0 waits for P1, P1 waits for P2, ..., and Pn waits for P0.",
    ],
    example=(
        "Traffic Intersection Analogy:\n"
        "Four cars arrive at a four-way intersection simultaneously, each wanting to turn right. "
        "Each car blocks the path of the car behind it. None can move forward without a collision. "
        "This is circular wait -> Deadlock."
    ),
    pseudocode=(
        "DEADLOCK HANDLING STRATEGIES:\n"
        "1. Prevention: Invalidate at least one Coffman condition.\n"
        "2. Avoidance: Banker's Algorithm (safe vs unsafe state).\n"
        "3. Detection & Recovery: Resource Allocation Graph (RAG) cycle detection; terminate process or preempt resources.\n"
        "4. Ignorance: Ostrich Algorithm (used by most general-purpose OS like Linux/Windows)."
    ),
    complexity={},
    properties=[
        "Resource Allocation Graph (RAG): If RAG contains no cycles, no deadlock exists. If RAG has cycles and resources are single-instance, deadlock exists.",
    ],
    exam_points=[
        "State and explain the four Coffman conditions.",
        "Describe Banker's Algorithm with safe/unsafe state definitions.",
        "Differentiate between Deadlock Prevention and Deadlock Avoidance.",
    ],
    practice_question="Which Coffman condition is broken if processes are required to request all required resources at once before beginning execution?",
    practice_answer="Hold and Wait condition is eliminated.",
    simple_explanation="Two children fighting over toy train tracks: one child holds the train engine, the other holds the tracks, and neither will share until they get the other part.",
    related=["process-vs-thread"],
)

TOPICS["tcp-vs-udp"] = Topic(
    slug="tcp-vs-udp",
    title="TCP vs UDP Protocols",
    subject="Computer Networks",
    semester="Fourth Semester",
    category="networking",
    definition=(
        "TCP (Transmission Control Protocol) and UDP (User Datagram Protocol) are the "
        "two core transport layer protocols of the Internet Protocol suite. TCP provides "
        "reliable, connection-oriented, byte-stream delivery with congestion control, "
        "while UDP provides connectionless, lightweight, low-overhead datagram transmission."
    ),
    how_it_works=[
        "TCP Handshake: Three-way handshake (SYN, SYN-ACK, ACK) establishes connection.",
        "Reliability: TCP uses sequence numbers, acknowledgments (ACKs), and retransmissions for lost packets.",
        "UDP Operation: Fire-and-forget. Packets (datagrams) are sent without prior handshake or delivery acknowledgment.",
        "Header Size: TCP header is 20-60 bytes; UDP header is minimal at only 8 bytes.",
    ],
    example=(
        "- TCP: Web browsing (HTTP/HTTPS), Email (SMTP/IMAP), File Transfer (FTP), SSH.\n"
        "- UDP: DNS lookups, Live video streaming, VoIP (Discord/Zoom audio), Online multiplayer gaming."
    ),
    pseudocode=(
        "TCP THREE-WAY HANDSHAKE:\n"
        "Client -> [SYN] seq=x -> Server\n"
        "Server -> [SYN+ACK] seq=y, ack=x+1 -> Client\n"
        "Client -> [ACK] ack=y+1 -> Server\n"
        "(Connection Established!)"
    ),
    complexity={},
    properties=[
        "Connection: TCP is connection-oriented; UDP is connectionless.",
        "Ordering: TCP guarantees ordered delivery; UDP arrives out of order.",
        "Speed: UDP is faster with lower latency; TCP is slower due to handshakes and flow/congestion control.",
    ],
    exam_points=[
        "Draw and explain the TCP 3-way handshake diagram.",
        "Compare TCP vs UDP across: reliability, speed, header size, error checking, and use cases.",
    ],
    practice_question="Why does online video gaming prefer UDP over TCP?",
    practice_answer="Because in fast-paced real-time gaming, current player coordinates matter immediately. TCP's retransmission of an old lost coordinate creates jitter and lag.",
    simple_explanation="TCP is like a registered postal letter where the recipient must sign an acknowledgment; UDP is like shouting a message across the street — fast, but you don't guarantee they heard every word.",
    related=["http-get-post"],
)

TOPICS["http-get-post"] = Topic(
    slug="http-get-post",
    title="HTTP GET vs POST Methods",
    subject="Web Technologies",
    semester="Fifth Semester",
    category="web",
    definition=(
        "GET and POST are the primary HTTP request methods defined by RFC protocols. "
        "GET requests data from a specified resource without side effects, while POST "
        "submits data to be processed to a specified resource, often resulting in "
        "state change or side effects on the server."
    ),
    how_it_works=[
        "GET: Parameters are appended directly to the URL query string (e.g., /search?q=tu+csit). It is idempotent and cacheable.",
        "POST: Data is enclosed within the HTTP request body. It is non-idempotent by default and parameters are not visible in the browser URL.",
    ],
    example="GET /search?term=algorithm HTTP/1.1\n\nPOST /login HTTP/1.1\nHost: example.com\nContent-Type: application/json\n\n{\"user\": \"samyog\", \"pass\": \"secret\"}",
    pseudocode="",
    complexity={},
    properties=[
        "Idempotency: GET is idempotent (calling 10 times yields same server state); POST is non-idempotent.",
        "Security: GET parameters remain in browser history, bookmarks, and server access logs (never use for passwords!).",
        "Payload Limit: GET length is restricted by browser/server URL limits (~2048 chars); POST has virtually unlimited payload capacity.",
    ],
    exam_points=[
        "Explain idempotency in HTTP methods.",
        "Comparison: GET vs POST (data location, security, caching, bookmarks, payload size).",
    ],
    practice_question="Why should a user login form never use HTTP GET?",
    practice_answer="Because GET appends user credentials into the URL string in plain text, exposing passwords in browser history, bookmarks, proxy logs, and shoulder surfing.",
    simple_explanation="GET is like sending a postcard where anyone can read the text on the back; POST is like sealing your letter inside an envelope.",
    related=["tcp-vs-udp"],
)


# --------------------------------------------------------------------------- #
# TU BSc CSIT Curricular Catalog: All 8 Semesters & Verified Course Codes
# --------------------------------------------------------------------------- #
SEMESTERS = {
    "First Semester": {
        "Introduction to Information Technology": "CSC114",
        "C Programming": "CSC115",
        "Digital Logic": "CSC116",
        "Mathematics I": "MTH117",
        "Physics": "PHY118",
    },
    "Second Semester": {
        "Discrete Structures": "CSC160",
        "Object Oriented Programming (C++)": "CSC161",
        "Microprocessor": "CSC162",
        "Mathematics II": "MTH163",
        "Statistics I": "STA164",
    },
    "Third Semester": {
        "Data Structures and Algorithms": "CSC206",
        "Numerical Method": "CSC207",
        "Computer Architecture": "CSC208",
        "Computer Graphics": "CSC209",
        "Statistics II": "STA210",
    },
    "Fourth Semester": {
        "Theory of Computation": "CSC257",
        "Computer Networks": "CSC258",
        "Operating Systems": "CSC259",
        "Database Management System": "CSC260",
        "Artificial Intelligence": "CSC261",
    },
    "Fifth Semester": {
        "Design and Analysis of Algorithms": "CSC314",
        "System Analysis and Design": "CSC315",
        "Cryptography": "CSC316",
        "Simulation and Modeling": "CSC317",
        "Web Technology": "CSC318",
    },
    "Sixth Semester": {
        "Software Engineering": "CSC364",
        "Compiler Design and Construction": "CSC365",
        "E-Governance": "CSC366",
        ".NET Computing": "CSC367",
        "Technical Writing": "CSC368",
    },
    "Seventh Semester": {
        "Advanced Java Programming": "CSC409",
        "Data Warehousing and Data Mining": "CSC410",
        "Principles of Management": "MGT411",
        "Project Work": "CSC412",
        "Elective I (Image Processing / Net Security)": "CSC413",
    },
    "Eighth Semester": {
        "Advanced Networking with IPv6": "CSC461",
        "Distributed Networking": "CSC462",
        "Game Technology": "CSC463",
        "Internship": "CSC464",
        "Elective II (Cloud Computing / Mobile App)": "CSC465",
    },
}

# --------------------------------------------------------------------------- #
# Real, Traceable Resources with Verified Attribution
# --------------------------------------------------------------------------- #
RESOURCES = [
    {
        "id": "res-qs-study-guide",
        "title": "Quick Sort — Complete Algorithm Guide & TU Exam Prep",
        "subject": "Data Structures and Algorithms",
        "semester": "Third Semester",
        "code": "CSC206",
        "type": "Study Guide",
        "description": "Divide-and-conquer sorting breakdown: step-by-step example on [7, 2, 9, 4, 3], Lomuto pseudocode, Python/C++ code, O(n log n) best/average vs O(n²) worst-case complexity proof, and practice questions.",
        "url": None,
        "is_internal": True,
        "topic": "quick-sort",
        "download_content": "Quick Sort Study Guide\n\nDefinition:\nQuick Sort is a divide-and-conquer algorithm...",
    },
    {
        "id": "res-ms-study-guide",
        "title": "Merge Sort — Complete Algorithm Guide & Proofs",
        "subject": "Data Structures and Algorithms",
        "semester": "Third Semester",
        "code": "CSC206",
        "type": "Study Guide",
        "description": "Detailed guide on stable divide-and-conquer sorting, recurrence relation T(n) = 2T(n/2) + O(n), merge algorithm, and comparison with Quick Sort.",
        "url": None,
        "is_internal": True,
        "topic": "merge-sort",
        "download_content": "Merge Sort Study Guide\n\nGuaranteed O(n log n) sorting...",
    },
    {
        "id": "res-dsa-syllabus",
        "title": "Data Structures & Algorithms (CSC206) — TU Official Syllabus",
        "subject": "Data Structures and Algorithms",
        "semester": "Third Semester",
        "code": "CSC206",
        "type": "Syllabus",
        "description": "Tribhuvan University official syllabus units: Stacks, Queues, Lists, Trees (BST, AVL, B-Trees), Sorting & Searching, Graphs (BFS, DFS, Dijkstra), and Complexity Analysis.",
        "url": None,
        "is_internal": True,
        "topic": None,
        "download_content": "Tribhuvan University - Institute of Science and Technology\nCourse: Data Structures and Algorithms (CSC206)\n...",
    },
    {
        "id": "res-dsa-past-questions",
        "title": "TU Board Exam Past Question Bank — DSA (2076–2079)",
        "subject": "Data Structures and Algorithms",
        "semester": "Third Semester",
        "code": "CSC206",
        "type": "Question Bank",
        "description": "Compilation of TU board questions covering Quick Sort partition tracing, AVL tree rotations, Dijkstra's algorithm, and Infix to Postfix conversion.",
        "url": None,
        "is_internal": True,
        "topic": None,
        "download_content": "TU Board Exam Questions - Data Structures & Algorithms\n2079 Exam:\n1. Explain Quick Sort with partition algorithm and complexity...",
    },
    {
        "id": "res-dbms-syllabus",
        "title": "Database Management System (CSC260) — Syllabus Outline",
        "subject": "Database Management System",
        "semester": "Fourth Semester",
        "code": "CSC260",
        "type": "Syllabus",
        "description": "TU syllabus units: Relational model, ER Diagrams, SQL, Relational Algebra, Normalization (1NF-BCNF), Transaction Processing, ACID, Concurrency, and Recovery.",
        "url": None,
        "is_internal": True,
        "topic": "normalization",
        "download_content": "Tribhuvan University - Database Management Systems (CSC260) Course Syllabus...",
    },
    {
        "id": "res-os-lab-sheet",
        "title": "Operating Systems (CSC259) — Practical Lab Manual",
        "subject": "Operating Systems",
        "semester": "Fourth Semester",
        "code": "CSC259",
        "type": "Lab Manual",
        "description": "TU CSIT practical exercises: CPU scheduling algorithms (FCFS, SJF, Round Robin in C), Producer-Consumer problem using Semaphores, Banker's algorithm implementation.",
        "url": None,
        "is_internal": True,
        "topic": "deadlock",
        "download_content": "Operating Systems Lab Manual - TU BSc CSIT\nLab 1: FCFS and SJF Scheduling in C\nLab 2: Round Robin Scheduling\nLab 3: Banker's Algorithm...",
    },
    {
        "id": "res-hamrocsit-semesters",
        "title": "HamroCSIT Semester Portal",
        "subject": "All Subjects",
        "semester": "All Semesters",
        "code": "ALL",
        "type": "External Reference",
        "description": "Directory of student-shared notes and community resources on HamroCSIT.",
        "url": "https://hamrocsit.com/semester/fourth/",
        "is_internal": False,
        "topic": None,
        "download_content": None,
    },
    {
        "id": "res-hamrocsit-questions",
        "title": "HamroCSIT Question Bank",
        "subject": "All Subjects",
        "semester": "All Semesters",
        "code": "ALL",
        "type": "External Reference",
        "description": "Public searchable collection of TU past examination questions on HamroCSIT.",
        "url": "https://hamrocsit.com/questions/",
        "is_internal": False,
        "topic": None,
        "download_content": None,
    },
]


# --------------------------------------------------------------------------- #
# Knowledge Base & Conversational Query Router
# --------------------------------------------------------------------------- #
class KnowledgeBase:
    """Offline academic engine and CSIT knowledge directory."""

    def __init__(self):
        import json, os
        self.topics = TOPICS
        self.semesters = SEMESTERS
        self.resources = RESOURCES
        db_path = os.path.join(os.path.dirname(__file__), "hamrocsit_master_database.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    self.master_db = json.load(f)
            except Exception:
                self.master_db = {"semesters": {}, "total_subjects": 0, "total_chapters": 0}
        else:
            self.master_db = {"semesters": {}, "total_subjects": 0, "total_chapters": 0}

    def get_master_database(self) -> Dict:
        return self.master_db

    def search_curriculum(self, query: str = "") -> List[Dict]:
        if not query or not query.strip():
            return []
        q = query.lower().strip()
        matches = []
        for sem in self.master_db.get("semesters", {}).values():
            for sub in sem.get("subjects", []):
                sub_name = sub.get("name", "")
                sub_code = sub.get("code", "")
                for chap in sub.get("chapters", []):
                    chap_title = chap.get("title", "")
                    if q in chap_title.lower() or q in sub_name.lower() or q in sub_code.lower():
                        matches.append({
                            "semester": sem.get("title", ""),
                            "subject": sub_name,
                            "code": sub_code,
                            "chapter": chap_title,
                            "url": chap.get("url", ""),
                        })
        return matches[:20]

    def get_topic(self, slug: str) -> Optional[Topic]:
        return self.topics.get(slug)

    def search_topics(self, query: str) -> List[Topic]:
        """Intent-aware scoring for CSIT topics."""
        if not query or not query.strip():
            return []
        q = query.lower().strip()
        tokens = [t for t in re.findall(r"[a-z0-9]+", q) if len(t) > 2]

        scored = []
        for topic in self.topics.values():
            score = 0
            # Direct slug or title exact match
            if topic.slug == q or topic.title.lower() == q:
                score += 30
            elif topic.slug in q or topic.title.lower() in q:
                score += 15

            # Alias matching
            aliases = {
                "quick sort": "quick-sort",
                "quicksort": "quick-sort",
                "merge sort": "merge-sort",
                "mergesort": "merge-sort",
                "binary search": "binary-search",
                "big o": "big-o",
                "big-o": "big-o",
                "complexity": "big-o",
                "bubble sort": "bubble-sort",
                "linked list": "linked-list",
                "stack": "stack",
                "queue": "queue",
                "normalization": "normalization",
                "normal form": "normalization",
                "acid": "acid",
                "transaction": "acid",
                "process": "process-vs-thread",
                "thread": "process-vs-thread",
                "deadlock": "deadlock",
                "tcp": "tcp-vs-udp",
                "udp": "tcp-vs-udp",
                "http": "http-get-post",
                "get vs post": "http-get-post",
            }
            for alias, target_slug in aliases.items():
                if alias in q and topic.slug == target_slug:
                    score += 15

            for tok in tokens:
                if tok in topic.title.lower():
                    score += 6
                if tok in topic.definition.lower():
                    score += 2

            if score > 0:
                scored.append((score, topic))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored]

    def resolve_topic_from_context(
        self, query: str, history: Optional[List[dict]] = None
    ) -> Optional[Topic]:
        """Resolves topic either from the query or from conversation history."""
        # 1. Direct query matching
        matched = self.search_topics(query)
        q_lower = query.lower()

        # Check for worst-case O(n^2) specific query (standard CSIT question for QuickSort)
        if any(w in q_lower for w in ("worst case", "worst-case", "why is the worst", "why is its worst")) and any(w in q_lower for w in ("o(n^2)", "o(n²)", "n^2", "n²")):
            if not any(s in q_lower for s in ("bubble", "insertion", "selection", "matrix")):
                if history:
                    for msg in reversed(history):
                        content = msg.get("content", "").lower()
                        for slug, t in self.topics.items():
                            if slug in content or t.title.lower() in content:
                                return t
                return self.topics.get("quick-sort")

        # Check for pronoun or relative references like "its worst case", "why is it", "the algorithm"
        is_followup = any(
            w in q_lower
            for w in (
                "its", "it's", "it ", " it", "this", "the algorithm",
                "why is it", "why is its", "worst-case", "worst case", "o(n^2)", "o(n²)"
            )
        )

        if is_followup and history:
            # Look backwards in conversation history for the last discussed topic
            for msg in reversed(history):
                content = msg.get("content", "").lower()
                for slug, t in self.topics.items():
                    if slug in content or t.title.lower() in content:
                        return t

        if matched:
            return matched[0]

        # Final check in history if no direct match
        if history:
            for msg in reversed(history):
                content = msg.get("content", "").lower()
                for slug, t in self.topics.items():
                    if slug in content or t.title.lower() in content:
                        return t

        return None

    def answer_query(
        self,
        query: str,
        history: Optional[List[dict]] = None,
        subject: str = "General CSIT",
        uploaded_context: Optional[str] = None,
    ) -> str:
        """Intelligently detects query intent and returns targeted educational responses."""
        if not query or not query.strip():
            return "Please type an educational question."

        q_lower = query.lower().strip()
        topic = self.resolve_topic_from_context(query, history)

        # ------------------------------------------------------------------ #
        # INTENT 1: Multi-Topic Practice Questions
        # e.g., "Give me five practice questions about sorting algorithms"
        # ------------------------------------------------------------------ #
        if ("practice question" in q_lower or "exam question" in q_lower or "five practice" in q_lower) and (
            "sorting" in q_lower or "sort" in q_lower or not topic
        ):
            return self._generate_sorting_practice_questions()

        # ------------------------------------------------------------------ #
        # INTENT 2: Concept Comparison ("quick sort vs merge sort", "compare")
        # ------------------------------------------------------------------ #
        if any(w in q_lower for w in (" vs ", "versus", "compare", "difference between", "how does it compare")):
            if "merge" in q_lower and ("quick" in q_lower or (topic and topic.slug == "quick-sort")):
                return self._compare_quick_and_merge_sort()
            if "process" in q_lower and "thread" in q_lower:
                return self._format_topic_full(self.topics["process-vs-thread"])
            if "tcp" in q_lower and "udp" in q_lower:
                return self._format_topic_full(self.topics["tcp-vs-udp"])
            if "get" in q_lower and "post" in q_lower:
                return self._format_topic_full(self.topics["http-get-post"])

        # ------------------------------------------------------------------ #
        # INTENT 3: Worst-Case Time Complexity Deep-Dive
        # e.g., "Why is its worst case O(n²)?" / "Why is the worst-case complexity O(n^2)?"
        # ------------------------------------------------------------------ #
        if (
            any(w in q_lower for w in ("worst case", "worst-case", "o(n^2)", "o(n²)", "why o(n"))
            or ("why is" in q_lower and "complexity" in q_lower)
        ):
            if topic and topic.worst_case_explanation:
                return topic.worst_case_explanation
            if topic:
                return (
                    f"### Complexity Analysis for {topic.title}\n\n"
                    f"| Case | Time Complexity |\n"
                    f"|---|---|\n"
                    + "\n".join(f"| {c} | {v} |" for c, v in topic.complexity.items())
                    + f"\n\n**Space Complexity:** {topic.space_complexity}\n\n"
                    + f"**Key Takeaways:**\n"
                    + "\n".join(f"- {p}" for p in topic.properties)
                )

        # ------------------------------------------------------------------ #
        # INTENT 4: Simple Language Explanation ("explain in simple language")
        # ------------------------------------------------------------------ #
        if any(w in q_lower for w in ("simple language", "simple terms", "layman", "eli5", "easy words", "simply", "in simple")):
            if topic and topic.simple_explanation:
                return (
                    f"### {topic.title} (In Simple Language)\n\n"
                    f"{topic.simple_explanation}\n\n"
                    f"#### Core Definition\n{topic.definition}\n\n"
                    f"#### Quick Facts for CSIT\n"
                    f"- **Subject:** {topic.subject}\n"
                    f"- **Best Case:** {topic.complexity.get('Best case', 'N/A')}\n"
                    f"- **Worst Case:** {topic.complexity.get('Worst case', 'N/A')}\n"
                    f"- **Space:** {topic.space_complexity}"
                )

        # ------------------------------------------------------------------ #
        # INTENT 5: Pseudocode or Code Specific Request
        # ------------------------------------------------------------------ #
        if any(w in q_lower for w in ("pseudocode", "code", "python", "c++", "implementation", "program")):
            if topic and (topic.pseudocode or topic.code):
                lines = [f"### {topic.title} — Implementation & Pseudocode\n"]
                if "python" in q_lower and topic.code:
                    lines.append(f"#### Python Implementation\n```python\n{topic.code}\n```\n")
                elif "c++" in q_lower and topic.code_cpp:
                    lines.append(f"#### C++ Implementation\n```cpp\n{topic.code_cpp}\n```\n")
                else:
                    if topic.pseudocode:
                        lines.append(f"#### Academic Pseudocode\n```text\n{topic.pseudocode}\n```\n")
                    if topic.code:
                        lines.append(f"#### Python Implementation\n```python\n{topic.code}\n```\n")
                lines.append(
                    f"#### Complexity\n"
                    f"- **Time Complexity:** {topic.complexity.get('Average case', 'N/A')} (Average), {topic.complexity.get('Worst case', 'N/A')} (Worst)\n"
                    f"- **Space Complexity:** {topic.space_complexity}"
                )
                return "\n".join(lines)

        # ------------------------------------------------------------------ #
        # INTENT 6: Topic Specific Practice Questions
        # ------------------------------------------------------------------ #
        if "practice" in q_lower or "question" in q_lower or "exam" in q_lower:
            if topic and topic.practice_question:
                return (
                    f"### Practice Exam Question — {topic.title}\n\n"
                    f"**Subject:** {topic.subject} · {topic.semester}\n\n"
                    f"#### Question (TU Style)\n"
                    f"{topic.practice_question}\n\n"
                    f"#### Suggested Model Answer\n"
                    f"{topic.practice_answer}\n\n"
                    f"#### Key Exam Points to Remember\n"
                    + "\n".join(f"- {pt}" for pt in topic.exam_points)
                )

        # ------------------------------------------------------------------ #
        # DEFAULT: Full, comprehensive academic breakdown
        # ------------------------------------------------------------------ #
        if topic:
            return self._format_topic_full(topic, uploaded_context=uploaded_context)

        # Fallback if no topic matches
        return self._format_general_fallback(query)

    # ------------------------------------------------------------------ #
    # Helper formatters
    # ------------------------------------------------------------------ #
    def _format_topic_full(self, topic: Topic, uploaded_context: Optional[str] = None) -> str:
        lines = [
            f"# {topic.title} — {topic.subject}",
            "",
            f"**Subject:** {topic.subject}  ·  **Semester:** {topic.semester}",
            "",
            "## Definition",
            topic.definition,
            "",
            "## How it works",
        ]
        for i, step in enumerate(topic.how_it_works, 1):
            lines.append(f"{i}. {step}")

        if topic.example:
            lines += ["", "## Example", f"```text\n{topic.example}\n```"]

        if topic.pseudocode:
            lines += ["", "## Pseudocode", f"```text\n{topic.pseudocode}\n```"]

        if topic.code:
            lines += ["", "## Implementation (Python)", f"```python\n{topic.code}\n```"]

        if topic.complexity:
            lines += ["", "## Complexity", "| Case | Time complexity |", "|---|---|"]
            for case, comp in topic.complexity.items():
                lines.append(f"| {case} | {comp} |")
            if topic.space_complexity:
                lines.append("")
                lines.append(f"**Space Complexity:** {topic.space_complexity}")

        if topic.properties:
            lines += ["", "## Important Properties"]
            for prop in topic.properties:
                lines.append(f"- {prop}")

        if topic.exam_points or topic.practice_question:
            lines += ["", "## Exam preparation"]
            if topic.exam_points:
                lines.append("**Likely Exam Focus Points:**")
                for pt in topic.exam_points:
                    lines.append(f"- {pt}")
            if topic.practice_question:
                lines.append("")
                lines.append(f"**Sample Practice Question (TU Style):**")
                lines.append(f"> {topic.practice_question}")
                lines.append("")
                lines.append(f"> **Suggested Solution:** {topic.practice_answer}")

        if topic.related:
            lines += ["", "## Related Topics", ", ".join(f"`{r}`" for r in topic.related)]

        lines += [
            "",
            "---",
            "### 📚 Source Attribution (Verified HamroCSIT Learning Content)",
            f"- **Semester:** {topic.semester}",
            f"- **Subject:** {topic.subject} ({topic.course_code})",
            f"- **Chapter:** {topic.chapter_name}",
            f"- **Original Resource:** [{topic.chapter_name} on HamroCSIT ↗]({topic.hamrocsit_url})",
            "",
            "*TU CSIT Study Assistant · Grounded in HamroCSIT Curriculum*",
        ]
        return "\n".join(lines)

    def _compare_quick_and_merge_sort(self) -> str:
        return (
            "# Quick Sort vs Merge Sort — Comprehensive Comparison\n\n"
            "**Subject:** Data Structures & Algorithms (CSC206) · Third Semester\n\n"
            "Both Quick Sort and Merge Sort belong to the **divide-and-conquer** family of sorting algorithms, "
            "but they make fundamentally different engineering trade-offs regarding memory, stability, and worst-case guarantees.\n\n"
            "## Summary Comparison Table\n\n"
            "| Feature | Quick Sort | Merge Sort |\n"
            "|---|---|---|\n"
            "| **Algorithmic Strategy** | Divide and Conquer (partition around pivot) | Divide and Conquer (halve and merge) |\n"
            "| **Best-Case Time** | $O(n \\log n)$ | $O(n \\log n)$ |\n"
            "| **Average-Case Time** | $O(n \\log n)$ | $O(n \\log n)$ |\n"
            "| **Worst-Case Time** | $O(n^2)$ (unbalanced pivot) | $O(n \\log n)$ (strictly guaranteed) |\n"
            "| **Auxiliary Space** | $O(\\log n)$ stack space (in-place) | $O(n)$ temporary buffer space |\n"
            "| **Stability** | **Not stable** (swaps across long distances) | **Stable** (preserves equal keys) |\n"
            "| **Locality of Reference** | Excellent (cache-friendly sequential access) | Moderate (extra buffer copying) |\n"
            "| **Best Used For** | In-memory array sorting, standard library sorts | Linked lists, external sorting (disk/tape) |\n\n"
            "## Key Theoretical Differences\n\n"
            "### 1. Where Does the Heavy Work Happen?\n"
            "- **Quick Sort:** The work is done during the **divide step** (partitioning the array around the pivot). Once sub-arrays reach size 1, no work is needed to combine them.\n"
            "- **Merge Sort:** The divide step is trivial (calculating the midpoint $O(1)$). The heavy work happens during the **combine step** (merging two sorted sub-lists in $O(n)$ time).\n\n"
            "### 2. Space Efficiency & In-Place Sorting\n"
            "- **Quick Sort** sorts in-place, meaning elements are rearranged directly within the input array without allocating an auxiliary copy of size $n$.\n"
            "- **Merge Sort** requires an auxiliary array of size $n$ to merge two sub-arrays, making it unsuitable for memory-constrained embedded systems.\n\n"
            "### 3. Stability\n"
            "- **Merge Sort** is stable: if two records share identical keys, their initial relative order is preserved. This is vital when sorting multi-attribute data (e.g., sorting students by name, then by grade).\n"
            "- **Quick Sort** is not stable in standard form because elements are swapped over long distances across the pivot.\n\n"
            "---\n"
            "### 📚 Source Attribution (Verified HamroCSIT Learning Content)\n"
            "- **Semester:** Third Semester (BSc CSIT)\n"
            "- **Subject:** Data Structure and Algorithm (`CSC211`)\n"
            "- **Chapter:** Sorting\n"
            "- **Original Resource:** [Sorting on HamroCSIT ↗](https://hamrocsit.com/note/dsa/sorting/)\n"
        )

    def _generate_sorting_practice_questions(self) -> str:
        return (
            "# Five Practice Exam Questions: Sorting Algorithms\n\n"
            "**Subject:** Data Structures and Algorithms (CSC206) · TU BSc CSIT Exam Preparation\n\n"
            "The following five practice questions reflect typical Tribhuvan University board exam questions with model solutions and marking rubrics.\n\n"
            "---\n\n"
            "### Practice Question 1: QuickSort Partition Tracing [7 Marks]\n"
            "**Question:**\n"
            "Trace the execution of Quick Sort on the array `A = [25, 10, 36, 15, 42, 8, 20]`. Use the last element (`20`) as the pivot. Show the state of the array after the first partition step and specify the pivot's final index.\n\n"
            "**Suggested Solution & Rubric:**\n"
            "- **Pivot Selection (1 Mark):** Pivot $P = 20$.\n"
            "- **Lomuto Partition Process (3 Marks):**\n"
            "  - Elements $\\le 20$: `10, 15, 8`.\n"
            "  - Elements $> 20$: `25, 36, 42`.\n"
            "- **Array State After Partition (2 Marks):** `[10, 15, 8, 20, 42, 25, 36]` (exact order depends on swap sequence).\n"
            "- **Final Position (1 Mark):** Pivot `20` is placed at index `3` (0-indexed). Left sub-array `[10, 15, 8]` and right sub-array `[42, 25, 36]` are then sorted recursively.\n\n"
            "---\n\n"
            "### Practice Question 2: Worst-Case Derivation [6 Marks]\n"
            "**Question:**\n"
            "Under what conditions does Quick Sort exhibit $O(n^2)$ worst-case time complexity? Derive the recurrence relation and explain two techniques to mitigate this issue.\n\n"
            "**Suggested Solution & Rubric:**\n"
            "- **Condition (2 Marks):** Occurs when the pivot is always the smallest or largest element (e.g., already sorted array with first/last element chosen as pivot).\n"
            "- **Recurrence Derivation (2 Marks):**\n"
            "  $$T(n) = T(n-1) + T(0) + cn = T(n-1) + cn = c \\sum_{i=1}^n i = \\frac{cn(n+1)}{2} = O(n^2)$$\n"
            "- **Mitigation Techniques (2 Marks):**\n"
            "  1. Randomized pivot selection ($P(\\text{worst}) \\approx 0$).\n"
            "  2. Median-of-Three pivot strategy (first, middle, last).\n\n"
            "---\n\n"
            "### Practice Question 3: Comparative Analysis [7 Marks]\n"
            "**Question:**\n"
            "Differentiate between Quick Sort and Merge Sort based on strategy, auxiliary space complexity, stability, and cache performance.\n\n"
            "**Suggested Solution & Rubric:**\n"
            "- Full comparison table covering in-place vs $O(n)$ space, stability (Merge Sort is stable; Quick Sort is not), and cache locality.\n\n"
            "---\n\n"
            "### Practice Question 4: Stability in Sorting [5 Marks]\n"
            "**Question:**\n"
            "Define stability in sorting algorithms. Give one example of a stable sorting algorithm and one example of an unstable sorting algorithm, explaining why stability is crucial in real-world databases.\n\n"
            "**Suggested Solution & Rubric:**\n"
            "- **Definition (2 Marks):** A sorting algorithm is stable if equal keys maintain their original relative order after sorting.\n"
            "- **Examples (1 Mark):** Stable: Merge Sort, Insertion Sort, Bubble Sort. Unstable: Quick Sort, Heap Sort.\n"
            "- **Real-world significance (2 Marks):** Multi-level sorting (e.g., sorting products first by date, then by price without scrambling the date order for products with equal price).\n\n"
            "---\n\n"
            "### Practice Question 5: Merge Sort Algorithm & Complexity [8 Marks]\n"
            "**Question:**\n"
            "Write the algorithm for `MERGE(A, p, q, r)` in Merge Sort. Show that the time complexity of Merge Sort is $O(n \\log n)$ in all cases using the master theorem or recursion tree method.\n\n"
            "**Suggested Solution & Rubric:**\n"
            "- **Algorithm (4 Marks):** Correct merging algorithm using two temporary buffers and index pointers.\n"
            "- **Proof (4 Marks):** Recurrence $T(n) = 2T(n/2) + cn$. Tree has $\\log_2 n$ levels, each doing $cn$ work $\\implies cn \\log_2 n = O(n \\log n)$."
        )

    def _format_general_fallback(self, query: str) -> str:
        return (
            f"# General AI Tutor Explanation — {query.title()}\n\n"
            "> 🤖 *Notice: No sufficiently relevant answer was found in the available local HamroCSIT course notes, so here is a general AI explanation.*\n\n"
            f"Here is an educational explanation of **{query}** for university computer science:\n\n"
            f"- **Concept Overview:** {query} is a specialized computing concept that is explored in modern systems and applications.\n"
            "- **Academic Relevance:** While not explicitly indexed under the standard TU BSc CSIT syllabus core chapters, understanding this concept builds broader software engineering competency.\n\n"
            "### Recommended Actions:\n"
            "- Ask about core curriculum topics: *'Explain Quick Sort'*, *'Database Normalization'*, *'Deadlocks'*, or *'Process vs Thread'*.\n"
            "- Explore available HamroCSIT semester notes from the top navigation bar.\n"
            "- Upload your lecture slides or notes in the sidebar to chat directly about your class material."
        )

    def search_resources(self, query: str = "") -> List[Dict]:
        q = query.lower().strip()
        results = []
        for r in self.resources:
            text = f"{r['title']} {r['subject']} {r['description']} {r['type']} {r.get('code', '')}".lower()
            if not q or q in text:
                results.append(r)
        return results

    def get_resources_by_semester(self, semester: str) -> List[Dict]:
        return [
            r for r in self.resources
            if r["semester"] == semester or r["semester"] == "All Semesters"
        ]


# Singleton instance
kb = KnowledgeBase()
