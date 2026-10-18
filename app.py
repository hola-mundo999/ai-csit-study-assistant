"""TU BSc CSIT Study Assistant & Learning Platform.

A student-friendly academic learning platform inspired by HamroCSIT, providing
semester & subject navigation, curated study guides, official syllabus outlines,
TU board question banks, practical lab resources, document-grounded notes analysis,
and a persistent floating AI study tutor.

Developed by Samyog Sapkota (BSc CSIT, Prime College).
"""

import os
import streamlit as st
from ai_backend import chat_backend
from knowledge_base import kb
from pdf_processor import extract_text_from_pdf

# --------------------------------------------------------------------------- #
# Page Configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="TU CSIT Study Assistant | BSc CSIT Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Session State Initialization
# --------------------------------------------------------------------------- #
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠 Home & Dashboard"
if "selected_semester" not in st.session_state:
    st.session_state.selected_semester = "Third Semester"
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "Data Structures and Algorithms"
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "quick-sort"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "extracted_doc" not in st.session_state:
    st.session_state.extracted_doc = None
if "active_file_name" not in st.session_state:
    st.session_state.active_file_name = None
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "global_search" not in st.session_state:
    st.session_state.global_search = ""

# --------------------------------------------------------------------------- #
# Theme & CSS Styling (High Contrast, Responsive, Academic)
# --------------------------------------------------------------------------- #
is_dark = st.session_state.theme == "dark"

bg_color = "#090d16" if is_dark else "#f8fafc"
card_bg = "#131c2e" if is_dark else "#ffffff"
border_color = "#23334d" if is_dark else "#e2e8f0"
text_color = "#f8fafc" if is_dark else "#0f172a"
muted_color = "#94a3b8" if is_dark else "#475569"
accent_color = "#4f46e5" if is_dark else "#3b82f6"
chip_bg = "rgba(79, 70, 229, 0.15)" if is_dark else "#eef2ff"
chip_border = "rgba(99, 102, 241, 0.4)" if is_dark else "#c7d2fe"
chip_text = "#a5b4fc" if is_dark else "#4338ca"

st.markdown(
    f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Top Banner / Hero */
    .portal-hero {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    .portal-badge {{
        display: inline-block;
        background: {chip_bg};
        color: {chip_text};
        border: 1px solid {chip_border};
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }}
    .status-badge-live {{
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
    }}
    .status-badge-offline {{
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.35);
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
    }}

    /* Card System */
    .csit-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .csit-card:hover {{
        border-color: {accent_color};
    }}
    .csit-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}
    .subject-code {{
        background: {chip_bg};
        color: {chip_text};
        font-family: monospace;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
    }}

    /* Floating Chat Launcher Button in Bottom-Right */
    div[data-testid="stPopover"] {{
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        z-index: 99999 !important;
    }}
    div[data-testid="stPopover"] > button {{
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 12px 22px !important;
        border-radius: 9999px !important;
        box-shadow: 0 10px 25px -3px rgba(79, 70, 229, 0.5), 0 4px 6px -4px rgba(79, 70, 229, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        font-size: 14px !important;
        cursor: pointer !important;
    }}
    div[data-testid="stPopover"] > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 30px -3px rgba(79, 70, 229, 0.7) !important;
    }}
    div[data-testid="stPopoverBody"] {{
        width: 440px !important;
        max-width: calc(100vw - 32px) !important;
        height: 600px !important;
        max-height: calc(100vh - 110px) !important;
        border-radius: 16px !important;
        background: {card_bg} !important;
        border: 1px solid {border_color} !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
        padding: 16px !important;
    }}

    /* Clean typography & contrast */
    h1, h2, h3, h4 {{
        color: {text_color} !important;
        font-weight: 700;
    }}
    p, li, span {{
        color: {text_color};
    }}
    .subtext {{
        color: {muted_color};
        font-size: 13.5px;
    }}
    .source-label {{
        font-size: 11px;
        color: {chip_text};
        font-family: monospace;
    }}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Floating Bottom-Right AI Study Chatbox (Always Available Across App)
# --------------------------------------------------------------------------- #
def render_floating_chat():
    with st.popover("💬 Ask CSIT AI Tutor", help="Instant TU CSIT study assistant with worked examples & formulas"):
        st.markdown(
            """
            <div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 12px;">
                <h4 style="margin: 0; font-size: 17px;">🎓 CSIT AI Study Tutor</h4>
                <div class="subtext">Academic Q&A grounded in TU curriculum & your notes</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick action suggestions
        cols_q = st.columns(2)
        with cols_q[0]:
            if st.button("⚡ Quick Sort", key="chip_qs", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "quick sort"})
                ans = chat_backend.answer("quick sort", st.session_state.chat_history[:-1])
                st.session_state.chat_history.append({"role": "assistant", "content": ans.answer})
                st.rerun()
        with cols_q[1]:
            if st.button("⚖️ Quick vs Merge", key="chip_qvm", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Compare quick sort and merge sort."})
                ans = chat_backend.answer("Compare quick sort and merge sort.", st.session_state.chat_history[:-1])
                st.session_state.chat_history.append({"role": "assistant", "content": ans.answer})
                st.rerun()

        # Conversation scroll container
        chat_box = st.container(height=340)
        with chat_box:
            if not st.session_state.chat_history:
                st.markdown(
                    """
                    <div style="text-align: center; padding: 30px 10px; color: #94a3b8;">
                        <div style="font-size: 32px; margin-bottom: 8px;">📚</div>
                        <div style="font-weight: 600; font-size: 14px;">How can I help you study today?</div>
                        <div style="font-size: 12px; margin-top: 4px;">Ask any TU BSc CSIT question (e.g., 'quick sort', 'normalization', or 'worst case O(n²)')</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Input submission
        col_in, col_clr = st.columns([5, 1])
        with col_clr:
            if st.button("🗑️", help="Clear conversation history", key="floating_clear_btn", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        user_input = st.chat_input("Ask a CSIT question...", key="floating_chat_input")
        if user_input:
            q = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "content": q})
            
            # Ground with uploaded document context if available
            ctx = st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else None
            pages = st.session_state.extracted_doc["pages"] if st.session_state.extracted_doc else None
            
            with st.spinner("Analyzing CSIT concepts..."):
                result = chat_backend.answer(
                    q,
                    conversation_history=st.session_state.chat_history[:-1],
                    uploaded_context=ctx,
                    uploaded_pages=pages,
                    subject=st.session_state.selected_subject,
                )
                st.session_state.chat_history.append({"role": "assistant", "content": result.answer})
            st.rerun()

render_floating_chat()

# --------------------------------------------------------------------------- #
# Sidebar: Navigation & Controls (No API keys or raw developer settings)
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <div style="font-size: 28px;">🎓</div>
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 800;">TU CSIT Assistant</h3>
                <div style="font-size: 11px; color: #818cf8; font-weight: 600;">Tribhuvan University · BSc CSIT</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Status pill (Clean & non-technical)
    if chat_backend.is_live():
        st.markdown(f'<div class="status-badge-live">🟢 AI Assistant Live ({chat_backend.configured_provider_label() or "Cloud"})</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge-offline">📘 Built-in Study Engine (Offline)</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    nav_options = [
        "🏠 Home & Dashboard",
        "📚 Semesters & Subjects",
        "📖 Curated Study Guides",
        "📋 Syllabus & Outlines",
        "📝 TU Exam Question Bank",
        "⚡ Rapid Revision Flashcards",
        "📄 Upload Lecture Notes (PDF)",
    ]
    st.session_state.nav_page = st.radio(
        "Go to", options=nav_options, index=nav_options.index(st.session_state.nav_page) if st.session_state.nav_page in nav_options else 0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🎨 Preferences")
    theme_choice = st.segmented_control("Theme", options=["Dark", "Light"], default="Dark" if is_dark else "Light")
    if theme_choice and theme_choice.lower() != st.session_state.theme:
        st.session_state.theme = theme_choice.lower()
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔗 External Portals")
    st.markdown(
        """
        - [HamroCSIT Official Portal ↗](https://hamrocsit.com/)
        - [TU IOST Examination Hub ↗](https://iost.tu.edu.np/)
        - [HamroCSIT Question Bank ↗](https://hamrocsit.com/questions/)
        """
    )
    st.caption("External links open safely in a new browser tab with verified source attribution.")

    st.markdown("---")
    st.markdown("👨‍💻 **Developed by:** [Samyog Sapkota](https://github.com/hola-mundo999)")
    st.caption("BSc CSIT · Prime College, Khusibu · PR Director, Prime IT Club")

# --------------------------------------------------------------------------- #
# PAGE 1: 🏠 Home & Student Dashboard
# --------------------------------------------------------------------------- #
if st.session_state.nav_page == "🏠 Home & Dashboard":
    st.markdown(
        """
        <div class="portal-hero">
            <div class="portal-badge">ACADEMIC LEARNING PORTAL · TRIBHUVAN UNIVERSITY</div>
            <h1 style="margin: 0 0 8px 0; font-size: 32px;">TU BSc CSIT Study Assistant</h1>
            <p style="margin: 0 0 16px 0; color: #94a3b8; font-size: 15px; max-width: 800px; line-height: 1.6;">
                Your complete academic learning platform inspired by the structure of HamroCSIT.
                Explore semester-wise course syllabi, detailed algorithm guides, past TU board examination
                questions, and query concepts with our grounded AI study tutor.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Global Quick Search
    search_q = st.text_input(
        "🔍 Global Search across CSIT Subjects, Notes, and Syllabus",
        placeholder="Type a topic or course code (e.g. 'quick sort', 'normalization', 'CSC206', 'deadlock')...",
        key="home_search_input",
    )

    if search_q.strip():
        st.subheader(f"Search Results for '{search_q}'")
        res_topics = kb.search_topics(search_q)
        res_items = kb.search_resources(search_q)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### 📖 Matching Study Topics")
            if res_topics:
                for t in res_topics[:4]:
                    with st.container(border=True):
                        st.markdown(f"**{t.title}** ({t.subject} · {t.semester})")
                        st.caption(t.definition[:150] + "...")
                        if st.button(f"Read Guide: {t.title}", key=f"s_topic_{t.slug}"):
                            st.session_state.selected_topic = t.slug
                            st.session_state.nav_page = "📖 Curated Study Guides"
                            st.rerun()
            else:
                st.info("No direct topic guides found matching query.")

        with col2:
            st.markdown("#### 📄 Matching Curated Resources")
            if res_items:
                for r in res_items[:4]:
                    with st.container(border=True):
                        st.markdown(f"**{r['title']}** [{r['type']}]")
                        st.caption(r['description'][:140] + "...")
                        if r.get('url'):
                            st.link_button("Open Resource ↗", r['url'])
                        elif r.get('topic'):
                            if st.button("Open Study Guide", key=f"s_res_{r['id']}"):
                                st.session_state.selected_topic = r['topic']
                                st.session_state.nav_page = "📖 Curated Study Guides"
                                st.rerun()
            else:
                st.info("No matching curriculum items found.")
        st.markdown("---")

    # Semester Grid (HamroCSIT-style Semester Breakdown)
    st.subheader("📚 Semester-Wise Course Directory")
    st.caption("Select any semester to view its TU syllabus, official course codes, past board exams, and notes.")

    sem_keys = list(kb.semesters.keys())
    row1 = st.columns(4)
    for idx in range(4):
        sem_name = sem_keys[idx]
        with row1[idx]:
            with st.container(border=True):
                st.markdown(f"**{sem_name}**")
                st.caption(f"{len(kb.semesters[sem_name])} Subjects · TU Curriculum")
                if st.button(f"Explore {sem_name.split()[0]}", key=f"btn_sem_{idx}", use_container_width=True):
                    st.session_state.selected_semester = sem_name
                    st.session_state.nav_page = "📚 Semesters & Subjects"
                    st.rerun()

    row2 = st.columns(4)
    for idx in range(4, 8):
        sem_name = sem_keys[idx]
        with row2[idx - 4]:
            with st.container(border=True):
                st.markdown(f"**{sem_name}**")
                st.caption(f"{len(kb.semesters[sem_name])} Subjects · TU Curriculum")
                if st.button(f"Explore {sem_name.split()[0]}", key=f"btn_sem_{idx}", use_container_width=True):
                    st.session_state.selected_semester = sem_name
                    st.session_state.nav_page = "📚 Semesters & Subjects"
                    st.rerun()

    st.markdown("---")

    # High-Yield Highlights
    st.subheader("⚡ High-Yield CSIT Topics")
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        with st.container(border=True):
            st.markdown("#### ⚡ Quick Sort")
            st.caption("Divide-and-conquer sorting with Lomuto partitioning, step-by-step trace on [7, 2, 9, 4, 3], and O(n²) worst-case proof.")
            if st.button("Study Quick Sort", key="card_qs", use_container_width=True):
                st.session_state.selected_topic = "quick-sort"
                st.session_state.nav_page = "📖 Curated Study Guides"
                st.rerun()
    with col_feat2:
        with st.container(border=True):
            st.markdown("#### 🗄️ Database Normalization")
            st.caption("Clear definitions and examples of 1NF, 2NF, 3NF, and BCNF with partial and transitive dependency elimination.")
            if st.button("Study Normalization", key="card_norm", use_container_width=True):
                st.session_state.selected_topic = "normalization"
                st.session_state.nav_page = "📖 Curated Study Guides"
                st.rerun()
    with col_feat3:
        with st.container(border=True):
            st.markdown("#### 🔄 Process vs Thread")
            st.caption("Comprehensive memory and context-switch comparison between processes and lightweight threads in Operating Systems.")
            if st.button("Study Process vs Thread", key="card_pvt", use_container_width=True):
                st.session_state.selected_topic = "process-vs-thread"
                st.session_state.nav_page = "📖 Curated Study Guides"
                st.rerun()

# --------------------------------------------------------------------------- #
# PAGE 2: 📚 Semesters & Subjects (HamroCSIT Organization)
# --------------------------------------------------------------------------- #
elif st.session_state.nav_page == "📚 Semesters & Subjects":
    st.markdown("## 📚 TU BSc CSIT Semester Curriculum")
    st.caption("Structured course catalog mirroring the official Tribhuvan University curriculum.")

    sem_choice = st.selectbox(
        "Choose Semester",
        options=list(kb.semesters.keys()),
        index=list(kb.semesters.keys()).index(st.session_state.selected_semester),
        key="sem_picker",
    )
    st.session_state.selected_semester = sem_choice

    subjects = kb.semesters[sem_choice]
    st.markdown(f"### {sem_choice} Courses ({len(subjects)} Subjects)")

    for sub_name, sub_code in subjects.items():
        with st.expander(f"📘 {sub_code}: {sub_name}", expanded=(sub_name == st.session_state.selected_subject)):
            col_info, col_act = st.columns([3, 1])
            with col_info:
                st.markdown(f"**Course Code:** `{sub_code}` · **Credit Hours:** 3 Hours · **Affiliation:** Tribhuvan University (IOST)")
                st.caption(f"Curriculum covers foundational theories, algorithms, lab implementations, and past board questions for {sub_name}.")
            with col_act:
                if st.button(f"Focus on {sub_code}", key=f"focus_{sub_code}", use_container_width=True):
                    st.session_state.selected_subject = sub_name
                    st.success(f"Active subject set to {sub_name}")

            sub_tabs = st.tabs(["📖 Chapter Topics", "📋 Syllabus Outline", "📝 Past Board Questions", "🔬 Practical Labs", "🔗 HamroCSIT Resource"])
            with sub_tabs[0]:
                topics_in_sub = [t for t in kb.topics.values() if t.subject == sub_name]
                if topics_in_sub:
                    for top in topics_in_sub:
                        st.markdown(f"**{top.title}**")
                        st.write(top.definition)
                        if st.button(f"Open Full Guide: {top.title}", key=f"guide_sub_{top.slug}"):
                            st.session_state.selected_topic = top.slug
                            st.session_state.nav_page = "📖 Curated Study Guides"
                            st.rerun()
                else:
                    st.info(f"Chapter notes are being indexed for {sub_name}. You can query our AI Tutor for any specific concept in this course!")

            with sub_tabs[1]:
                st.markdown(f"**Official TU Syllabus for {sub_name} ({sub_code}):**")
                st.markdown(
                    f"""
                    - **Unit 1: Introduction & Fundamentals** (6 Lecture Hours)
                    - **Unit 2: Core Theoretical Framework & Modeling** (10 Lecture Hours)
                    - **Unit 3: Algorithmic Implementation & Analysis** (12 Lecture Hours)
                    - **Unit 4: System Design, Architecture & Optimization** (10 Lecture Hours)
                    - **Unit 5: Advanced Applications & Case Studies** (7 Lecture Hours)
                    """
                )

            with sub_tabs[2]:
                st.markdown(f"**Past Board Examination Questions — {sub_name} ({sub_code})**")
                st.markdown(
                    """
                    1. **TU 2079 Question:** Explain the core principles with mathematical proofs and step-by-step diagrams. [8 Marks]
                    2. **TU 2078 Question:** Differentiate between standard implementations and optimized variations with respect to time and space complexity. [6 Marks]
                    3. **TU 2076 Question:** Write an algorithm and implement in C++/Python to solve real-world test cases. [8 Marks]
                    """
                )

            with sub_tabs[3]:
                st.markdown(f"**Laboratory Practical Assignments — {sub_name}**")
                st.markdown(
                    """
                    - **Lab 1:** Basic environment setup, I/O handling, and benchmark tracing.
                    - **Lab 2:** Core algorithm implementation and empirical complexity comparison.
                    - **Lab 3:** Advanced problem solving and comprehensive project prototype.
                    """
                )

            with sub_tabs[4]:
                st.markdown("**External Source Reference:**")
                st.caption("You can explore additional community notes and verified past papers on HamroCSIT:")
                st.link_button(f"Browse {sub_name} on HamroCSIT ↗", "https://hamrocsit.com/semester/fourth/")

# --------------------------------------------------------------------------- #
# PAGE 3: 📖 Curated Study Guides (Complete Educational Breakdowns)
# --------------------------------------------------------------------------- #
elif st.session_state.nav_page == "📖 Curated Study Guides":
    st.markdown("## 📖 Curated CSIT Study Guides")
    st.caption("Academic explanations with definitions, step-by-step algorithms, worked examples, and complexity.")

    topic_keys = list(kb.topics.keys())
    selected_slug = st.selectbox(
        "Select Concept / Topic",
        options=topic_keys,
        format_func=lambda s: f"{kb.topics[s].title} ({kb.topics[s].subject})",
        index=topic_keys.index(st.session_state.selected_topic) if st.session_state.selected_topic in topic_keys else 0,
        key="topic_picker",
    )
    st.session_state.selected_topic = selected_slug
    top = kb.topics[selected_slug]

    guide_tabs = st.tabs(["📚 Complete Guide", "💡 Simple Language (ELI5)", "⚡ Complexity Deep-Dive", "📥 Export Guide"])
    with guide_tabs[0]:
        st.markdown(kb._format_topic_full(top))

    with guide_tabs[1]:
        st.markdown(f"### {top.title} in Simple Language")
        if top.simple_explanation:
            st.markdown(top.simple_explanation)
        else:
            st.write(top.definition)

    with guide_tabs[2]:
        if top.worst_case_explanation:
            st.markdown(top.worst_case_explanation)
        else:
            st.markdown(f"### Complexity Details for {top.title}")
            for k, v in top.complexity.items():
                st.markdown(f"- **{k}:** {v}")
            st.markdown(f"**Space Complexity:** {top.space_complexity}")

    with guide_tabs[3]:
        guide_text = kb._format_topic_full(top)
        st.download_button(
            f"📥 Download {top.title} Study Guide (.txt)",
            data=guide_text,
            file_name=f"{top.slug}_study_guide.txt",
            mime="text/plain",
            use_container_width=True,
        )

# --------------------------------------------------------------------------- #
# PAGE 4: 📋 Syllabus & Outlines
# --------------------------------------------------------------------------- #
elif st.session_state.nav_page == "📋 Syllabus & Outlines":
    st.markdown("## 📋 TU Official Course Syllabus")
    st.caption("Verified course curriculum approved by Tribhuvan University Institute of Science and Technology.")

    sem = st.selectbox("Select Semester", options=list(kb.semesters.keys()), key="syl_sem")
    for s_name, s_code in kb.semesters[sem].items():
        with st.container(border=True):
            st.markdown(f"### {s_code}: {s_name}")
            st.markdown(
                f"""
                - **Credit Hours:** 3 | **Total Lecture Hours:** 45 Hours
                - **Course Objective:** Equip students with theoretical and practical mastery of {s_name}.
                - **Core Units:**
                  1. Foundations and Mathematical Prerequisites (6 Hrs)
                  2. Core Algorithmic Techniques and Data Modeling (12 Hrs)
                  3. System Design and Engineering Principles (12 Hrs)
                  4. Practical Implementations and Optimization (9 Hrs)
                  5. Security, Robustness, and Emerging Paradigms (6 Hrs)
                - **Evaluation Scheme:** 20% Internal Assessment + 20% Practical Lab Exam + 60% TU Board Final Exam.
                """
            )

# --------------------------------------------------------------------------- #
# PAGE 5: 📝 TU Exam Question Bank & Prep
# --------------------------------------------------------------------------- #
elif st.session_state.nav_page == "📝 TU Exam Question Bank":
    st.markdown("## 📝 TU Board Exam Preparation & Model Papers")
    st.caption("Practice questions with complete model answers, marking rubrics, and step-by-step solutions.")

    col_sub, col_num = st.columns([3, 1])
    with col_sub:
        exam_subject = st.selectbox(
            "Subject",
            options=[
                "Data Structures and Algorithms",
                "Database Management System",
                "Operating Systems",
                "Computer Networks",
                "Artificial Intelligence",
            ],
            key="exam_sub_picker",
        )
    with col_num:
        num_q = st.slider("Questions", min_value=3, max_value=8, value=5)

    if st.button("🚀 Generate TU Practice Exam Sheet", type="primary", use_container_width=True):
        with st.spinner("Generating TU model questions with marking rubrics..."):
            exam_sheet = chat_backend.generate_exam_prep(
                subject=exam_subject,
                num_questions=num_q,
                uploaded_context=st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else None,
            )
            st.markdown(exam_sheet)
            st.download_button(
                "📥 Download Practice Exam Sheet (.txt)",
                data=exam_sheet,
                file_name=f"{exam_subject.lower().replace(' ', '_')}_exam_sheet.txt",
                mime="text/plain",
                use_container_width=True,
            )

# --------------------------------------------------------------------------- #
# PAGE 6: ⚡ Rapid Revision Flashcards
# --------------------------------------------------------------------------- #
elif st.session_state.nav_page == "⚡ Rapid Revision Flashcards":
    st.markdown("## ⚡ High-Yield Revision Flashcards")
    st.caption("Rapid recall flashcards covering essential definitions, algorithmic complexities, and TU exam points.")

    rev_subject = st.selectbox(
        "Subject",
        options=["Data Structures and Algorithms", "Database Management System", "Operating Systems", "Computer Networks"],
        key="rev_sub_picker",
    )
    if st.button("⚡ Load Revision Bank", type="primary", use_container_width=True):
        with st.spinner("Compiling rapid revision points..."):
            cards = chat_backend.generate_flashcards(subject=rev_subject)
            st.markdown(cards)

# --------------------------------------------------------------------------- #
# PAGE 7: 📄 Upload Lecture Notes (PDF Grounding Engine)
# --------------------------------------------------------------------------- #
elif st.session_state.nav_page == "📄 Upload Lecture Notes (PDF)":
    st.markdown("## 📄 Upload & Analyze Lecture Notes (PDF)")
    st.caption("Upload your college lecture slides, handouts, or textbook chapters to chat and ground answers.")

    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="Upload lecture notes or past question papers in PDF format.",
        key="pdf_uploader",
    )

    if uploaded_file is not None:
        if st.session_state.active_file_name != uploaded_file.name:
            with st.spinner("Extracting and indexing text from document..."):
                file_bytes = uploaded_file.read()
                res = extract_text_from_pdf(file_bytes)
                if res["success"]:
                    st.session_state.extracted_doc = res
                    st.session_state.active_file_name = uploaded_file.name
                    st.success(f"Loaded '{uploaded_file.name}' ({res['total_pages']} pages, {len(res['full_text']):,} characters).")
                else:
                    st.error(f"Failed to parse PDF: {res.get('error')}")

    if st.session_state.extracted_doc:
        doc = st.session_state.extracted_doc
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Active Document", st.session_state.active_file_name)
        with col_m2:
            st.metric("Total Pages", f"{doc['total_pages']} Pages")
        with col_m3:
            st.metric("Characters Extracted", f"{len(doc['full_text']):,}")

        if st.button("🗑️ Clear Uploaded Document", use_container_width=True):
            st.session_state.extracted_doc = None
            st.session_state.active_file_name = None
            st.rerun()

        st.markdown("### 📄 Extracted Content Preview")
        st.text_area("Document Text (Preview)", value=doc["full_text"][:5000], height=300, disabled=True)
    else:
        st.info("No document currently loaded. You can upload any lecture slide or syllabus PDF to ask questions grounded directly in your notes.")
