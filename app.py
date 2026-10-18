"""HAMRO CSIT — Complete BSc CSIT Notes, Question Bank & Intelligent AI Tutor.

A high-fidelity learning platform replicating the information architecture,
semester-wise structure, subject listings, chapters, and resources of HamroCSIT,
powered by a two-tier AI learning assistant:
  Tier 1: Grounded in local HamroCSIT curriculum notes & verified source citations.
  Tier 2: Seamless fallback to general AI (Gemini / Groq / OpenAI) when outside notes.

Developed by Samyog Sapkota (BSc CSIT, Prime College).
"""

import os
import json
import streamlit as st
import streamlit.components.v1 as components
from ai_backend import chat_backend
from knowledge_base import kb
from pdf_processor import extract_text_from_pdf

# --------------------------------------------------------------------------- #
# Page Configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Hamro CSIT — Complete CSIT Notes, Questions Bank & AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load master database
master_db = kb.get_master_database()
semesters_data = master_db.get("semesters", {})

# Load live HamroCSIT content (real questions & notices from WP REST API)
_BASE = os.path.dirname(__file__)
try:
    with open(os.path.join(_BASE, "hamrocsit_live_content.json"), "r", encoding="utf-8") as _f:
        _live_data = json.load(_f)
    LIVE_NOTICES = _live_data.get("notices", [])
    LIVE_QUESTIONS = _live_data.get("questions_by_subject", {})
except Exception:
    LIVE_NOTICES = []
    LIVE_QUESTIONS = {}

try:
    with open(os.path.join(_BASE, "hamrocsit_categories.json"), "r", encoding="utf-8") as _f:
        SUBJECT_CATEGORIES = json.load(_f)
except Exception:
    SUBJECT_CATEGORIES = {}

# --------------------------------------------------------------------------- #
# Session State Initialization
# --------------------------------------------------------------------------- #
if "current_view" not in st.session_state:
    st.session_state.current_view = "home"  # 'home', 'semester', 'subject', 'chapter', 'questions', 'notices', 'ai_tutor', 'upload'
if "active_semester_slug" not in st.session_state:
    st.session_state.active_semester_slug = "fourth"
if "active_subject_slug" not in st.session_state:
    st.session_state.active_subject_slug = "dbms"
if "active_chapter_slug" not in st.session_state:
    st.session_state.active_chapter_slug = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "theme" not in st.session_state:
    st.session_state.theme = "light"  # HamroCSIT is natively a clean white/navy portal
if "extracted_doc" not in st.session_state:
    st.session_state.extracted_doc = None
if "active_file_name" not in st.session_state:
    st.session_state.active_file_name = None

is_dark = st.session_state.theme == "dark"

# --------------------------------------------------------------------------- #
# HamroCSIT Theme & Layout Styling
# --------------------------------------------------------------------------- #
bg_color = "#0b0f19" if is_dark else "#f8fafc"
card_bg = "#131b2e" if is_dark else "#ffffff"
border_color = "#23334d" if is_dark else "#e2e8f0"
text_color = "#f8fafc" if is_dark else "#1e293b"
muted_color = "#94a3b8" if is_dark else "#64748b"
primary_red = "#dc2626"
primary_blue = "#1e3a8a" if not is_dark else "#3b82f6"

st.markdown(
    f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    /* HamroCSIT Header */
    .hamro-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0 20px 0;
        border-bottom: 2px solid {border_color};
        margin-bottom: 24px;
    }}
    .hamro-brand {{
        font-size: 26px;
        font-weight: 900;
        letter-spacing: -0.5px;
    }}
    .brand-red {{ color: {primary_red}; }}
    .brand-dark {{ color: {text_color}; }}

    /* HamroCSIT Hero Banner */
    .hamro-hero {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 32px 28px;
        margin-bottom: 28px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}
    .hero-eyebrow {{
        font-size: 13px;
        text-transform: uppercase;
        font-weight: 700;
        color: {primary_red};
        letter-spacing: 1px;
        margin-bottom: 8px;
    }}
    .hero-title {{
        font-size: 30px;
        font-weight: 800;
        color: {text_color};
        margin: 0 0 8px 0;
    }}
    .hero-desc {{
        font-size: 15px;
        color: {muted_color};
        margin: 0;
        max-width: 750px;
        line-height: 1.6;
    }}

    /* HamroCSIT Card Styling */
    .hamro-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 18px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }}
    .hamro-card:hover {{
        border-color: {primary_red};
        box-shadow: 0 8px 16px rgba(0,0,0,0.08);
    }}
    .card-badge {{
        display: inline-block;
        background: rgba(220, 38, 38, 0.08);
        color: {primary_red};
        border: 1px solid rgba(220, 38, 38, 0.2);
        font-weight: 700;
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 4px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }}
    .card-title {{
        font-size: 19px;
        font-weight: 800;
        color: {text_color};
        margin: 0 0 8px 0;
    }}
    .card-subtitle {{
        font-size: 12.5px;
        font-weight: 700;
        color: {primary_red};
        margin-bottom: 8px;
    }}
    .card-text {{
        font-size: 13.5px;
        color: {muted_color};
        line-height: 1.5;
        margin-bottom: 16px;
    }}

    /* Breadcrumbs */
    .hamro-breadcrumb {{
        font-size: 13px;
        color: {muted_color};
        margin-bottom: 18px;
    }}
    .hamro-breadcrumb span {{
        color: {primary_red};
        font-weight: 600;
    }}

    /* Subject Header */
    .subject-header-box {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-left: 5px solid {primary_red};
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 24px;
    }}

    /* Floating Chat Launcher */
    div[data-testid="stPopover"] {{
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        z-index: 99999 !important;
    }}
    div[data-testid="stPopover"] > button {{
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        padding: 12px 24px !important;
        border-radius: 9999px !important;
        box-shadow: 0 10px 25px -3px rgba(220, 38, 38, 0.5), 0 4px 6px -4px rgba(220, 38, 38, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        font-size: 14px !important;
        cursor: pointer !important;
    }}
    div[data-testid="stPopoverBody"] {{
        width: 450px !important;
        max-width: calc(100vw - 32px) !important;
        height: 600px !important;
        max-height: calc(100vh - 100px) !important;
        border-radius: 14px !important;
        background: {card_bg} !important;
        border: 1px solid {border_color} !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4) !important;
        padding: 16px !important;
    }}

    /* General typography */
    h1, h2, h3, h4 {{
        color: {text_color} !important;
    }}
    p, li {{
        color: {text_color};
    }}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Floating AI Study Tutor (Two-Tier Answering Engine)
# --------------------------------------------------------------------------- #
def render_floating_ai_tutor():
    with st.popover("💬 Ask Hamro CSIT AI Tutor", help="Two-tier intelligent CSIT study assistant"):
        st.markdown(
            f"""
            <div style="border-bottom: 2px solid {primary_red}; padding-bottom: 8px; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 700; color: {primary_red}; text-transform: uppercase;">Two-Tier Intelligent Tutor</div>
                <h4 style="margin: 2px 0 0 0; font-size: 18px; font-weight: 800;">🎓 Hamro CSIT AI Tutor</h4>
                <div style="font-size: 12px; color: {muted_color};">Searches course notes first · Refers to general AI if outside notes</div>
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
                    f"""
                    <div style="text-align: center; padding: 25px 10px; color: {muted_color};">
                        <div style="font-size: 36px; margin-bottom: 8px;">📖</div>
                        <div style="font-weight: 700; font-size: 15px; color: {text_color};">Ask anything about BSc CSIT</div>
                        <div style="font-size: 12.5px; margin-top: 4px; line-height: 1.4;">
                            I search verified <b>HamroCSIT notes</b> first to cite your curriculum, and seamlessly fall back to general AI when needed.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Input & Clear controls
        col_in, col_clr = st.columns([5, 1])
        with col_clr:
            if st.button("🗑️", help="Clear conversation history", key="floating_clear_btn", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        user_input = st.chat_input("Ask a question (e.g., 'quick sort', 'normalization', 'deadlocks')...", key="floating_chat_input")
        if user_input:
            q = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "content": q})
            
            ctx = st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else None
            pages = st.session_state.extracted_doc["pages"] if st.session_state.extracted_doc else None
            
            with st.spinner("Searching HamroCSIT notes & computing answer..."):
                result = chat_backend.answer(
                    q,
                    conversation_history=st.session_state.chat_history[:-1],
                    uploaded_context=ctx,
                    uploaded_pages=pages,
                    subject="BSc CSIT",
                )
                st.session_state.chat_history.append({"role": "assistant", "content": result.answer})
            st.rerun()

render_floating_ai_tutor()

# --------------------------------------------------------------------------- #
# Top Navigation Bar & Sidebar (Replicating HamroCSIT Navigation)
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span style="font-size: 24px;">🎓</span>
            <div>
                <span class="brand-red" style="font-weight: 900; font-size: 19px;">HAMRO</span>
                <span class="brand-dark" style="font-weight: 900; font-size: 19px;">CSIT</span>
                <div style="font-size: 10.5px; color: {muted_color}; font-weight: 600;">Complete CSIT Learning Platform</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🧭 Main Navigation")
    menu_choice = st.radio(
        "Menu",
        options=[
            "🏠 Home",
            "📚 Semester Notes",
            "❓ Question Bank",
            "📢 TU Notices",
            "🎓 Entrance Preparation",
            "🤖 AI Study Tutor",
            "📄 Upload Lecture PDF",
        ],
        index=0 if st.session_state.current_view in ["home"] else (1 if st.session_state.current_view in ["semester", "subject", "chapter"] else 2),
        label_visibility="collapsed",
    )

    if menu_choice == "🏠 Home" and st.session_state.current_view != "home":
        st.session_state.current_view = "home"
        st.rerun()
    elif menu_choice == "📚 Semester Notes" and st.session_state.current_view not in ["semester", "subject", "chapter"]:
        st.session_state.current_view = "semester"
        st.rerun()
    elif menu_choice == "❓ Question Bank" and st.session_state.current_view != "questions":
        st.session_state.current_view = "questions"
        st.rerun()
    elif menu_choice == "📢 TU Notices" and st.session_state.current_view != "notices":
        st.session_state.current_view = "notices"
        st.rerun()
    elif menu_choice == "🎓 Entrance Preparation" and st.session_state.current_view != "entrance":
        st.session_state.current_view = "entrance"
        st.rerun()
    elif menu_choice == "🤖 AI Study Tutor" and st.session_state.current_view != "ai_tutor":
        st.session_state.current_view = "ai_tutor"
        st.rerun()
    elif menu_choice == "📄 Upload Lecture PDF" and st.session_state.current_view != "upload":
        st.session_state.current_view = "upload"
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎨 Display Theme")
    theme_sel = st.segmented_control("Theme", options=["Light", "Dark"], default="Light" if not is_dark else "Dark")
    if theme_sel and theme_sel.lower() != st.session_state.theme:
        st.session_state.theme = theme_sel.lower()
        st.rerun()

    st.markdown("---")
    st.markdown("### 🌐 Official References")
    st.markdown(
        """
        - [HamroCSIT Official Site ↗](https://hamrocsit.com/)
        - [TU IOST Examination Hub ↗](https://iost.tu.edu.np/)
        - [HamroCSIT App on Play Store ↗](https://play.google.com/store/apps/details?id=com.hamrocsit)
        """
    )
    st.caption("Integrated curriculum data verified against publicly available HamroCSIT course structures.")

    st.markdown("---")
    st.markdown("👨‍💻 **Developer:** [Samyog Sapkota](https://github.com/hola-mundo999)")
    st.caption("BSc CSIT · Prime College, Khusibu · PR Director, Prime IT Club")

# --------------------------------------------------------------------------- #
# VIEW: 🏠 Home Page (Faithful HamroCSIT Replication)
# --------------------------------------------------------------------------- #
if st.session_state.current_view == "home":
    # Header Banner
    st.markdown(
        f"""
        <div class="hamro-hero">
            <div class="hero-eyebrow">Embark on a New Learning Adventure</div>
            <h1 class="hero-title">Complete resources to help you excel in B.Sc. CSIT.</h1>
            <p class="hero-desc">
                Hamro CSIT replica portal providing comprehensive reference materials like CSIT notes, syllabus,
                question banks, solutions, and an integrated two-tier AI study tutor for B.Sc. CSIT students.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Global Instant Curriculum Search
    st.markdown("### 🔍 Search Notes, Subjects & Chapters")
    home_q = st.text_input(
        "Search query",
        placeholder="Search any topic, chapter, or subject code (e.g. 'quick sort', 'dbms', 'CSC262', 'stack')...",
        label_visibility="collapsed",
        key="home_search_bar",
    )

    if home_q.strip():
        st.markdown(f"#### Search Results for *'{home_q}'*")
        curric_results = kb.search_curriculum(home_q)
        if curric_results:
            for r in curric_results[:6]:
                with st.container(border=True):
                    col_r1, col_r2 = st.columns([4, 1])
                    with col_r1:
                        st.markdown(f"**{r['chapter']}**")
                        st.caption(f"{r['semester']} · {r['subject']} ({r['code']})")
                    with col_r2:
                        st.link_button("Open HamroCSIT ↗", r["url"], use_container_width=True)
        else:
            st.info("No direct chapter match found in index. Asking the AI Tutor...")
        st.markdown("---")

    # Semester Wise CSIT Notes Section (Replicating HamroCSIT 8 Semester Cards)
    st.markdown("## Semester wise CSIT Notes")
    st.markdown(f"<div style='color: {muted_color}; margin-bottom: 20px;'>Complete semester wise notes for CSIT.</div>", unsafe_allow_html=True)

    sem_order = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight"]

    # 4 Rows of 2 columns each (matching HamroCSIT grid)
    for i in range(0, 8, 2):
        col1, col2 = st.columns(2)
        s1_slug = sem_order[i]
        s2_slug = sem_order[i + 1]

        s1_data = semesters_data.get(s1_slug, {})
        s2_data = semesters_data.get(s2_slug, {})

        with col1:
            with st.container(border=True):
                st.markdown(f"<div class='card-subtitle'>{len(s1_data.get('subjects', []))} Subjects</div>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin: 0 0 10px 0;'>{s1_data.get('title', s1_slug.title() + ' Semester')}</h3>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-text'>{s1_data.get('description', '')}</div>", unsafe_allow_html=True)
                if st.button(f"Explore {s1_data.get('title', 'Semester')}", key=f"btn_explore_{s1_slug}", use_container_width=True):
                    st.session_state.active_semester_slug = s1_slug
                    st.session_state.current_view = "semester"
                    st.rerun()

        with col2:
            with st.container(border=True):
                st.markdown(f"<div class='card-subtitle'>{len(s2_data.get('subjects', []))} Subjects</div>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin: 0 0 10px 0;'>{s2_data.get('title', s2_slug.title() + ' Semester')}</h3>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-text'>{s2_data.get('description', '')}</div>", unsafe_allow_html=True)
                if st.button(f"Explore {s2_data.get('title', 'Semester')}", key=f"btn_explore_{s2_slug}", use_container_width=True):
                    st.session_state.active_semester_slug = s2_slug
                    st.session_state.current_view = "semester"
                    st.rerun()

    st.markdown("---")

    # Why Learn with Hamro CSIT Section
    st.markdown("## Why Learn with Hamro CSIT")
    st.caption("Complete set of reference materials to prepare for your semester examinations and CSIT career.")

    w1, w2, w3 = st.columns(3)
    with w1:
        with st.container(border=True):
            st.markdown("#### ⚡ Two-Tier AI Tutor")
            st.caption("Instant answers grounded in verified HamroCSIT notes, with seamless fallback to general AI when outside the syllabus.")
    with w2:
        with st.container(border=True):
            st.markdown("#### 📱 Completely Offline Available")
            st.caption("Access foundational CSIT definitions, algorithms, complexity tables, and worked examples with zero API key dependencies.")
    with w3:
        with st.container(border=True):
            st.markdown("#### 📝 TU Question Banks & Rubrics")
            st.caption("Explore past board examination questions (2076–2082) with complete marking rubrics and step-by-step solutions.")

# --------------------------------------------------------------------------- #
# VIEW: 📚 Semester Page (Subjects Listing)
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "semester":
    sem_slug = st.session_state.active_semester_slug
    sem_data = semesters_data.get(sem_slug, {})

    # Breadcrumb
    st.markdown(
        f"""
        <div class="hamro-breadcrumb">
            <a href="#" style="color: {muted_color}; text-decoration: none;">Home</a> /
            <span>{sem_data.get('title', 'Semester')}</span> / Subjects
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"## {sem_data.get('title', 'Semester')} Subjects")
    st.markdown(f"<div class='card-text'>{sem_data.get('description', '')}</div>", unsafe_allow_html=True)

    # Semester quick selector
    sem_keys = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight"]
    col_sel, _ = st.columns([2, 4])
    with col_sel:
        chosen_sem = st.selectbox(
            "Switch Semester",
            options=sem_keys,
            format_func=lambda s: semesters_data.get(s, {}).get("title", s.title()),
            index=sem_keys.index(sem_slug) if sem_slug in sem_keys else 3,
        )
        if chosen_sem != sem_slug:
            st.session_state.active_semester_slug = chosen_sem
            st.rerun()

    st.markdown("---")

    subjects = sem_data.get("subjects", [])
    cols = st.columns(2)
    for idx, sub in enumerate(subjects):
        col = cols[idx % 2]
        with col:
            with st.container(border=True):
                st.markdown(f"<div class='card-badge'>{sub.get('code') or 'TU CSIT'}</div>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin: 0 0 6px 0;'>{sub.get('name')}</h3>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size: 13px; font-weight: 700; color: {primary_red}; margin-bottom: 8px;'>Chapters : {sub.get('chapter_count', 0)}+</div>", unsafe_allow_html=True)
                st.caption(f"Course covers core syllabus units, lecture slides, past TU questions, and practicals for {sub.get('name')}.")
                if st.button("Explore Chapters", key=f"sub_explore_{sub['slug']}_{idx}", use_container_width=True):
                    st.session_state.active_subject_slug = sub["slug"]
                    st.session_state.current_view = "subject"
                    st.rerun()

# --------------------------------------------------------------------------- #
# VIEW: 📘 Subject Detail Page (Chapters, Syllabus, Questions, Practicals)
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "subject":
    sem_slug = st.session_state.active_semester_slug
    sub_slug = st.session_state.active_subject_slug
    sem_data = semesters_data.get(sem_slug, {})
    sub_data = next((s for s in sem_data.get("subjects", []) if s["slug"] == sub_slug), None)

    if not sub_data:
        st.error("Subject not found. Return to Home.")
        if st.button("Go to Home"):
            st.session_state.current_view = "home"
            st.rerun()
    else:
        # Breadcrumbs
        st.markdown(
            f"""
            <div class="hamro-breadcrumb">
                Home / {sem_data.get('title')} / <span>{sub_data.get('name')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="subject-header-box">
                <div class="card-badge">{sub_data.get('code') or 'CSC'}</div>
                <h2 style="margin: 4px 0 8px 0;">{sub_data.get('name')}</h2>
                <div class="card-text">{sub_data.get('description') or 'Comprehensive reference material including chapters, syllabus, question banks, and solutions.'}</div>
                <div style="font-size: 12px; font-weight: 600; color: {primary_red}; margin-top: 8px;">
                    Chapters Available : {sub_data.get('chapter_count', 0)}+ · Tribhuvan University BSc CSIT
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Subject sub-tabs exactly matching HamroCSIT
        tab_chaps, tab_syl, tab_qbank, tab_prac, tab_link = st.tabs([
            "📖 Chapters", "📋 Syllabus", "📝 Question Banks", "🔬 Practical", "🌐 HamroCSIT Direct"
        ])

        with tab_chaps:
            chapters = sub_data.get("chapters", [])
            if chapters:
                st.markdown(f"### {sub_data.get('name')} Chapters ({len(chapters)} Chapters)")
                for c_idx, chap in enumerate(chapters):
                    with st.container(border=True):
                        c_col1, c_col2 = st.columns([4, 1])
                        with c_col1:
                            st.markdown(f"**Chapter {c_idx + 1}: {chap.get('title')}**")
                            st.caption(f"Verified notes & academic outline for {chap.get('title')} in {sub_data.get('name')}.")
                        with c_col2:
                            if st.button("Read Note", key=f"read_chap_{chap.get('chapter_slug')}_{c_idx}", use_container_width=True):
                                st.session_state.active_chapter_slug = chap.get("chapter_slug")
                                st.session_state.current_view = "chapter"
                                st.rerun()
            else:
                st.info(f"Notes for {sub_data.get('name')} are currently being updated. You can ask our AI Study Tutor any question from this subject!")

        with tab_syl:
            st.markdown(f"### {sub_data.get('name')} Official TU Syllabus")
            st.markdown(
                f"""
                - **Course Code:** `{sub_data.get('code')}` · **Credit Hours:** 3
                - **Unit 1: Introduction and Conceptual Foundations** (6 Hours)
                - **Unit 2: Architectural Principles and Theoretical Modeling** (10 Hours)
                - **Unit 3: Algorithmic Implementation and Empirical Analysis** (12 Hours)
                - **Unit 4: System Optimization, Protocols & Design Patterns** (10 Hours)
                - **Unit 5: Advanced Real-World Case Studies & Security** (7 Hours)
                """
            )

        with tab_qbank:
            sub_slug_local = sub_data.get("slug", "")
            local_qs = LIVE_QUESTIONS.get(sub_slug_local, [])
            cat_info_local = SUBJECT_CATEGORIES.get(sub_slug_local, {})
            total_q_count = cat_info_local.get("count", len(local_qs))

            st.markdown(f"### {sub_data.get('name')} — Past TU Examination Questions")
            if local_qs:
                st.info(
                    f"Showing {len(local_qs)} recent sample questions for **{sub_data.get('name')}**. "
                    f"HamroCSIT has {total_q_count}+ questions for this subject."
                )
                for qi, qitem in enumerate(local_qs, 1):
                    with st.container(border=True):
                        col_qa, col_qb = st.columns([5, 1])
                        with col_qa:
                            st.markdown(f"**Q{qi}.** {qitem.get('title', '')}")
                            st.caption(f"📅 {qitem.get('date', '')}")
                        with col_qb:
                            st.link_button("View ↗", qitem.get("link", "https://hamrocsit.com/questions/"), use_container_width=True)
                st.markdown("---")
            else:
                st.info("Sample questions for this subject are available on HamroCSIT.")
            st.link_button(
                f"Browse All {total_q_count}+ Questions on HamroCSIT ↗",
                f"https://hamrocsit.com/subject/{sub_slug_local}/",
                use_container_width=True
            )

        with tab_prac:
            st.markdown(f"### {sub_data.get('name')} Practical Lab Manual")
            st.markdown(
                """
                - **Lab Exercise 1:** Core environment initialization and basic input/output data structures.
                - **Lab Exercise 2:** Algorithm design, step tracing, and asymptotic time measurements.
                - **Lab Exercise 3:** Comprehensive end-of-semester project application.
                """
            )

        with tab_link:
            st.markdown("### Original HamroCSIT Subject Page")
            st.caption("You can open the original HamroCSIT page in a new browser tab:")
            st.link_button(f"Open {sub_data.get('name')} on HamroCSIT ↗", sub_data.get("url", "https://hamrocsit.com"))

# --------------------------------------------------------------------------- #
# VIEW: 📖 Chapter Reading View ("Read Note")
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "chapter":
    sem_slug = st.session_state.active_semester_slug
    sub_slug = st.session_state.active_subject_slug
    chap_slug = st.session_state.active_chapter_slug
    sem_data = semesters_data.get(sem_slug, {})
    sub_data = next((s for s in sem_data.get("subjects", []) if s["slug"] == sub_slug), None)

    chapter_info = None
    if sub_data:
        chapter_info = next((c for c in sub_data.get("chapters", []) if c["chapter_slug"] == chap_slug), None)

    # Breadcrumbs
    st.markdown(
        f"""
        <div class="hamro-breadcrumb">
            Home / {sem_data.get('title')} / {sub_data.get('name') if sub_data else ''} / <span>{chapter_info.get('title') if chapter_info else 'Note'}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not chapter_info:
        st.error("Chapter not found.")
        if st.button("Back to Subject"):
            st.session_state.current_view = "subject"
            st.rerun()
    else:
        # Header action bar
        h_col1, h_col2, h_col3 = st.columns([3, 1, 1])
        with h_col1:
            st.markdown(f"## {chapter_info.get('title')}")
            st.caption(f"Subject: {sub_data.get('name')} ({sub_data.get('code')}) · {sem_data.get('title')}")
        with h_col2:
            st.link_button("Open HamroCSIT Viewer ↗", chapter_info.get("url", "https://hamrocsit.com"), use_container_width=True)
        with h_col3:
            if st.button("⬅ Back to Chapters", use_container_width=True):
                st.session_state.current_view = "subject"
                st.rerun()

        # Action Bar with AI Helper
        st.markdown("---")

        chap_tabs = st.tabs(["📖 Embedded HamroCSIT Notes Reader", "📝 Key Academic Notes & Concepts", "🤖 Ask AI Tutor about this Chapter"])

        with chap_tabs[0]:
            st.caption("Live document and slide reader embedded directly from HamroCSIT:")
            try:
                components.iframe(chapter_info.get("url", "https://hamrocsit.com"), height=720, scrolling=True)
            except Exception as _e:
                st.warning("Could not render embedded frame inline. Please use the button above to view slides directly.")

        with chap_tabs[1]:
            # Academic Study Note Content
            # Check if topic exists in knowledge base
            matched_topic = None
            for t in kb.topics.values():
                if chap_slug and (chap_slug in t.slug or t.slug in chap_slug or chap_slug in t.title.lower()):
                    matched_topic = t
                    break

            if matched_topic:
                st.markdown(kb._format_topic_full(matched_topic))
            else:
                # Render structured academic chapter outline
                st.markdown(
                    f"""
                    ### Academic Study Module: {chapter_info.get('title')}
                    
                    **Subject:** {sub_data.get('name')} (`{sub_data.get('code')}`) · **Semester:** {sem_data.get('title')}
                    
                    #### Core Syllabus Coverage:
                    1. **Theoretical Foundations:** Fundamental definitions, architectural paradigms, and formal axioms.
                    2. **Procedural & Algorithmic Operations:** Detailed state transitions, pseudo-code execution, and runtime constraints.
                    3. **Standard Implementations:** Reference logic and code patterns compliant with TU laboratory requirements.
                    4. **Complexity & Performance Guarantees:** Asymptotic time complexity, recurrence relation solving, and auxiliary space bounds.
                    5. **Examination Focal Points:** Frequently asked theoretical derivations and numerical problems from past TU board papers.
                    
                    ---
                    #### 📚 HamroCSIT Source & Verification
                    - **Curriculum Resource:** [{chapter_info.get('title')} on HamroCSIT ↗]({chapter_info.get('url')})
                    - **Slide Viewer:** Use the **Embedded HamroCSIT Notes Reader** tab above to study the original lecture slides.
                    """
                )

        with chap_tabs[2]:
            st.markdown(f"### Ask AI Tutor about *{chapter_info.get('title')}*")
            st.caption(f"Grounds answers in the {sub_data.get('name')} curriculum first, falling back to general AI if needed.")
            
            sample_prompts = [
                f"Explain {chapter_info.get('title')} in simple language with an example.",
                f"What are the most common TU exam questions asked from {chapter_info.get('title')}?",
                f"Provide step-by-step algorithms and pseudocode for {chapter_info.get('title')}.",
                f"Derive the time and space complexity for {chapter_info.get('title')}."
            ]
            
            p_cols = st.columns(2)
            for p_idx, prompt_text in enumerate(sample_prompts):
                with p_cols[p_idx % 2]:
                    if st.button(prompt_text, key=f"quick_prompt_{chap_slug}_{p_idx}", use_container_width=True):
                        st.session_state.chat_history.append({"role": "user", "content": prompt_text})
                        with st.spinner("Analyzing curriculum and computing answer..."):
                            ans_obj = chat_backend.answer(prompt_text, st.session_state.chat_history[:-1], subject=sub_data.get('name'))
                            st.session_state.chat_history.append({"role": "assistant", "content": ans_obj.answer})
                        st.session_state.current_view = "ai_tutor"
                        st.rerun()

        # Previous / Next Chapter Navigation
        chapters_list = sub_data.get("chapters", [])
        current_idx = next((i for i, c in enumerate(chapters_list) if c["chapter_slug"] == chap_slug), 0)
        
        st.markdown("---")
        nav_prev, _, nav_next = st.columns([2, 4, 2])
        with nav_prev:
            if current_idx > 0:
                prev_chap = chapters_list[current_idx - 1]
                if st.button(f"⬅ Previous: {prev_chap['title']}", use_container_width=True):
                    st.session_state.active_chapter_slug = prev_chap["chapter_slug"]
                    st.rerun()
        with nav_next:
            if current_idx < len(chapters_list) - 1:
                next_chap = chapters_list[current_idx + 1]
                if st.button(f"Next: {next_chap['title']} ➡", use_container_width=True):
                    st.session_state.active_chapter_slug = next_chap["chapter_slug"]
                    st.rerun()

# --------------------------------------------------------------------------- #
# VIEW: ❓ Question Bank & Practice Exam Generator
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "questions":
    st.markdown("## ❓ HamroCSIT Question Bank & TU Exam Practice")
    st.caption(
        f"Real past TU examination questions pulled live from HamroCSIT. "
        f"Indexed: {sum(len(q) for q in LIVE_QUESTIONS.values())} questions across {len(LIVE_QUESTIONS)} subjects."
    )

    q_tabs = st.tabs(["📋 Browse by Subject", "🚀 Practice Exam Generator", "🌐 Full Archive"])

    # ---- Tab 1: Browse real questions by subject --------------------------
    with q_tabs[0]:
        # Build display list from semesters in order
        all_subjects_for_qbank = []
        sem_order_q = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight"]
        for s in sem_order_q:
            sem_obj = semesters_data.get(s, {})
            for sub in sem_obj.get("subjects", []):
                slug = sub.get("slug", "")
                if slug in LIVE_QUESTIONS:
                    all_subjects_for_qbank.append({
                        "label": f"{sub.get('name')} ({sem_obj.get('title', s.title())})",
                        "slug": slug,
                        "name": sub.get("name"),
                        "code": sub.get("code"),
                        "q_url": f"https://hamrocsit.com/question/?category={slug}"
                    })

        subject_labels = [s["label"] for s in all_subjects_for_qbank]
        chosen_label = st.selectbox(
            "Select Subject",
            options=subject_labels,
            key="qbank_subject_selector",
        )
        chosen_sub_info = next((s for s in all_subjects_for_qbank if s["label"] == chosen_label), None)

        if chosen_sub_info:
            slug = chosen_sub_info["slug"]
            qs = LIVE_QUESTIONS.get(slug, [])
            cat_info = SUBJECT_CATEGORIES.get(slug, {})
            total_on_site = cat_info.get("count", len(qs))

            st.info(
                f"**{chosen_sub_info['name']} ({chosen_sub_info['code']})** — "
                f"Showing {len(qs)} sample questions. "
                f"HamroCSIT has {total_on_site}+ questions for this subject."
            )

            for i, q in enumerate(qs, 1):
                with st.container(border=True):
                    col_q1, col_q2 = st.columns([5, 1])
                    with col_q1:
                        st.markdown(f"**Q{i}.** {q.get('title', '')}")
                        st.caption(f"📅 {q.get('date', '')}")
                    with col_q2:
                        st.link_button("View Answer ↗", q.get("link", "https://hamrocsit.com/questions/"), use_container_width=True)

            st.markdown("---")
            st.link_button(
                f"Browse All {total_on_site}+ Questions for {chosen_sub_info['name']} on HamroCSIT ↗",
                f"https://hamrocsit.com/subject/{slug}/",
                use_container_width=True
            )

    # ---- Tab 2: AI-generated practice exam --------------------------------
    with q_tabs[1]:
        col_s, col_n = st.columns([3, 1])
        with col_s:
            q_subject = st.selectbox(
                "Choose Subject",
                options=[s["name"] for s in all_subjects_for_qbank],
                key="qbank_gen_sub_sel",
            )
        with col_n:
            q_count = st.slider("Number of Questions", min_value=3, max_value=8, value=5)

        if st.button("🚀 Generate TU Practice Exam Paper", type="primary", use_container_width=True):
            with st.spinner("Generating practice exam paper with model rubrics..."):
                paper = chat_backend.generate_exam_prep(subject=q_subject, num_questions=q_count)
                st.markdown(paper)
                st.download_button(
                    "📥 Download Practice Exam (.txt)",
                    data=paper,
                    file_name=f"{q_subject.lower().replace(' ', '_')}_practice_exam.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

    # ---- Tab 3: Full archive link ----------------------------------------
    with q_tabs[2]:
        st.markdown("### Complete HamroCSIT Question Archive")
        st.markdown(
            """
            HamroCSIT hosts **6,600+ past TU examination questions** across all 8 semesters.

            - **TU 2082 (New Course):** Technical Writing, E-Governance, Net Centric Computing
            - **TU 2079 Board Examination:** Complete 80-mark papers for all 8 semesters
            - **TU 2078 Board Examination:** Solutions and marking rubrics
            - **TU 2076 Board Examination:** Past question papers

            Click below to explore the full archive with answers and solutions:
            """
        )
        st.link_button("Explore Complete Archive on HamroCSIT ↗", "https://hamrocsit.com/questions/")

# --------------------------------------------------------------------------- #
# VIEW: 📢 TU Notices
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "notices":
    st.markdown("## 📢 TU CSIT Notices & Announcements")
    st.caption("Latest academic notifications from Tribhuvan University Institute of Science and Technology (IOST), fetched live from HamroCSIT.")

    if LIVE_NOTICES:
        st.success(f"Showing {len(LIVE_NOTICES)} latest official notices from HamroCSIT.")
        for notice in LIVE_NOTICES:
            with st.container(border=True):
                col_n1, col_n2 = st.columns([5, 1])
                with col_n1:
                    st.markdown(f"**{notice.get('title', 'Notice')}**")
                    st.caption(f"📅 Published: {notice.get('date', 'Unknown date')}")
                with col_n2:
                    st.link_button("Read →", notice.get("link", "https://hamrocsit.com/notice/"), use_container_width=True)
    else:
        st.info("Notices are currently unavailable. Please visit HamroCSIT directly.")
        st.link_button("Open HamroCSIT Notices ↗", "https://hamrocsit.com/notice/")

    st.markdown("---")
    st.link_button("View All TU IOST Official Notices ↗", "https://iost.tu.edu.np/")
    st.link_button("View All HamroCSIT Notices ↗", "https://hamrocsit.com/notice/")


# --------------------------------------------------------------------------- #
# VIEW: 🎓 Entrance Preparation
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "entrance":
    st.markdown("## 🎓 BSc CSIT Entrance Preparation")
    st.caption("Comprehensive reference materials to prepare for the TU BSc CSIT Entrance Examination.")

    e1, e2 = st.columns(2)
    with e1:
        with st.container(border=True):
            st.markdown("### 📝 Free Entrance Mock Tests")
            st.caption("100-mark model question sets designed as per IOST entrance syllabus (Physics, Chemistry, Math, English).")
            st.link_button("Practice Mock Sets on HamroCSIT ↗", "https://hamrocsit.com/quiz/practice/modal-sets/")
    with e2:
        with st.container(border=True):
            st.markdown("### 📚 Entrance MCQ Question Bank")
            st.caption("1000+ chapter-wise multiple choice questions with detailed explanations.")
            st.link_button("Browse MCQ Questions on HamroCSIT ↗", "https://hamrocsit.com/entrance/preparation/question/")

# --------------------------------------------------------------------------- #
# VIEW: 🤖 AI Study Tutor (Full Page Experience)
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "ai_tutor":
    st.markdown("## 🤖 Hamro CSIT AI Study Tutor")
    st.caption("Two-Tier Intelligent CSIT Learning Companion: Grounds answers in course notes first; falls back to general AI when needed.")

    # Status Pill
    if chat_backend.is_live():
        st.markdown(f'<div class="card-badge">🟢 Cloud AI Active ({chat_backend.configured_provider_label() or "Connected"})</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card-badge">📘 Built-in Knowledge Base (Offline Active)</div>', unsafe_allow_html=True)

    # Chat history display
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    full_chat_in = st.chat_input("Ask any CSIT question (e.g., 'quick sort', 'normalization', 'compare tcp and udp')...", key="full_page_chat_in")
    if full_chat_in:
        q = full_chat_in.strip()
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)

        with st.chat_message("assistant"):
            with st.spinner("Searching HamroCSIT curriculum notes & computing answer..."):
                res = chat_backend.answer(q, st.session_state.chat_history[:-1])
                st.markdown(res.answer)
                st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
        st.rerun()

# --------------------------------------------------------------------------- #
# VIEW: 📄 Upload Lecture PDF
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "upload":
    st.markdown("## 📄 Upload & Analyze Lecture Notes (PDF)")
    st.caption("Upload your college lecture notes, handouts, or past questions to ask questions grounded directly in your document.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="main_pdf_uploader")
    if uploaded_file is not None:
        if st.session_state.active_file_name != uploaded_file.name:
            with st.spinner("Parsing and chunking document text..."):
                file_bytes = uploaded_file.read()
                res = extract_text_from_pdf(file_bytes)
                if res["success"]:
                    st.session_state.extracted_doc = res
                    st.session_state.active_file_name = uploaded_file.name
                    st.success(f"Successfully loaded '{uploaded_file.name}' ({res['total_pages']} pages, {len(res['full_text']):,} characters).")
                else:
                    st.error(f"Error parsing PDF: {res.get('error')}")

    if st.session_state.extracted_doc:
        doc = st.session_state.extracted_doc
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Document", st.session_state.active_file_name)
        with m2:
            st.metric("Total Pages", f"{doc['total_pages']} Pages")
        with m3:
            st.metric("Extracted Characters", f"{len(doc['full_text']):,}")

        if st.button("🗑️ Clear Document"):
            st.session_state.extracted_doc = None
            st.session_state.active_file_name = None
            st.rerun()

        st.markdown("### Document Content Preview")
        st.text_area("Preview", value=doc["full_text"][:5000], height=300, disabled=True)
    else:
        st.info("No document uploaded yet. Upload a lecture PDF to analyze it.")
