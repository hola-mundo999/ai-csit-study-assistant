"""HAMRO CSIT — Complete BSc CSIT Notes, Question Bank & Intelligent AI Tutor.

Faithful pixel-accurate recreation of HamroCSIT (https://hamrocsit.com/) with:
  - Exact white top navigation bar with HamroCSIT logo and direct navigation pills
  - Exact hero banner: "Best learning platform to Prepare for CSIT Semester Exams"
  - Exact 8-semester colorful category cards (.category-color-1 to .category-color-8)
  - Subject cards with clean white background, soft shadow, and chapter counts
  - Chapter reader with clean embedded PDF slides and interactive study tools
  - Floating HamroCSIT AI Study Tutor in bottom-right with two-tier grounding
  - Real TU past board questions & official notices from HamroCSIT API
"""

import os
import json
import base64
import urllib.request
from bs4 import BeautifulSoup
import streamlit as st
import streamlit.components.v1 as components
from ai_backend import chat_backend
from knowledge_base import kb
from pdf_processor import extract_text_from_pdf

# --------------------------------------------------------------------------- #
# Page Configuration (Collapsed sidebar, wide layout, light portal style)
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Hamro CSIT — Complete CSIT Notes, Questions Bank & AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
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

# Load HamroCSIT Logo and Illustration
try:
    with open(os.path.join(_BASE, "hamrocsit_logo_b64.txt"), "r", encoding="utf-8") as _f:
        HAMRO_LOGO_DATA_URI = _f.read().strip()
except Exception:
    HAMRO_LOGO_DATA_URI = "https://hamrocsit.com/wp-content/themes/tucsitnotes/assets/images/new/logo.svg"

try:
    with open(os.path.join(_BASE, "prof_svg_b64.txt"), "r", encoding="utf-8") as _f:
        HERO_PROF_SVG_URI = _f.read().strip()
except Exception:
    HERO_PROF_SVG_URI = "https://hamrocsit.com/wp-content/themes/tucsitnotes/assets/images/prof.svg"

# --------------------------------------------------------------------------- #
# Session State Initialization
# --------------------------------------------------------------------------- #
if "current_view" not in st.session_state:
    st.session_state.current_view = "home"  # 'home', 'semester', 'subject', 'chapter', 'questions', 'notices', 'entrance', 'ai_tutor', 'upload'
if "active_semester_slug" not in st.session_state:
    st.session_state.active_semester_slug = "fourth"
if "active_subject_slug" not in st.session_state:
    st.session_state.active_subject_slug = "dbms"
if "active_chapter_slug" not in st.session_state:
    st.session_state.active_chapter_slug = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "extracted_doc" not in st.session_state:
    st.session_state.extracted_doc = None
if "active_file_name" not in st.session_state:
    st.session_state.active_file_name = None

# Helper to fetch PDF viewer iframe from HamroCSIT note page
@st.cache_data(show_spinner=False, ttl=86400)
def get_hamrocsit_viewer_url(note_page_url: str) -> str:
    if not note_page_url:
        return ""
    try:
        req = urllib.request.Request(note_page_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, timeout=6).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        iframe = soup.find('iframe')
        if iframe and iframe.get('src'):
            src = iframe['src']
            if src.startswith('/'):
                src = 'https://hamrocsit.com' + src
            return src
    except Exception:
        pass
    return note_page_url

# --------------------------------------------------------------------------- #
# HamroCSIT Authentic Styling (Clean White + Emerald/Teal #00af92)
# --------------------------------------------------------------------------- #
st.markdown(
    f"""
    <style>
        /* Base page styling */
        .stApp {{
            background-color: #fbfcfe;
            color: #202029;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}

        /* Hide Streamlit default chrome & deploy header */
        header[data-testid="stHeader"] {{
            background: transparent !important;
            height: 2.5rem !important;
        }}
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 5rem !important;
            max-width: 1200px !important;
        }}

        /* Clean Top Navigation Bar */
        .hamro-navbar {{
            background: #ffffff;
            border-bottom: 1px solid #edeef3;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        }}
        .hamro-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
        }}
        .hamro-logo-text {{
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #202029;
            line-height: 1;
        }}
        .hamro-logo-text .hamro-sub {{
            font-weight: 300;
            color: #00af92;
        }}

        /* Hero Section */
        .hamro-hero-wrap {{
            background: #ffffff;
            border-radius: 10px;
            padding: 40px 36px;
            margin-bottom: 30px;
            border: 1px solid #f0f2f5;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        }}
        .hero-sub-title {{
            color: #00af92;
            font-size: 15px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }}
        .hero-title {{
            color: #202029;
            font-size: 38px;
            font-weight: 800;
            line-height: 1.25;
            margin: 0 0 16px 0;
            letter-spacing: -0.5px;
        }}
        .hero-title span {{
            color: #00af92;
        }}
        .hero-desc {{
            color: #64748b;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 24px;
            max-width: 600px;
        }}

        /* 8-Semester Category Item Cards */
        .category-item {{
            display: flex;
            align-items: center;
            padding: 18px 16px;
            border-radius: 8px;
            margin-bottom: 18px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
            transition: all 0.25s ease-in-out;
            border: 1px solid rgba(0,0,0,0.04);
            background-color: #ffffff;
            min-height: 84px;
        }}
        .category-item:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.09);
        }}
        .category-item-icon {{
            height: 48px;
            width: 48px;
            line-height: 48px;
            text-align: center;
            margin-right: 14px;
            font-size: 24px;
            background-color: #ffffff;
            border-radius: 8px;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .category-item-content h6 {{
            font-size: 16px;
            font-weight: 700;
            color: #202029;
            margin: 0 0 3px 0;
        }}
        .category-item-content span {{
            font-size: 12px;
            font-weight: 600;
            color: #64748b;
        }}

        /* Exact HamroCSIT category background colors */
        .category-color-3 {{ background-color: #f3e3d3 !important; }}
        .category-color-5 {{ background-color: #f3d6d6 !important; }}
        .category-color-8 {{ background-color: #f5e5b0 !important; }}
        .category-color-4 {{ background-color: #cce7fd !important; }}
        .category-color-2 {{ background-color: #d3d3f3 !important; }}
        .category-color-7 {{ background-color: #cfdbf3 !important; }}
        .category-color-6 {{ background-color: #d1f3ed !important; }}
        .category-color-1 {{ background-color: #cff0d2 !important; }}

        /* HamroCSIT Subject Cards (card_main) */
        .card_main {{
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #edeef3;
            box-shadow: 0 2px 6px 0 rgba(218, 218, 253, 0.65), 0 2px 6px 0 rgba(206, 206, 238, 0.54);
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .card_main:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 18px rgba(0, 175, 146, 0.15);
            border-color: #00af92;
        }}
        .card_main h5 {{
            font-size: 19px;
            font-weight: 700;
            color: #0a253f;
            margin: 0 0 8px 0;
        }}
        .card_main p {{
            font-size: 13.5px;
            color: #64748b;
            line-height: 1.5;
            margin: 0 0 14px 0;
        }}

        /* Breadcrumb banner */
        .site-breadcrumb {{
            background-color: #edeef3;
            border-radius: 8px;
            padding: 24px 20px;
            margin-bottom: 24px;
        }}
        .breadcrumb-title {{
            font-size: 28px;
            color: #202029;
            font-weight: 800;
            margin: 0 0 6px 0;
        }}
        .breadcrumb-sub {{
            font-size: 13.5px;
            color: #64748b;
        }}

        /* Floating AI Tutor launcher (Emerald/Teal brand color) */
        div[data-testid="stPopover"] {{
            position: fixed !important;
            bottom: 24px !important;
            right: 24px !important;
            z-index: 99999 !important;
        }}
        div[data-testid="stPopover"] > button {{
            background: linear-gradient(135deg, #00af92 0%, #008770 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            padding: 12px 22px !important;
            border-radius: 9999px !important;
            box-shadow: 0 10px 25px -3px rgba(0, 175, 146, 0.5), 0 4px 6px -4px rgba(0, 175, 146, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            font-size: 14.5px !important;
            cursor: pointer !important;
        }}
        div[data-testid="stPopoverBody"] {{
            width: 440px !important;
            max-width: calc(100vw - 32px) !important;
            height: 580px !important;
            border-radius: 12px !important;
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.3) !important;
            padding: 16px !important;
        }}

        /* Buttons matching HamroCSIT primary teal */
        button[kind="primary"] {{
            background-color: #00af92 !important;
            border-color: #00af92 !important;
            color: #ffffff !important;
        }}
        button[kind="secondary"] {{
            border-color: #e2e8f0 !important;
            color: #202029 !important;
        }}
        button[kind="secondary"]:hover {{
            border-color: #00af92 !important;
            color: #00af92 !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Floating HamroCSIT AI Study Tutor (Two-Tier Answering Engine)
# --------------------------------------------------------------------------- #
def render_floating_ai_tutor():
    with st.popover("💬 Ask Hamro CSIT AI Tutor", help="Two-tier intelligent CSIT study assistant"):
        st.markdown(
            """
            <div style="border-bottom: 2px solid #00af92; padding-bottom: 8px; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #00af92; text-transform: uppercase;">Two-Tier Intelligent Tutor</div>
                <h4 style="margin: 2px 0 0 0; font-size: 18px; font-weight: 800; color: #202029;">🎓 Hamro CSIT AI Tutor</h4>
                <div style="font-size: 12px; color: #64748b;">Searches HamroCSIT notes first · Refers to general AI if outside notes</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick action chips
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("⚡ Quick Sort", key="flt_btn_qs", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "quick sort"})
                ans = chat_backend.answer("quick sort", st.session_state.chat_history[:-1])
                st.session_state.chat_history.append({"role": "assistant", "content": ans.answer})
                st.rerun()
        with col_c2:
            if st.button("⚖️ Quick vs Merge", key="flt_btn_qvm", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Compare quick sort and merge sort."})
                ans = chat_backend.answer("Compare quick sort and merge sort.", st.session_state.chat_history[:-1])
                st.session_state.chat_history.append({"role": "assistant", "content": ans.answer})
                st.rerun()

        # Conversation container
        chat_box = st.container(height=340)
        with chat_box:
            if not st.session_state.chat_history:
                st.markdown(
                    """
                    <div style="text-align: center; padding: 25px 10px; color: #64748b;">
                        <div style="font-size: 36px; margin-bottom: 8px;">📖</div>
                        <div style="font-weight: 700; font-size: 15px; color: #202029;">Ask anything about BSc CSIT</div>
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
            if st.button("🗑️", help="Clear conversation history", key="flt_clear_btn", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        user_input = st.chat_input("Ask a question (e.g., 'quick sort', 'normalization', 'deadlocks')...", key="flt_chat_input")
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
# Top Navigation Header (Exact HamroCSIT Logo & Navigation Pills)
# --------------------------------------------------------------------------- #
nav_cols = st.columns([3, 1, 1, 1, 1, 1, 1.2])

with nav_cols[0]:
    st.markdown(
        f"""
        <div class="hamro-brand">
            <img src="{HAMRO_LOGO_DATA_URI}" width="38" height="38" alt="HamroCSIT Logo" />
            <div class="hamro-logo-text">
                HAMRO<span class="hamro-sub">CSIT</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_cols[1]:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = "home"
        st.rerun()

with nav_cols[2]:
    if st.button("📚 Notes", use_container_width=True):
        st.session_state.current_view = "semester"
        st.rerun()

with nav_cols[3]:
    if st.button("❓ Questions", use_container_width=True):
        st.session_state.current_view = "questions"
        st.rerun()

with nav_cols[4]:
    if st.button("📢 Notices", use_container_width=True):
        st.session_state.current_view = "notices"
        st.rerun()

with nav_cols[5]:
    if st.button("🎓 Entrance", use_container_width=True):
        st.session_state.current_view = "entrance"
        st.rerun()

with nav_cols[6]:
    if st.button("🤖 AI Tutor", type="primary", use_container_width=True):
        st.session_state.current_view = "ai_tutor"
        st.rerun()

st.markdown("<hr style='margin: 8px 0 24px 0; border: none; border-bottom: 1px solid #edeef3;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# VIEW: 🏠 Home Page (Exact HamroCSIT Design)
# --------------------------------------------------------------------------- #
if st.session_state.current_view == "home":
    # Hero Section
    h_col1, h_col2 = st.columns([1.3, 0.9])
    with h_col1:
        st.markdown(
            f"""
            <div class="hero-sub-title">Embark on a New Learning Adventure</div>
            <h1 class="hero-title">Best learning <span>platform to Prepare</span> for CSIT Semester Exams</h1>
            <p class="hero-desc">
                Complete resources to help you excel in B.Sc. CSIT — verified chapter notes, past exam papers,
                syllabus, practicals, and an intelligent AI assistant.
            </p>
            """,
            unsafe_allow_html=True,
        )

        # HamroCSIT Search bar
        home_q = st.text_input(
            "Search",
            placeholder="Search Question, Topic, or Subject (e.g. 'quick sort', 'dsa', 'dbms')...",
            label_visibility="collapsed",
            key="home_search_input",
        )
        if home_q.strip():
            curric_results = kb.search_curriculum(home_q)
            if curric_results:
                st.markdown(f"**Found {len(curric_results)} matching modules for '{home_q}':**")
                for r in curric_results[:4]:
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**{r['chapter']}**")
                            st.caption(f"{r['semester']} · {r['subject']} ({r['code']})")
                        with c2:
                            st.link_button("Open ↗", r["url"], use_container_width=True)
            else:
                st.info(f"No direct curriculum match found for '{home_q}'. Click '🤖 AI Tutor' in the top bar to ask the AI.")

    with h_col2:
        st.markdown(
            f"""
            <div style="text-align: center; padding-top: 10px;">
                <img src="{HERO_PROF_SVG_URI}" style="max-width: 100%; height: auto; max-height: 320px;" alt="HamroCSIT Student Learning" />
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin: 32px 0 28px 0; border: none; border-bottom: 1px solid #edeef3;'>", unsafe_allow_html=True)

    # ----------------------------------------------------------------------- #
    # Semester wise CSIT Notes (Exact 8 Category Cards with Real HamroCSIT Colors)
    # ----------------------------------------------------------------------- #
    st.markdown("<h2 style='font-size: 26px; font-weight: 800; margin-bottom: 4px; color: #202029;'>Semester wise CSIT Notes</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14.5px; margin-bottom: 22px;'>Complete semester wise notes for CSIT.</p>", unsafe_allow_html=True)

    sem_cards = [
        {"slug": "first", "title": "First Semester", "subs": "5 Subjects", "icon": "🧭", "color_cls": "category-color-3"},
        {"slug": "second", "title": "Second Semester", "subs": "5 Subjects", "icon": "☁️", "color_cls": "category-color-5"},
        {"slug": "third", "title": "Third Semester", "subs": "5 Subjects", "icon": "📦", "color_cls": "category-color-8"},
        {"slug": "fourth", "title": "Fourth Semester", "subs": "5 Subjects", "icon": "⚙️", "color_cls": "category-color-4"},
        {"slug": "fifth", "title": "Fifth Semester", "subs": "6 Subjects", "icon": "🛠️", "color_cls": "category-color-2"},
        {"slug": "sixth", "title": "Sixth Semester", "subs": "6 Subjects", "icon": "💻", "color_cls": "category-color-7"},
        {"slug": "seventh", "title": "Seventh Semester", "subs": "5 Subjects", "icon": "📱", "color_cls": "category-color-6"},
        {"slug": "eight", "title": "Eight Semester", "subs": "4 Subjects", "icon": "📖", "color_cls": "category-color-1"},
    ]

    # Row 1 (1st to 4th Sem)
    row1 = st.columns(4)
    for idx in range(4):
        item = sem_cards[idx]
        with row1[idx]:
            st.markdown(
                f"""
                <div class="category-item {item['color_cls']}">
                    <div class="category-item-icon">{item['icon']}</div>
                    <div class="category-item-content">
                        <h6>{item['title']}</h6>
                        <span>{item['subs']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Open {item['title']}", key=f"btn_sem_card_{item['slug']}", use_container_width=True):
                st.session_state.active_semester_slug = item["slug"]
                st.session_state.current_view = "semester"
                st.rerun()

    # Row 2 (5th to 8th Sem)
    row2 = st.columns(4)
    for idx in range(4, 8):
        item = sem_cards[idx]
        with row2[idx - 4]:
            st.markdown(
                f"""
                <div class="category-item {item['color_cls']}">
                    <div class="category-item-icon">{item['icon']}</div>
                    <div class="category-item-content">
                        <h6>{item['title']}</h6>
                        <span>{item['subs']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Open {item['title']}", key=f"btn_sem_card_{item['slug']}", use_container_width=True):
                st.session_state.active_semester_slug = item["slug"]
                st.session_state.current_view = "semester"
                st.rerun()

    st.markdown("<hr style='margin: 36px 0 28px 0; border: none; border-bottom: 1px solid #edeef3;'>", unsafe_allow_html=True)

    # Why Learn with Hamro CSIT Section
    st.markdown("<h2 style='font-size: 24px; font-weight: 800; margin-bottom: 18px; color: #202029;'>Why Learn with Hamro CSIT</h2>", unsafe_allow_html=True)
    w1, w2, w3 = st.columns(3)
    with w1:
        with st.container(border=True):
            st.markdown("#### ⚡ Two-Tier AI Study Assistant")
            st.caption("Answers student questions using verified local HamroCSIT notes first, citing Semester > Subject > Chapter, and seamlessly falls back to general AI.")
    with w2:
        with st.container(border=True):
            st.markdown("#### 📚 375 Chapters & 66 Subjects")
            st.caption("Complete 8-semester curriculum coverage from Tribhuvan University with direct access to lecture notes, syllabi, and presentation slides.")
    with w3:
        with st.container(border=True):
            st.markdown("#### 📝 Real TU Question Banks")
            st.caption("Over 6,600 real past Tribhuvan University board examination questions with comprehensive solutions and model practice sets.")

# --------------------------------------------------------------------------- #
# VIEW: 📚 Semester Page (Subjects Grid)
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "semester":
    sem_slug = st.session_state.active_semester_slug
    sem_data = semesters_data.get(sem_slug, {})

    # HamroCSIT Site Breadcrumb Banner
    st.markdown(
        f"""
        <div class="site-breadcrumb">
            <h1 class="breadcrumb-title">{sem_data.get('title', 'Semester')}</h1>
            <div class="breadcrumb-sub">Home / {sem_data.get('title', 'Semester')} / Subjects</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick Switcher
    sem_keys = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight"]
    col_sel, _ = st.columns([3, 5])
    with col_sel:
        chosen_sem = st.selectbox(
            "Select Semester",
            options=sem_keys,
            format_func=lambda s: semesters_data.get(s, {}).get("title", s.title()),
            index=sem_keys.index(sem_slug) if sem_slug in sem_keys else 3,
            key="sem_page_selector",
        )
        if chosen_sem != sem_slug:
            st.session_state.active_semester_slug = chosen_sem
            st.rerun()

    st.markdown("<hr style='margin: 16px 0 24px 0; border: none; border-bottom: 1px solid #edeef3;'>", unsafe_allow_html=True)

    # Subjects grid (2 columns matching HamroCSIT card_main)
    subjects = sem_data.get("subjects", [])
    cols = st.columns(2)
    for idx, sub in enumerate(subjects):
        col = cols[idx % 2]
        with col:
            st.markdown(
                f"""
                <div class="card_main">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-size: 11px; font-weight: 700; color: #00af92; background: #e6f7f4; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">{sub.get('code') or 'TU CSIT'}</span>
                            <h5 style="margin-top: 8px;">{sub.get('name')}</h5>
                        </div>
                        <span style="font-size: 26px;">📖</span>
                    </div>
                    <p>{sub.get('description') or 'Comprehensive reference material including chapters, syllabus, question banks, and practicals.'}</p>
                    <div style="font-size: 12.5px; font-weight: 600; color: #00af92; margin-bottom: 12px;">
                        Chapters Available : {sub.get('chapter_count', 0)}+
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Explore {sub.get('name')}", key=f"btn_explore_sub_{sub['slug']}_{idx}", use_container_width=True):
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
        st.error("Subject not found.")
        if st.button("Back to Home"):
            st.session_state.current_view = "home"
            st.rerun()
    else:
        st.markdown(
            f"""
            <div class="site-breadcrumb">
                <h1 class="breadcrumb-title">{sub_data.get('name')}</h1>
                <div class="breadcrumb-sub">Home / {sem_data.get('title')} / {sub_data.get('name')} ({sub_data.get('code')})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_chaps, tab_syl, tab_qbank, tab_prac, tab_link = st.tabs([
            "📖 Chapters", "📋 Syllabus", "📝 Past Questions", "🔬 Practical", "🌐 HamroCSIT Direct"
        ])

        with tab_chaps:
            chapters = sub_data.get("chapters", [])
            if chapters:
                st.markdown(f"### {sub_data.get('name')} Chapters ({len(chapters)} Modules)")
                for c_idx, chap in enumerate(chapters):
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**Chapter {c_idx + 1}: {chap.get('title')}**")
                            st.caption(f"Verified notes & academic outline for {chap.get('title')} in {sub_data.get('name')}.")
                        with c2:
                            if st.button("Read Note", key=f"btn_read_chap_{chap.get('chapter_slug')}_{c_idx}", use_container_width=True):
                                st.session_state.active_chapter_slug = chap.get("chapter_slug")
                                st.session_state.current_view = "chapter"
                                st.rerun()
            else:
                st.info(f"Notes for {sub_data.get('name')} are being updated. You can ask our AI Study Tutor any question from this subject!")

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

            st.markdown(f"### {sub_data.get('name')} — Past TU Board Questions")
            if local_qs:
                st.info(f"Showing {len(local_qs)} verified past board questions. HamroCSIT hosts {total_q_count}+ questions for this subject.")
                for qi, qitem in enumerate(local_qs, 1):
                    with st.container(border=True):
                        q_col1, q_col2 = st.columns([5, 1.2])
                        with q_col1:
                            st.markdown(f"**Q{qi}.** {qitem.get('title', '')}")
                            st.caption(f"📅 Published: {qitem.get('date', '')}")
                        with q_col2:
                            st.link_button("View Answer ↗", qitem.get("link", "https://hamrocsit.com/questions/"), use_container_width=True)
            else:
                st.info("Past questions for this subject are available on HamroCSIT.")
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
            st.link_button(f"Open {sub_data.get('name')} on HamroCSIT ↗", sub_data.get("url", "https://hamrocsit.com"))

# --------------------------------------------------------------------------- #
# VIEW: 📖 Chapter Reading View (Clean PDF.js Slides Viewer + Study Guide)
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

    if not chapter_info:
        st.error("Chapter not found.")
        if st.button("Back to Subject"):
            st.session_state.current_view = "subject"
            st.rerun()
    else:
        # Breadcrumbs
        st.markdown(
            f"""
            <div class="site-breadcrumb">
                <h1 class="breadcrumb-title">{chapter_info.get('title')}</h1>
                <div class="breadcrumb-sub">Home / {sem_data.get('title')} / {sub_data.get('name')} / {chapter_info.get('title')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        h_col1, h_col2, h_col3 = st.columns([3, 1.2, 1.2])
        with h_col1:
            st.markdown(f"**Subject:** {sub_data.get('name')} (`{sub_data.get('code')}`) · **Semester:** {sem_data.get('title')}")
        with h_col2:
            st.link_button("Open HamroCSIT ↗", chapter_info.get("url", "https://hamrocsit.com"), use_container_width=True)
        with h_col3:
            if st.button("⬅ Back to Chapters", use_container_width=True):
                st.session_state.current_view = "subject"
                st.rerun()

        st.markdown("<hr style='margin: 12px 0 20px 0; border: none; border-bottom: 1px solid #edeef3;'>", unsafe_allow_html=True)

        chap_tabs = st.tabs(["📖 Document & Slides Viewer", "📝 Key Academic Notes & Concepts", "🤖 Ask AI Tutor about this Chapter"])

        with chap_tabs[0]:
            # Retrieve direct clean viewer.php URL
            viewer_url = get_hamrocsit_viewer_url(chapter_info.get("url", ""))
            target_url = viewer_url if viewer_url else chapter_info.get("url", "https://hamrocsit.com")
            try:
                components.iframe(target_url, height=780, scrolling=True)
            except Exception:
                st.warning("Could not render viewer inline. Please click 'Open HamroCSIT' above to view the slides.")

        with chap_tabs[1]:
            matched_topic = None
            for t in kb.topics.values():
                if chap_slug and (chap_slug in t.slug or t.slug in chap_slug or chap_slug in t.title.lower()):
                    matched_topic = t
                    break

            if matched_topic:
                st.markdown(kb._format_topic_full(matched_topic))
            else:
                st.markdown(
                    f"""
                    ### Academic Study Module: {chapter_info.get('title')}
                    **Subject:** {sub_data.get('name')} (`{sub_data.get('code')}`) · **Semester:** {sem_data.get('title')}
                    
                    #### Core Syllabus Coverage:
                    1. **Theoretical Foundations:** Core definitions, models, and formal axioms.
                    2. **Procedural & Algorithmic Operations:** State transitions, pseudocode logic, and step-by-step processing.
                    3. **Standard Implementations:** Standard code patterns compliant with Tribhuvan University laboratories.
                    4. **Complexity & Performance Guarantees:** Big-O asymptotic analysis and spatial constraints.
                    5. **Examination Focal Points:** Frequently asked theoretical derivations and numerical questions from past TU board papers.
                    
                    ---
                    #### 📚 HamroCSIT Source & Verification
                    - **Curriculum Resource:** [{chapter_info.get('title')} on HamroCSIT ↗]({chapter_info.get('url')})
                    """
                )

        with chap_tabs[2]:
            st.markdown(f"### Ask AI Tutor about *{chapter_info.get('title')}*")
            st.caption(f"Grounds answers in {sub_data.get('name')} notes first, falling back to general AI if needed.")
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

        # Previous / Next navigation
        chapters_list = sub_data.get("chapters", [])
        current_idx = next((i for i, c in enumerate(chapters_list) if c["chapter_slug"] == chap_slug), 0)
        st.markdown("<hr style='margin: 24px 0 16px 0; border: none; border-bottom: 1px solid #edeef3;'>", unsafe_allow_html=True)
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
# VIEW: ❓ Question Bank
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "questions":
    st.markdown(
        """
        <div class="site-breadcrumb">
            <h1 class="breadcrumb-title">HamroCSIT Question Bank</h1>
            <div class="breadcrumb-sub">Past Tribhuvan University Examination Questions & Practice Sets</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    q_tabs = st.tabs(["📋 Browse by Subject", "🚀 Practice Exam Generator", "🌐 Archive"])

    with q_tabs[0]:
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
                    })

        subject_labels = [s["label"] for s in all_subjects_for_qbank]
        chosen_label = st.selectbox("Select Subject", options=subject_labels, key="qbank_sel_top")
        chosen_sub_info = next((s for s in all_subjects_for_qbank if s["label"] == chosen_label), None)

        if chosen_sub_info:
            slug = chosen_sub_info["slug"]
            qs = LIVE_QUESTIONS.get(slug, [])
            cat_info = SUBJECT_CATEGORIES.get(slug, {})
            total_on_site = cat_info.get("count", len(qs))

            st.info(f"Showing verified past questions for **{chosen_sub_info['name']}**. HamroCSIT has {total_on_site}+ questions for this course.")
            for i, q in enumerate(qs, 1):
                with st.container(border=True):
                    col_q1, col_q2 = st.columns([5, 1.2])
                    with col_q1:
                        st.markdown(f"**Q{i}.** {q.get('title', '')}")
                        st.caption(f"📅 Published: {q.get('date', '')}")
                    with col_q2:
                        st.link_button("View Answer ↗", q.get("link", "https://hamrocsit.com/questions/"), use_container_width=True)

    with q_tabs[1]:
        col_s, col_n = st.columns([3, 1])
        with col_s:
            q_subject = st.selectbox(
                "Choose Subject",
                options=[s["name"] for s in all_subjects_for_qbank],
                key="qbank_gen_sub",
            )
        with col_n:
            q_count = st.slider("Number of Questions", min_value=3, max_value=8, value=5)

        if st.button("🚀 Generate TU Practice Exam Paper", type="primary", use_container_width=True):
            with st.spinner("Generating practice exam paper with model rubrics..."):
                paper = chat_backend.generate_exam_prep(subject=q_subject, num_questions=q_count)
                st.markdown(paper)

    with q_tabs[2]:
        st.markdown("### Complete HamroCSIT Question Archive")
        st.markdown("Over 6,600+ past TU examination questions with model solutions across all 8 semesters.")
        st.link_button("Explore Complete Archive on HamroCSIT ↗", "https://hamrocsit.com/questions/")

# --------------------------------------------------------------------------- #
# VIEW: 📢 TU Notices
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "notices":
    st.markdown(
        """
        <div class="site-breadcrumb">
            <h1 class="breadcrumb-title">TU CSIT Notices & Announcements</h1>
            <div class="breadcrumb-sub">Latest academic notifications from Tribhuvan University IOST, fetched live from HamroCSIT</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if LIVE_NOTICES:
        for notice in LIVE_NOTICES:
            with st.container(border=True):
                col_n1, col_n2 = st.columns([5, 1])
                with col_n1:
                    st.markdown(f"**{notice.get('title', 'Notice')}**")
                    st.caption(f"📅 Published: {notice.get('date', 'Unknown date')}")
                with col_n2:
                    st.link_button("Read →", notice.get("link", "https://hamrocsit.com/notice/"), use_container_width=True)
    else:
        st.info("Notices are currently unavailable. Visit HamroCSIT directly.")
        st.link_button("Open HamroCSIT Notices ↗", "https://hamrocsit.com/notice/")

# --------------------------------------------------------------------------- #
# VIEW: 🎓 Entrance Preparation
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "entrance":
    st.markdown(
        """
        <div class="site-breadcrumb">
            <h1 class="breadcrumb-title">BSc CSIT Entrance Preparation</h1>
            <div class="breadcrumb-sub">Free mock tests, MCQ banks, and college admission guidelines</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
# VIEW: 🤖 AI Study Tutor (Full Page)
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "ai_tutor":
    st.markdown(
        """
        <div class="site-breadcrumb">
            <h1 class="breadcrumb-title">Hamro CSIT AI Study Tutor</h1>
            <div class="breadcrumb-sub">Two-Tier Learning Assistant: Grounds answers in course notes first; falls back to general AI when needed.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    full_chat_in = st.chat_input("Ask any CSIT question (e.g., 'quick sort', 'normalization', 'compare tcp and udp')...", key="full_page_chat")
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
# Footer (Exact HamroCSIT Footer Structure)
# --------------------------------------------------------------------------- #
st.markdown("<hr style='margin: 48px 0 24px 0; border: none; border-bottom: 1px solid #edeef3;'>", unsafe_allow_html=True)
f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
with f_col1:
    st.markdown(
        f"""
        <div class="hamro-brand" style="margin-bottom: 8px;">
            <img src="{HAMRO_LOGO_DATA_URI}" width="32" height="32" alt="HamroCSIT Logo" />
            <div class="hamro-logo-text" style="font-size: 19px;">
                HAMRO<span class="hamro-sub">CSIT</span>
            </div>
        </div>
        <p style="font-size: 13.5px; color: #64748b; line-height: 1.6; max-width: 420px;">
            Hamro CSIT is a comprehensive web and mobile platform that provides B.Sc. CSIT students with resources
            like notes, syllabi, question banks, solved past papers, practical files, and free entrance preparation materials.
        </p>
        """,
        unsafe_allow_html=True,
    )
with f_col2:
    st.markdown("**Quick Links**")
    st.caption("• [HamroCSIT Official Site ↗](https://hamrocsit.com/)")
    st.caption("• [TU IOST Examination Hub ↗](https://iost.tu.edu.np/)")
    st.caption("• [HamroCSIT Android App ↗](https://play.google.com/store/apps/details?id=com.hamrocsit)")
with f_col3:
    st.markdown("**Developer & Portal**")
    st.caption("Developed by **Samyog Sapkota**")
    st.caption("B.Sc. CSIT · Prime College, Khusibu")
    st.caption("Copyright 2026 | **HAMROCSIT** | All Right Reserved")
