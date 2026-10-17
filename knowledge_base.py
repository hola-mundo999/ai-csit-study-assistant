"""Curated offline CSIT knowledge base.

Provides educationally useful explanations for common TU BSc CSIT topics when no
external AI provider is configured. Every entry is original study material written
for this platform; none is copied from HamroCSIT or any other third party.

Topics are keyed by a stable slug and organized by subject and semester so the
floating AI tutor and resource browser can serve answers without relying on a
live model.
"""

from typing import Dict, List, Optional


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
        complexity: Optional[Dict[str, str]] = None,
        space_complexity: Optional[str] = None,
        properties: Optional[List[str]] = None,
        exam_points: Optional[List[str]] = None,
        practice_question: Optional[str] = None,
        practice_answer: Optional[str] = None,
        related: Optional[List[str]] = None,
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
        self.complexity = complexity or {}
        self.space_complexity = space_complexity or ""
        self.properties = properties or []
        self.exam_points = exam_points or []
        self.practice_question = practice_question
        self.practice_answer = practice_answer
        self.related = related or []


# --------------------------------------------------------------------------- #
# Curated topics (original educational content)
# --------------------------------------------------------------------------- #
TOPICS: Dict[str, Topic] = {}

TOPICS["quick-sort"] = Topic(
    slug="quick-sort",
    title="Quick Sort",
    subject="Data Structures & Algorithms",
    semester="Fourth Semester",
    definition=(
        "Quick Sort is a divide-and-conquer sorting algorithm. It selects a "
        "pivot element from the array, partitions the remaining elements into "
        "two sub-arrays — those less than the pivot and those greater than the "
        "pivot — and then recursively sorts the sub-arrays. The sorted "
        "sub-arrays combine to produce the final sorted array."
    ),
    how_it_works=[
        "Choose a pivot element from the array (commonly the last, first, or a random element).",
        "Partition the array around the pivot so that elements smaller than the pivot are on its left and elements greater than the pivot are on its right.",
        "Recursively apply Quick Sort to the left partition.",
        "Recursively apply Quick Sort to the right partition.",
        "When the partitions have zero or one element, they are already sorted; combining them yields the sorted array.",
    ],
    example=(
        "Consider the array:\n"
        "`[7, 2, 9, 4, 3]`\n"
        "\n"
        "Using `4` as the first pivot, one possible partition is:\n"
        "`[2, 3] | 4 | [7, 9]`\n"
        "\n"
        "Sorting the partitions produces:\n"
        "`[2, 3, 4, 7, 9]`\n"
        "\n"
        "The exact intermediate partition depends on the partitioning scheme and pivot choice."
    ),
    pseudocode=(
        "QUICKSORT(A, low, high):\n"
        "    if low < high:\n"
        "        p = PARTITION(A, low, high)\n"
        "        QUICKSORT(A, low, p - 1)\n"
        "        QUICKSORT(A, p + 1, high)"
    ),
    code=(
        "def quicksort(arr, low, high):\n"
        "    if low < high:\n"
        "        p = partition(arr, low, high)\n"
        "        quicksort(arr, low, p - 1)\n"
        "        quicksort(arr, p + 1, high)\n"
        "\n"
        "def partition(arr, low, high):\n"
        "    pivot = arr[high]\n"
        "    i = low - 1\n"
        "    for j in range(low, high):\n"
        "        if arr[j] <= pivot:\n"
        "            i += 1\n"
        "            arr[i], arr[j] = arr[j], arr[i]\n"
        "    arr[i + 1], arr[high] = arr[high], arr[i + 1]\n"
        "    return i + 1"
    ),
    complexity={
        "Best case": "O(n log n)",
        "Average case": "O(n log n)",
        "Worst case": "O(n^2)",
    },
    space_complexity=(
        "Typical in-place implementations use O(log n) average auxiliary stack "
        "space and can use O(n) stack space in the worst case."
    ),
    properties=[
        "Quick Sort is an in-place sorting algorithm (aside from recursion stack space).",
        "Standard Quick Sort is not stable; equal elements may change relative order.",
        "It is cache-friendly and often faster in practice than other O(n log n) algorithms.",
        "The worst case O(n^2) occurs when the pivot is repeatedly the smallest or largest element (e.g., already sorted input with a poor pivot choice).",
    ],
    exam_points=[
        "Quick Sort uses the divide-and-conquer strategy.",
        "The PARTITION step is the heart of Quick Sort.",
        "Average and best case time complexity is O(n log n); worst case is O(n^2).",
        "Randomized pivot selection makes the worst case unlikely in practice.",
        "Quick Sort is generally preferred over Merge Sort for arrays because it sorts in place.",
    ],
    practice_question=(
        "Trace Quick Sort on the array `[9, 3, 7, 1, 6]` using the last element as the pivot. "
        "Show the array after the first partition."
    ),
    practice_answer=(
        "Pivot = 6 (last element). After partitioning around 6, elements <= 6 move to the left "
        "and elements > 6 to the right, giving one valid result of `[3, 1] | 6 | [9, 7]`. "
        "Then Quick Sort is applied recursively to `[3, 1]` and `[9, 7]`, producing the final "
        "sorted array `[1, 3, 6, 7, 9]`. The exact intermediate arrangement depends on the "
        "partitioning scheme used."
    ),
    related=["merge-sort", "bubble-sort", "partition"],
)

TOPICS["merge-sort"] = Topic(
    slug="merge-sort",
    title="Merge Sort",
    subject="Data Structures & Algorithms",
    semester="Fourth Semester",
    definition=(
        "Merge Sort is a divide-and-conquer, stable sorting algorithm that divides "
        "the array into two halves, recursively sorts each half, and then merges the "
        "two sorted halves back together."
    ),
    how_it_works=[
        "Divide the array into two halves until each sub-array has one element.",
        "Recursively sort the left and right halves.",
        "Merge the two sorted halves by repeatedly taking the smaller front element.",
        "The merged result is a fully sorted array.",
    ],
    example=(
        "Consider `[38, 27, 43, 3, 9, 82, 10]`.\n"
        "Split into `[38, 27, 43]` and `[3, 9, 82, 10]`, sort each half, then merge "
        "to get `[3, 9, 10, 27, 38, 43, 82]`."
    ),
    pseudocode=(
        "MERGE-SORT(A, p, r):\n"
        "    if p < r:\n"
        "        q = floor((p + r) / 2)\n"
        "        MERGE-SORT(A, p, q)\n"
        "        MERGE-SORT(A, q + 1, r)\n"
        "        MERGE(A, p, q, r)"
    ),
    complexity={
        "Best case": "O(n log n)",
        "Average case": "O(n log n)",
        "Worst case": "O(n log n)",
    },
    space_complexity="O(n) auxiliary space for the temporary merge array.",
    properties=[
        "Merge Sort is stable — equal elements preserve their relative order.",
        "It guarantees O(n log n) time in all cases.",
        "It requires O(n) extra memory, making it less space-efficient than in-place Quick Sort for arrays.",
        "Well suited for sorting linked lists and external (disk-based) data.",
    ],
    exam_points=[
        "Merge Sort always divides the array into two equal halves.",
        "Time complexity is O(n log n) in best, average, and worst cases.",
        "Merge Sort is stable; Quick Sort is typically not stable.",
        "Merge Sort uses O(n) auxiliary space.",
    ],
    practice_question=(
        "Merge the two sorted sub-arrays `[2, 5, 8]` and `[1, 4, 7]` and show the result."
    ),
    practice_answer="`[1, 2, 4, 5, 7, 8]`.",
    related=["quick-sort"],
)

TOPICS["binary-search"] = Topic(
    slug="binary-search",
    title="Binary Search",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    definition=(
        "Binary Search is an efficient search algorithm that finds the position of a "
        "target value within a sorted array by repeatedly halving the search interval."
    ),
    how_it_works=[
        "Compare the target with the middle element of the sorted array.",
        "If they match, return the middle index.",
        "If the target is smaller, continue searching the left half.",
        "If the target is larger, continue searching the right half.",
        "Repeat until the target is found or the interval is empty.",
    ],
    example=(
        "Search for `7` in `[1, 3, 5, 7, 9, 11, 13]`.\n"
        "Middle element is `7` — found at index 3 (0-based)."
    ),
    pseudocode=(
        "BINARY-SEARCH(A, target):\n"
        "    low = 0\n"
        "    high = length(A) - 1\n"
        "    while low <= high:\n"
        "        mid = floor((low + high) / 2)\n"
        "        if A[mid] == target:\n"
        "            return mid\n"
        "        if A[mid] < target:\n"
        "            low = mid + 1\n"
        "        else:\n"
        "            high = mid - 1\n"
        "    return not found"
    ),
    complexity={
        "Best case": "O(1)",
        "Average case": "O(log n)",
        "Worst case": "O(log n)",
    },
    space_complexity="O(1) iterative; O(log n) recursive due to stack space.",
    properties=[
        "Requires the array to be sorted beforehand.",
        "Eliminates half of the remaining elements at each step.",
        "Much faster than linear search O(n) for large sorted arrays.",
    ],
    exam_points=[
        "Binary Search works only on sorted arrays.",
        "Time complexity is O(log n).",
        "Space complexity is O(1) iterative or O(log n) recursive.",
    ],
    practice_question=(
        "How many comparisons does Binary Search make in the worst case to search an array of 1024 elements?"
    ),
    practice_answer=(
        "At most log2(1024) = 10 comparisons in the worst case."
    ),
    related=["linear-search"],
)

TOPICS["big-o"] = Topic(
    slug="big-o",
    title="Big-O Notation",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    definition=(
        "Big-O notation describes the upper bound on the growth of an algorithm's "
        "running time or space usage as the input size grows. It expresses the "
        "worst-case rate of growth, ignoring constant factors and lower-order terms."
    ),
    how_it_works=[
        "Count the basic operations an algorithm performs as a function of input size n.",
        "Keep only the fastest-growing term.",
        "Drop constant coefficients (e.g., 3n^2 + 2n + 1 becomes O(n^2)).",
        "The result classifies the algorithm's efficiency family.",
    ],
    example=(
        "A loop that runs n times doing constant work is O(n).\n"
        "A nested loop running n times inside another n times is O(n^2).\n"
        "Binary Search halving the search space each step is O(log n)."
    ),
    complexity={
        "Constant": "O(1)",
        "Logarithmic": "O(log n)",
        "Linear": "O(n)",
        "Linearithmic": "O(n log n)",
        "Quadratic": "O(n^2)",
        "Cubic": "O(n^3)",
        "Exponential": "O(2^n)",
    },
    properties=[
        "Big-O describes the worst-case upper bound.",
        "Big-Theta (Θ) describes tight bound; Big-Omega (Ω) describes lower bound.",
        "Useful for comparing algorithms independent of hardware or language.",
    ],
    exam_points=[
        "Big-O gives the upper bound on growth rate.",
        "Drop constants and lower-order terms.",
        "Common classes: O(1), O(log n), O(n), O(n log n), O(n^2), O(2^n).",
    ],
    practice_question=(
        "What is the Big-O of a single loop that runs from 1 to n?"
    ),
    practice_answer="O(n) — linear time.",
    related=["quick-sort", "merge-sort"],
)

TOPICS["linked-list"] = Topic(
    slug="linked-list",
    title="Linked List",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    definition=(
        "A Linked List is a linear collection of data elements called nodes, where "
        "each node points to the next node by means of a pointer. It is a dynamic "
        "data structure whose size can grow or shrink at runtime."
    ),
    how_it_works=[
        "Each node contains data and a reference (pointer) to the next node.",
        "The first node is called the head; the last node points to null.",
        "Insertion and deletion only require updating pointers, not shifting elements.",
        "Accessing an element by index requires traversing from the head.",
    ],
    pseudocode=(
        "INSERT-AT-HEAD(L, x):\n"
        "    node = new Node(x)\n"
        "    node.next = L.head\n"
        "    L.head = node"
    ),
    complexity={
        "Access": "O(n)",
        "Search": "O(n)",
        "Insert at head": "O(1)",
        "Delete at head": "O(1)",
    },
    properties=[
        "Dynamic size — no need to pre-allocate like an array.",
        "Insertion/deletion at known positions is O(1).",
        "Random access is not supported; traversal is O(n).",
        "Extra memory is used for pointers in each node.",
    ],
    exam_points=[
        "Linked list nodes contain data and a next pointer.",
        "Head is the entry point; last node points to null.",
        "Insertion/deletion at head is O(1); access is O(n).",
    ],
    practice_question=(
        "What is the time complexity to insert a node at the head of a linked list?"
    ),
    practice_answer="O(1).",
    related=[],
)

TOPICS["stack"] = Topic(
    slug="stack",
    title="Stack",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    definition=(
        "A Stack is a linear data structure that follows the Last-In, First-Out "
        "(LIFO) principle — the last element added is the first one removed."
    ),
    how_it_works=[
        "Push adds an element to the top of the stack.",
        "Pop removes and returns the top element.",
        "Peek returns the top element without removing it.",
        "Trying to pop from an empty stack causes underflow.",
    ],
    complexity={
        "Push": "O(1)",
        "Pop": "O(1)",
        "Peek": "O(1)",
        "Search": "O(n)",
    },
    properties=[
        "LIFO ordering.",
        "Used for undo mechanisms, expression evaluation, and call-stack management.",
        "Can be implemented using an array or a linked list.",
    ],
    exam_points=[
        "Stack follows Last-In, First-Out (LIFO).",
        "Push and pop are O(1) operations.",
        "Stack overflow occurs when pushing to a full stack; underflow when popping an empty stack.",
    ],
    practice_question=(
        "If you push A, B, C onto a stack and then pop twice, what is the remaining top element?"
    ),
    practice_answer="A.",
    related=["queue"],
)

TOPICS["queue"] = Topic(
    slug="queue",
    title="Queue",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    definition=(
        "A Queue is a linear data structure that follows the First-In, First-Out "
        "(FIFO) principle — the first element added is the first one removed."
    ),
    how_it_works=[
        "Enqueue adds an element to the rear of the queue.",
        "Dequeue removes and returns the front element.",
        "Peek returns the front element without removing it.",
        "Elements are processed in the order they arrived.",
    ],
    complexity={
        "Enqueue": "O(1)",
        "Dequeue": "O(1)",
        "Peek": "O(1)",
        "Search": "O(n)",
    },
    properties=[
        "FIFO ordering.",
        "Used for task scheduling, breadth-first search, and buffering.",
        "Can be implemented using an array (circular queue) or linked list.",
    ],
    exam_points=[
        "Queue follows First-In, First-Out (FIFO).",
        "Enqueue and dequeue are O(1) operations.",
        "Front is the removal end; rear is the insertion end.",
    ],
    practice_question=(
        "If you enqueue A, B, C and then dequeue once, what is the new front element?"
    ),
    practice_answer="B.",
    related=["stack"],
)

TOPICS["bubble-sort"] = Topic(
    slug="bubble-sort",
    title="Bubble Sort",
    subject="Data Structures & Algorithms",
    semester="Third Semester",
    definition=(
        "Bubble Sort is a simple comparison-based sorting algorithm that repeatedly "
        "steps through the list, compares adjacent elements, and swaps them if they "
        "are in the wrong order. The largest unsorted element bubbles to the end on "
        "each pass."
    ),
    how_it_works=[
        "Compare adjacent elements from left to right.",
        "Swap them if they are in the wrong order.",
        "Repeat passes through the list until no swaps are needed.",
        "After each pass, the largest remaining element is in its final position.",
    ],
    example=(
        "Sort `[5, 1, 4, 2]`.\n"
        "Pass 1: `[1, 4, 2, 5]` (5 bubbles to the end).\n"
        "Pass 2: `[1, 2, 4, 5]`.\n"
        "Sorted."
    ),
    pseudocode=(
        "BUBBLE-SORT(A):\n"
        "    for i = 1 to length(A):\n"
        "        for j = 0 to length(A) - i - 1:\n"
        "            if A[j] > A[j + 1]:\n"
        "                swap(A[j], A[j + 1])"
    ),
    complexity={
        "Best case": "O(n)",
        "Average case": "O(n^2)",
        "Worst case": "O(n^2)",
    },
    space_complexity="O(1) auxiliary space.",
    properties=[
        "Simple to understand and implement.",
        "Inefficient for large datasets — O(n^2) average and worst case.",
        "Stable — equal elements keep their relative order.",
        "Best case O(n) when the list is already sorted (with an early-exit flag).",
    ],
    exam_points=[
        "Bubble Sort repeatedly swaps adjacent out-of-order elements.",
        "Worst and average case are O(n^2).",
        "Best case O(n) if already sorted.",
        "Stable sorting algorithm.",
    ],
    practice_question=(
        "After one full pass of Bubble Sort on `[5, 1, 4, 2]`, what is the array?"
    ),
    practice_answer="`[1, 4, 2, 5]` — the largest element 5 has bubbled to the end.",
    related=["quick-sort", "merge-sort"],
)

# DBMS
TOPICS["normalization"] = Topic(
    slug="normalization",
    title="Database Normalization",
    subject="Database Management Systems (DBMS)",
    semester="Fourth Semester",
    definition=(
        "Normalization is the process of organizing data in a database to reduce "
        "redundancy and improve data integrity by dividing large tables into smaller, "
        "related tables and defining relationships between them."
    ),
    how_it_works=[
        "Identify repeating groups and redundant data.",
        "Split tables so each fact is stored in only one place.",
        "Apply normal forms (1NF, 2NF, 3NF, BCNF) progressively.",
        "Use foreign keys to relate the smaller tables.",
    ],
    example=(
        "Instead of storing student name and course in one table, split into "
        "Students(student_id, name) and Enrollments(student_id, course) linked by student_id."
    ),
    complexity={},
    space_complexity="",
    properties=[
        "Reduces data redundancy and update anomalies.",
        "Higher normal forms remove more types of dependency anomalies.",
        "Over-normalization can hurt read performance due to more joins.",
    ],
    exam_points=[
        "1NF: atomic values, no repeating groups.",
        "2NF: 1NF + no partial dependency on a composite key.",
        "3NF: 2NF + no transitive dependency.",
        "BCNF: stricter version of 3NF.",
    ],
    practice_question=(
        "What is the main goal of normalization?"
    ),
    practice_answer="To reduce data redundancy and improve data integrity.",
    related=["acid"],
)

TOPICS["acid"] = Topic(
    slug="acid",
    title="ACID Properties",
    subject="Database Management Systems (DBMS)",
    semester="Fourth Semester",
    definition=(
        "ACID is a set of four properties — Atomicity, Consistency, Isolation, "
        "Durability — that guarantee database transactions are processed reliably "
        "even in the presence of errors or failures."
    ),
    how_it_works=[
        "Atomicity: a transaction is all-or-nothing.",
        "Consistency: a transaction brings the database from one valid state to another.",
        "Isolation: concurrent transactions do not interfere with each other.",
        "Durability: committed transactions survive crashes.",
    ],
    complexity={},
    properties=[
        "Essential for reliable banking, reservation, and financial systems.",
        "Implemented using logs, locking, and write-ahead logging.",
    ],
    exam_points=[
        "Atomicity — all or nothing.",
        "Consistency — valid state transitions.",
        "Isolation — concurrent transactions appear serial.",
        "Durability — committed data survives failures.",
    ],
    practice_question=(
        "Which ACID property ensures that a committed transaction survives a system crash?"
    ),
    practice_answer="Durability.",
    related=["normalization"],
)

# OS
TOPICS["process-vs-thread"] = Topic(
    slug="process-vs-thread",
    title="Process vs Thread",
    subject="Operating Systems",
    semester="Fifth Semester",
    definition=(
        "A Process is an instance of a program in execution with its own memory "
        "space. A Thread is a lightweight unit of execution within a process that "
        "shares the process's memory and resources."
    ),
    how_it_works=[
        "A process has its own address space, file descriptors, and resources.",
        "Threads within a process share the same heap and code, but have separate stacks.",
        "Context switching between threads is faster than between processes.",
        "Threads communicate more easily but a bug in one thread can affect the whole process.",
    ],
    complexity={},
    properties=[
        "Processes are isolated; a crash in one does not directly affect others.",
        "Threads are lightweight and cheaper to create than processes.",
        "Inter-process communication (IPC) is slower than inter-thread communication.",
    ],
    exam_points=[
        "Process = independent execution with own memory.",
        "Thread = lightweight execution sharing process memory.",
        "Thread context switching is faster than process context switching.",
    ],
    practice_question=(
        "Do threads within the same process share the same heap memory?"
    ),
    practice_answer="Yes.",
    related=["deadlock"],
)

TOPICS["deadlock"] = Topic(
    slug="deadlock",
    title="Deadlock",
    subject="Operating Systems",
    semester="Fifth Semester",
    definition=(
        "A Deadlock is a situation where two or more processes are blocked forever, "
        "each waiting for a resource held by another in the set."
    ),
    how_it_works=[
        "Four conditions must hold simultaneously: mutual exclusion, hold and wait, "
        "no preemption, and circular wait.",
        "If all four hold, a deadlock may occur.",
        "Operating systems prevent, avoid, detect, or recover from deadlocks.",
    ],
    complexity={},
    properties=[
        "Mutual exclusion: only one process uses a resource at a time.",
        "Hold and wait: a process holds resources while waiting for more.",
        "No preemption: resources cannot be forcibly taken.",
        "Circular wait: a cycle of processes waits on each other.",
    ],
    exam_points=[
        "Deadlock requires all four Coffman conditions.",
        "Banker's Algorithm is a deadlock avoidance algorithm.",
        "Deadlock can be handled by prevention, avoidance, detection, or recovery.",
    ],
    practice_question=(
        "Name one of the four necessary conditions for deadlock."
    ),
    practice_answer="Mutual exclusion / hold and wait / no preemption / circular wait (any one).",
    related=["process-vs-thread"],
)

# CN
TOPICS["tcp-vs-udp"] = Topic(
    slug="tcp-vs-udp",
    title="TCP vs UDP",
    subject="Computer Networks",
    semester="Sixth Semester",
    definition=(
        "TCP (Transmission Control Protocol) and UDP (User Datagram Protocol) are "
        "transport-layer protocols. TCP is connection-oriented and reliable; UDP is "
        "connectionless and faster but does not guarantee delivery."
    ),
    how_it_works=[
        "TCP establishes a connection (three-way handshake), delivers data in order, "
        "and retransmits lost packets.",
        "UDP sends datagrams without setup, ordering, or retransmission guarantees.",
        "TCP has higher overhead; UDP has lower latency.",
    ],
    complexity={},
    properties=[
        "TCP: reliable, ordered, flow- and congestion-controlled.",
        "UDP: unreliable, unordered, low overhead — suited for streaming and DNS.",
    ],
    exam_points=[
        "TCP is reliable; UDP is not.",
        "TCP uses a three-way handshake; UDP does not.",
        "UDP is preferred for real-time streaming and DNS.",
    ],
    practice_question=(
        "Which protocol is better suited for live video streaming: TCP or UDP?"
    ),
    practice_answer="UDP, because low latency matters more than guaranteed delivery.",
    related=[],
)

# Web
TOPICS["http-get-post"] = Topic(
    slug="http-get-post",
    title="HTTP GET vs POST",
    subject="Web Technologies",
    semester="Sixth Semester",
    definition=(
        "GET and POST are HTTP request methods. GET requests data from a server and "
        "appends parameters to the URL; POST submits data to be processed, typically "
        "in the request body."
    ),
    how_it_works=[
        "GET: idempotent, cacheable, parameters visible in the URL, limited length.",
        "POST: not idempotent by default, data in the body, no URL length limit, more sensitive data can be hidden from the URL.",
    ],
    complexity={},
    properties=[
        "Use GET for retrieving data (search, view).",
        "Use POST for creating or updating data (forms, uploads).",
    ],
    exam_points=[
        "GET appends parameters to the URL; POST sends them in the body.",
        "GET is idempotent; POST generally is not.",
        "POST is more suitable for sensitive or large submissions.",
    ],
    practice_question=(
        "Which HTTP method should be used to submit a registration form?"
    ),
    practice_answer="POST.",
    related=[],
)

# Semester → subject catalog (mirrors HamroCSIT organization)
SEMESTERS = {
    "First Semester": {
        "Introduction to Information Technology": "CSC114",
        "C Programming": "CSC115",
        "Digital Logic": "CSC116",
        "Mathematics I": "MTH117",
        "Physics": "PHY118",
    },
    "Second Semester": {
        "Object Oriented Programming in C++": "CSC155",
        "Microprocessor & Computer Architecture": "CSC156",
        "Probability & Statistics": "MTH157",
        "Digital Logic & Circuits (cont.)": "CSC158",
        "Mathematics II": "MTH159",
    },
    "Third Semester": {
        "Data Structures & Algorithms": "CSC201",
        "Computer Graphics": "CSC202",
        "Numerical Methods": "MTH203",
        "Discrete Mathematics": "MTH204",
        "System Analysis & Design": "CSC205",
    },
    "Fourth Semester": {
        "Object Oriented Software Engineering": "CSC251",
        "Computer Networks": "CSC252",
        "Database Management Systems": "CSC253",
        "Operating Systems": "CSC254",
        "Artificial Intelligence": "CSC255",
    },
    "Fifth Semester": {
        "Design & Analysis of Algorithms": "CSC301",
        "Software Engineering": "CSC302",
        "Cryptography": "CSC303",
        "Modeling & Simulation": "CSC304",
        "Web Technologies": "CSC305",
        "Multimedia & Image Processing": "CSC306",
    },
    "Sixth Semester": {
        "Compiler Design": "CSC351",
        "Advanced Java Programming": "CSC352",
        "E-Governance": "CSC353",
        "Network Security": "CSC354",
        "Dot NET Framework": "CSC355",
        "Technical Writing": "CSC356",
    },
    "Seventh Semester": {
        "Advanced Database Management Systems": "CSC401",
        "Data Mining & Warehousing": "CSC402",
        "Network Security (advanced)": "CSC403",
        "Advanced Java (cont.)": "CSC404",
        "Major Project I": "CSC405",
    },
    "Eight Semester": {
        "Advanced DBMS (cont.)": "CSC451",
        "Advanced Networking": "CSC452",
        "Major Project II": "CSC453",
        "Elective": "CSC454",
    },
}

RESOURCES = [
    {
        "slug": "quick-sort-guide",
        "title": "Quick Sort — Algorithm Guide",
        "subject": "Data Structures & Algorithms",
        "semester": "Fourth Semester",
        "type": "Study Guide",
        "description": "Divide-and-conquer sorting with worked example, pseudocode, Python implementation, and complexity analysis.",
        "url": None,
        "source": "TU CSIT Study Assistant (original)",
        "topic": "quick-sort",
    },
    {
        "slug": "dsa-syllabus",
        "title": "Data Structures & Algorithms — Course Outline",
        "subject": "Data Structures & Algorithms",
        "semester": "Third Semester",
        "type": "Syllabus",
        "description": "Core DSA topics: sorting, searching, linked lists, stacks, queues, trees, graphs.",
        "url": None,
        "source": "TU CSIT Study Assistant (original)",
        "topic": None,
    },
    {
        "slug": "hamrocsit-semesters",
        "title": "HamroCSIT Semester Notes",
        "subject": "All Subjects",
        "semester": "All Semesters",
        "type": "External Reference",
        "description": "Semester-wise CSIT notes, questions, and solutions on HamroCSIT.",
        "url": "https://hamrocsit.com/semester/first/",
        "source": "HamroCSIT (external)",
        "topic": None,
    },
    {
        "slug": "hamrocsit-questions",
        "title": "HamroCSIT Question Bank",
        "subject": "All Subjects",
        "semester": "All Semesters",
        "type": "External Reference",
        "description": "Past TU CSIT exam questions with search by semester and subject.",
        "url": "https://hamrocsit.com/questions/",
        "source": "HamroCSIT (external)",
        "topic": None,
    },
]


class KnowledgeBase:
    """Searchable offline knowledge base of CSIT topics and resources."""

    def __init__(self):
        self.topics = TOPICS
        self.semesters = SEMESTERS
        self.resources = RESOURCES

    def get_topic(self, slug: str) -> Optional[Topic]:
        return self.topics.get(slug)

    def search_topics(self, query: str) -> List[Topic]:
        """Intent-aware search over topic titles and definitions."""
        if not query or not query.strip():
            return []
        q = query.lower().strip()
        tokens = [t for t in __import__("re").findall(r"[a-z0-9]+", q) if len(t) > 2]

        scored = []
        for topic in self.topics.values():
            score = 0
            text = f"{topic.title} {topic.subject} {topic.definition} {' '.join(topic.how_it_works)}".lower()
            # Direct slug/title match
            if q in topic.slug or q in topic.title.lower():
                score += 10
            for tok in tokens:
                if tok in topic.title.lower():
                    score += 5
                if tok in text:
                    score += 2
            # Subject aliases
            aliases = {
                "quick sort": "quick-sort",
                "quicksort": "quick-sort",
                "binary search": "binary-search",
                "big o": "big-o",
                "big-o": "big-o",
                "linked list": "linked-list",
            }
            for alias, slug in aliases.items():
                if alias in q and topic.slug == slug:
                    score += 10
            if score > 0:
                scored.append((score, topic))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored]

    def search_resources(self, query: str = "") -> List[Dict]:
        q = query.lower()
        results = []
        for r in self.resources:
            text = f"{r['title']} {r['subject']} {r['description']} {r['type']}".lower()
            if not q or q in text:
                results.append(r)
        return results

    def get_resources_by_semester(self, semester: str) -> List[Dict]:
        return [r for r in self.resources if r["semester"] == semester or r["semester"] == "All Semesters"]

    def get_topics_by_subject(self, subject: str) -> List[Topic]:
        return [t for t in self.topics.values() if t.subject == subject]


kb = KnowledgeBase()
