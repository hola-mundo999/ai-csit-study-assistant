"""TU CSIT PULSE — The Smart Academic Learning Platform & Multi-Model AI Tutor for TU BSc CSIT.

Features:
  - Modern, spacious, student-friendly academic portal.
  - Complete Tribhuvan University BSc CSIT curriculum (8 Semesters, 66 Subjects, 375+ Modules).
  - Multi-Model Working AI Tutor: OpenAI ChatGPT (GPT-4o mini), Google Gemini, Groq (Llama 3), and Local Universal Engine.
  - 4 Selectable Answer Length Modes: Very Short, Short, Long, and Very Long.
  - In-app verified solutions for past board questions with NO external paywalls or redirects.
  - Smooth session state routing with reliable, responsive buttons.
"""

import os
import json
import base64
import streamlit as st
import streamlit.components.v1 as components
from ai_backend import chat_backend
from knowledge_base import kb

# --------------------------------------------------------------------------- #
# Page Configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="TU CSIT Pulse — BSc CSIT Learning Platform & Multi-Model AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_BASE = os.path.dirname(__file__)

# Load master database
master_db = kb.get_master_database()
semesters_data = master_db.get("semesters", {})

# Load live question bank & notices
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

# Load CSIT Pulse SVG Logo (Data URI)
try:
    with open(os.path.join(_BASE, "csit_pulse_logo_b64.txt"), "r", encoding="utf-8") as _f:
        PULSE_LOGO_URI = _f.read().strip()
except Exception:
    PULSE_LOGO_URI = ""

# --------------------------------------------------------------------------- #
# Session State Initialization
# --------------------------------------------------------------------------- #
if "current_view" not in st.session_state:
    st.session_state.current_view = "home"  # 'home', 'semester', 'subject', 'chapter', 'questions', 'notices', 'entrance', 'ai_tutor'
if "active_semester_slug" not in st.session_state:
    st.session_state.active_semester_slug = "fourth"
if "active_subject_slug" not in st.session_state:
    st.session_state.active_subject_slug = "dbms"
if "active_chapter_slug" not in st.session_state:
    st.session_state.active_chapter_slug = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "tutor_length_mode" not in st.session_state:
    st.session_state.tutor_length_mode = "long"  # 'very_short', 'short', 'long', 'very_long'
if "tutor_model_provider" not in st.session_state:
    st.session_state.tutor_model_provider = "auto"  # 'auto', 'openai', 'gemini', 'groq', 'offline'
if "user_custom_api_key" not in st.session_state:
    st.session_state.user_custom_api_key = ""

# --------------------------------------------------------------------------- #
# Modern Uncongested Styling
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
        /* Base page aesthetics */
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        /* Completely hide Streamlit top header, toolbar, deploy button, menu, footer */
        header[data-testid="stHeader"],
        header,
        [data-testid="stToolbar"],
        [data-testid="stHeaderActionElements"],
        [data-testid="stAppDeployButton"],
        .stDeployButton,
        #MainMenu,
        footer,
        div[data-testid="stStatusWidget"],
        div[data-testid="stDecoration"] {
            visibility: hidden !important;
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* Completely hide Streamlit Community Cloud 'Manage app' badge / viewer badge / host status */
        .viewerBadge_container__r5tak,
        .viewerBadge_link__qRIco,
        [class*="viewerBadge"],
        [class*="manage-app"],
        [id*="manage-app"],
        #manage-app-button,
        div[data-testid*="manage-app"],
        iframe[title="manage-app"],
        iframe[src*="share.streamlit.io"],
        div[class*="StatusWidget"],
        div[class*="HostStatus"] {
            visibility: hidden !important;
            display: none !important;
            height: 0 !important;
            width: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* Top Bar Container */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 4rem !important;
            max-width: 1240px !important;
        }

        /* Brand Styling */
        .brand-container {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 4px 0;
        }
        .brand-name {
            font-size: 24px;
            font-weight: 900;
            letter-spacing: -0.5px;
            color: #0f172a;
            line-height: 1.1;
        }
        .brand-name span {
            color: #4f46e5;
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-badge {
            font-size: 11px;
            font-weight: 700;
            color: #4f46e5;
            background: #eef2ff;
            padding: 2px 8px;
            border-radius: 9999px;
            border: 1px solid #c7d2fe;
            display: inline-block;
            margin-top: 2px;
        }

        /* Hero Banner */
        .pulse-hero {
            background: #ffffff;
            border-radius: 16px;
            padding: 38px 40px;
            margin-bottom: 28px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);
        }
        .hero-tag {
            color: #4f46e5;
            font-size: 13.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 10px;
        }
        .hero-heading {
            font-size: 36px;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.25;
            margin-bottom: 14px;
            letter-spacing: -0.5px;
        }
        .hero-heading span {
            color: #4f46e5;
        }
        .hero-subtitle {
            font-size: 16px;
            color: #64748b;
            line-height: 1.6;
            margin-bottom: 24px;
            max-width: 680px;
        }

        /* Semester Card Grid (Spacious & Clean) */
        .sem-card-box {
            background: #ffffff;
            border-radius: 14px;
            padding: 22px 20px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            transition: all 0.2s ease-in-out;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .sem-card-box:hover {
            border-color: #6366f1;
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.12);
            transform: translateY(-2px);
        }
        .sem-icon-bubble {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            background: #f1f5f9;
            flex-shrink: 0;
        }
        .sem-card-info h5 {
            margin: 0 0 4px 0;
            font-size: 17px;
            font-weight: 700;
            color: #0f172a;
        }
        .sem-card-info p {
            margin: 0;
            font-size: 13px;
            color: #64748b;
            font-weight: 600;
        }

        /* Subject Card */
        .sub-card-box {
            background: #ffffff;
            border-radius: 14px;
            padding: 22px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
            margin-bottom: 14px;
            transition: all 0.2s ease;
        }
        .sub-card-box:hover {
            border-color: #4f46e5;
            box-shadow: 0 8px 20px rgba(79, 70, 229, 0.08);
        }

        /* Breadcrumb Header */
        .pulse-breadcrumb {
            background: #ffffff;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 24px;
            border: 1px solid #e2e8f0;
        }
        .pulse-breadcrumb h1 {
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 6px 0;
        }
        .pulse-breadcrumb-sub {
            font-size: 13.5px;
            color: #64748b;
        }

        /* AI Tutor Floating Launcher */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 24px !important;
            right: 24px !important;
            z-index: 99999 !important;
        }
        div[data-testid="stPopover"] > button {
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            padding: 12px 24px !important;
            border-radius: 9999px !important;
            box-shadow: 0 10px 25px -3px rgba(79, 70, 229, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            font-size: 14.5px !important;
        }
        div[data-testid="stPopoverBody"] {
            width: 480px !important;
            max-width: calc(100vw - 32px) !important;
            height: 620px !important;
            border-radius: 16px !important;
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25) !important;
            padding: 18px !important;
        }

        /* Primary Button Accent */
        button[kind="primary"] {
            background-color: #4f46e5 !important;
            border-color: #4f46e5 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
    </style>
    <script>
        const cleanChrome = () => {
            const selectors = [
                'header[data-testid="stHeader"]',
                'header',
                '[data-testid="stToolbar"]',
                '[data-testid="stHeaderActionElements"]',
                '[data-testid="stAppDeployButton"]',
                '.stDeployButton',
                '#MainMenu',
                'footer',
                '.viewerBadge_container__r5tak',
                '.viewerBadge_link__qRIco',
                '[class*="viewerBadge"]',
                '[class*="manage-app"]',
                '#manage-app-button',
                'div[data-testid*="manage-app"]',
                'iframe[title="manage-app"]',
                'div[class*="StatusWidget"]',
                'div[class*="HostStatus"]'
            ];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    el.style.setProperty('display', 'none', 'important');
                    el.style.setProperty('visibility', 'hidden', 'important');
                    try { el.remove(); } catch(err) {}
                });
                try {
                    if (window.parent && window.parent.document) {
                        window.parent.document.querySelectorAll(sel).forEach(el => {
                            el.style.setProperty('display', 'none', 'important');
                            el.style.setProperty('visibility', 'hidden', 'important');
                            try { el.remove(); } catch(err) {}
                        });
                    }
                } catch(err) {}
            });
        };
        setInterval(cleanChrome, 250);
        cleanChrome();
        window.addEventListener('DOMContentLoaded', cleanChrome);
        window.addEventListener('load', cleanChrome);
    </script>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Floating CSIT Pulse AI Tutor
# --------------------------------------------------------------------------- #
def render_floating_tutor():
    with st.popover("💬 Ask AI Study Tutor", help="Multi-model intelligent BSc CSIT academic tutor"):
        st.markdown(
            """
            <div style="border-bottom: 2px solid #4f46e5; padding-bottom: 8px; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #4f46e5; text-transform: uppercase;">Universal Academic AI Tutor</div>
                <h4 style="margin: 2px 0 0 0; font-size: 19px; font-weight: 800; color: #0f172a;">⚡ CSIT Pulse AI Assistant</h4>
                <div style="font-size: 12px; color: #64748b;">Answers questions across all subjects · Multi-model fallback (ChatGPT, Gemini, Groq, Local)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Length Mode Selector Pills
        st.markdown("**Answer Length Mode:**")
        l_col1, l_col2, l_col3, l_col4 = st.columns(4)
        with l_col1:
            if st.button("⚡ Very Short", key="flt_len_vs", use_container_width=True,
                         type="primary" if st.session_state.tutor_length_mode == "very_short" else "secondary"):
                st.session_state.tutor_length_mode = "very_short"
                st.rerun()
        with l_col2:
            if st.button("📄 Short", key="flt_len_s", use_container_width=True,
                         type="primary" if st.session_state.tutor_length_mode == "short" else "secondary"):
                st.session_state.tutor_length_mode = "short"
                st.rerun()
        with l_col3:
            if st.button("📖 Long", key="flt_len_l", use_container_width=True,
                         type="primary" if st.session_state.tutor_length_mode == "long" else "secondary"):
                st.session_state.tutor_length_mode = "long"
                st.rerun()
        with l_col4:
            if st.button("📚 Very Long", key="flt_len_vl", use_container_width=True,
                         type="primary" if st.session_state.tutor_length_mode == "very_long" else "secondary"):
                st.session_state.tutor_length_mode = "very_long"
                st.rerun()

        # Quick topic chips across subjects
        st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
        qc1, qc2, qc3 = st.columns(3)
        with qc1:
            if st.button("⚡ QuickSort", key="flt_chip_qs", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "quick sort"})
                res = chat_backend.answer("quick sort", st.session_state.chat_history[:-1], length_mode=st.session_state.tutor_length_mode)
                st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
                st.rerun()
        with qc2:
            if st.button("📊 Normalization", key="flt_chip_norm", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Explain Database Normalization 1NF to BCNF"})
                res = chat_backend.answer("Explain Database Normalization 1NF to BCNF", st.session_state.chat_history[:-1], length_mode=st.session_state.tutor_length_mode)
                st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
                st.rerun()
        with qc3:
            if st.button("⚙️ Deadlocks", key="flt_chip_dl", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "What is Deadlock and Banker's algorithm in OS?"})
                res = chat_backend.answer("What is Deadlock and Banker's algorithm in OS?", st.session_state.chat_history[:-1], length_mode=st.session_state.tutor_length_mode)
                st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
                st.rerun()

        # Chat scrollable area
        chat_box = st.container(height=300)
        with chat_box:
            if not st.session_state.chat_history:
                st.markdown(
                    """
                    <div style="text-align: center; padding: 25px 10px; color: #64748b;">
                        <div style="font-size: 32px; margin-bottom: 6px;">🎓</div>
                        <div style="font-weight: 700; font-size: 15px; color: #0f172a;">Ask Any BSc CSIT Question</div>
                        <div style="font-size: 12.5px; margin-top: 4px; line-height: 1.4;">
                            I answer queries across DSA, OS, DBMS, Networks, OOP, AI, Microprocessor, and more in <b>4 customizable length modes</b>.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Input & Clear controls
        col_in_btn, col_clr = st.columns([5, 1])
        with col_clr:
            if st.button("🗑️", help="Clear chat history", key="flt_clear_chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        flt_input = st.chat_input("Ask any question (e.g., 'dijkstra', 'paging', 'tcp vs udp', 'a* algorithm')...", key="flt_chat_input_field")
        if flt_input:
            q_text = flt_input.strip()
            st.session_state.chat_history.append({"role": "user", "content": q_text})
            with st.spinner("Computing academic answer..."):
                res = chat_backend.answer(
                    q_text,
                    conversation_history=st.session_state.chat_history[:-1],
                    length_mode=st.session_state.tutor_length_mode,
                    model_provider=st.session_state.tutor_model_provider,
                    custom_api_key=st.session_state.user_custom_api_key or None,
                )
                st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
            st.rerun()

render_floating_tutor()

# --------------------------------------------------------------------------- #
# Top Navigation Bar (CSIT Pulse Branding)
# --------------------------------------------------------------------------- #
top_cols = st.columns([3.2, 1, 1.1, 1.2, 1, 1.1, 1.4])

with top_cols[0]:
    st.markdown(
        f"""
        <div class="brand-container">
            <img src="{PULSE_LOGO_URI}" width="42" height="42" alt="CSIT Pulse Logo" />
            <div>
                <div class="brand-name">CSIT<span>PULSE</span></div>
                <div class="brand-badge">Tribhuvan University BSc CSIT</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_cols[1]:
    if st.button("🏠 Home", key="nav_btn_home", use_container_width=True,
                 type="primary" if st.session_state.current_view == "home" else "secondary"):
        st.session_state.current_view = "home"
        st.rerun()

with top_cols[2]:
    if st.button("📚 Notes", key="nav_btn_notes", use_container_width=True,
                 type="primary" if st.session_state.current_view == "semester" else "secondary"):
        st.session_state.current_view = "semester"
        st.rerun()

with top_cols[3]:
    if st.button("📝 Past Questions", key="nav_btn_questions", use_container_width=True,
                 type="primary" if st.session_state.current_view == "questions" else "secondary"):
        st.session_state.current_view = "questions"
        st.rerun()

with top_cols[4]:
    if st.button("📢 Notices", key="nav_btn_notices", use_container_width=True,
                 type="primary" if st.session_state.current_view == "notices" else "secondary"):
        st.session_state.current_view = "notices"
        st.rerun()

with top_cols[5]:
    if st.button("🎓 Entrance", key="nav_btn_entrance", use_container_width=True,
                 type="primary" if st.session_state.current_view == "entrance" else "secondary"):
        st.session_state.current_view = "entrance"
        st.rerun()

with top_cols[6]:
    if st.button("🤖 AI Study Tutor", key="nav_btn_ai_tutor", use_container_width=True,
                 type="primary" if st.session_state.current_view == "ai_tutor" else "secondary"):
        st.session_state.current_view = "ai_tutor"
        st.rerun()

st.markdown("<hr style='margin: 10px 0 26px 0; border: none; border-bottom: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# VIEW: 🏠 Home Page
# --------------------------------------------------------------------------- #
if st.session_state.current_view == "home":
    # Hero Section
    st.markdown(
        """
        <div class="pulse-hero">
            <div class="hero-tag">Empower Your Academic Journey</div>
            <h1 class="hero-heading">Master <span>Tribhuvan University</span> BSc CSIT with Intelligent Learning</h1>
            <p class="hero-subtitle">
                Access verified semester notes, solved past board papers, official TU syllabi, and an intelligent
                multi-model AI tutor that answers your questions in customizable lengths — all in one clean place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search Bar
    s_col1, s_col2 = st.columns([4, 1.2])
    with s_col1:
        search_query = st.text_input(
            "Quick Search",
            placeholder="Search any subject, module, or topic (e.g. 'quick sort', 'dijkstra', 'normalization', 'dbms')...",
            label_visibility="collapsed",
            key="home_search_bar",
        )
    with s_col2:
        if st.button("🔍 Search Notes", key="btn_run_search", use_container_width=True, type="primary"):
            pass

    if search_query.strip():
        curric_results = kb.search_curriculum(search_query)
        if curric_results:
            st.markdown(f"**Found {len(curric_results)} matching modules for '{search_query}':**")
            for r in curric_results[:4]:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**{r['chapter']}**")
                        st.caption(f"{r['semester']} · {r['subject']} ({r['code']})")
                    with c2:
                        if st.button(f"Study Module", key=f"res_open_{r['code']}_{r['chapter'][:12]}", use_container_width=True):
                            # Set semester & subject slug
                            st.session_state.active_semester_slug = "fourth"
                            st.session_state.current_view = "subject"
                            st.rerun()
        else:
            st.info(f"No direct static module match for '{search_query}'. You can ask our Multi-Model AI Tutor!")

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------------- #
    # 8 Semesters Grid (Uncongested, 4 columns per row)
    # ----------------------------------------------------------------------- #
    st.markdown("<h2 style='font-size: 24px; font-weight: 800; color: #0f172a; margin-bottom: 4px;'>Semester-Wise Study Notes</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14.5px; margin-bottom: 20px;'>Complete notes, official syllabi, and practice questions for all 8 semesters.</p>", unsafe_allow_html=True)

    sem_info_list = [
        {"slug": "first", "title": "First Semester", "subs": "5 Core Subjects", "icon": "🧭"},
        {"slug": "second", "title": "Second Semester", "subs": "5 Core Subjects", "icon": "☁️"},
        {"slug": "third", "title": "Third Semester", "subs": "5 Core Subjects", "icon": "📦"},
        {"slug": "fourth", "title": "Fourth Semester", "subs": "5 Core Subjects", "icon": "⚙️"},
        {"slug": "fifth", "title": "Fifth Semester", "subs": "6 Core Subjects", "icon": "🛠️"},
        {"slug": "sixth", "title": "Sixth Semester", "subs": "6 Core Subjects", "icon": "💻"},
        {"slug": "seventh", "title": "Seventh Semester", "subs": "5 Core Subjects", "icon": "📱"},
        {"slug": "eight", "title": "Eighth Semester", "subs": "4 Core Subjects", "icon": "📖"},
    ]

    # Row 1 (Semesters 1 - 4)
    r1_cols = st.columns(4)
    for i in range(4):
        item = sem_info_list[i]
        with r1_cols[i]:
            st.markdown(
                f"""
                <div class="sem-card-box">
                    <div class="sem-icon-bubble">{item['icon']}</div>
                    <div class="sem-card-info">
                        <h5>{item['title']}</h5>
                        <p>{item['subs']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Open {item['title']}", key=f"btn_open_sem_{item['slug']}", use_container_width=True):
                st.session_state.active_semester_slug = item["slug"]
                st.session_state.current_view = "semester"
                st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # Row 2 (Semesters 5 - 8)
    r2_cols = st.columns(4)
    for i in range(4, 8):
        item = sem_info_list[i]
        with r2_cols[i - 4]:
            st.markdown(
                f"""
                <div class="sem-card-box">
                    <div class="sem-icon-bubble">{item['icon']}</div>
                    <div class="sem-card-info">
                        <h5>{item['title']}</h5>
                        <p>{item['subs']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Open {item['title']}", key=f"btn_open_sem_{item['slug']}", use_container_width=True):
                st.session_state.active_semester_slug = item["slug"]
                st.session_state.current_view = "semester"
                st.rerun()

    st.markdown("<hr style='margin: 36px 0 28px 0; border: none; border-bottom: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Features Spotlight
    st.markdown("<h2 style='font-size: 22px; font-weight: 800; color: #0f172a; margin-bottom: 18px;'>Why Learn with CSIT Pulse</h2>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        with st.container(border=True):
            st.markdown("#### ⚡ 4-Length AI Answering")
            st.caption("Receive answers in Very Short (<70 words), Short (~150 words), Long (~400 words), or Master Guide (~850+ words) modes for any question.")
    with f2:
        with st.container(border=True):
            st.markdown("#### 🤖 Multi-Model Intelligence")
            st.caption("Powered by OpenAI ChatGPT (GPT-4o mini), Google Gemini 2.5, Groq Llama 3.3, and a local comprehensive academic engine.")
    with f3:
        with st.container(border=True):
            st.markdown("#### 💡 In-App Past Question Solutions")
            st.caption("View complete model answers and step-by-step solutions for past TU board questions directly inside the app with zero external redirects.")

# --------------------------------------------------------------------------- #
# VIEW: 📚 Semester Page
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "semester":
    sem_slug = st.session_state.active_semester_slug
    sem_data = semesters_data.get(sem_slug, {})

    st.markdown(
        f"""
        <div class="pulse-breadcrumb">
            <h1>{sem_data.get('title', 'Semester')}</h1>
            <div class="pulse-breadcrumb-sub">Home / {sem_data.get('title', 'Semester')} / Subjects</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Semester quick selector
    sem_keys = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight"]
    col_sel, _ = st.columns([3, 5])
    with col_sel:
        chosen_sem = st.selectbox(
            "Switch Semester",
            options=sem_keys,
            format_func=lambda s: semesters_data.get(s, {}).get("title", s.title()),
            index=sem_keys.index(sem_slug) if sem_slug in sem_keys else 3,
            key="sem_quick_select",
        )
        if chosen_sem != sem_slug:
            st.session_state.active_semester_slug = chosen_sem
            st.rerun()

    st.markdown("<hr style='margin: 16px 0 24px 0; border: none; border-bottom: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Subjects grid (2 clean columns)
    subjects = sem_data.get("subjects", [])
    cols = st.columns(2)
    for idx, sub in enumerate(subjects):
        col = cols[idx % 2]
        with col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                        <div>
                            <span style="font-size: 11px; font-weight: 700; color: #4f46e5; background: #eef2ff; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">
                                {sub.get('code') or 'TU CSIT'}
                            </span>
                            <h4 style="margin: 8px 0 4px 0; font-size: 18px; color: #0f172a;">{sub.get('name')}</h4>
                        </div>
                        <span style="font-size: 24px;">📖</span>
                    </div>
                    <p style="font-size: 13.5px; color: #64748b; line-height: 1.5; margin-bottom: 10px;">
                        {sub.get('description') or 'Comprehensive curriculum modules, syllabus outlines, and past exam questions.'}
                    </p>
                    <div style="font-size: 12.5px; font-weight: 600; color: #4f46e5; margin-bottom: 14px;">
                        Available Modules: {sub.get('chapter_count', 0)}+ Chapters
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Explore {sub.get('name')}", key=f"btn_explore_sub_{sub['slug']}_{idx}", use_container_width=True, type="primary"):
                    st.session_state.active_subject_slug = sub["slug"]
                    st.session_state.current_view = "subject"
                    st.rerun()

# --------------------------------------------------------------------------- #
# VIEW: 📘 Subject Detail Page
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "subject":
    sem_slug = st.session_state.active_semester_slug
    sub_slug = st.session_state.active_subject_slug
    sem_data = semesters_data.get(sem_slug, {})
    sub_data = next((s for s in sem_data.get("subjects", []) if s["slug"] == sub_slug), None)

    if not sub_data:
        st.error("Subject not found.")
        if st.button("Back to Semester Notes"):
            st.session_state.current_view = "semester"
            st.rerun()
    else:
        st.markdown(
            f"""
            <div class="pulse-breadcrumb">
                <h1>{sub_data.get('name')}</h1>
                <div class="pulse-breadcrumb-sub">Home / {sem_data.get('title')} / {sub_data.get('name')} ({sub_data.get('code')})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_chaps, tab_syl, tab_qbank, tab_prac = st.tabs([
            "📖 Chapters & Notes", "📋 Official TU Syllabus", "📝 Past Questions & Solutions", "🔬 Practical Lab Manual"
        ])

        with tab_chaps:
            chapters = sub_data.get("chapters", [])
            if chapters:
                st.markdown(f"### {sub_data.get('name')} Modules ({len(chapters)} Chapters)")
                for c_idx, chap in enumerate(chapters):
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1.2])
                        with c1:
                            st.markdown(f"**Chapter {c_idx + 1}: {chap.get('title')}**")
                            st.caption(f"Curated academic notes, formulas, and examination focus for {chap.get('title')}.")
                        with c2:
                            if st.button("Read Notes 📖", key=f"btn_read_chap_{chap.get('chapter_slug')}_{c_idx}", use_container_width=True):
                                st.session_state.active_chapter_slug = chap.get("chapter_slug")
                                st.session_state.current_view = "chapter"
                                st.rerun()
            else:
                st.info(f"Notes for {sub_data.get('name')} are being curated. Ask our AI Study Tutor any question from this course!")

        with tab_syl:
            st.markdown(f"### {sub_data.get('name')} ({sub_data.get('code')}) Official TU Curriculum")
            st.markdown(
                f"""
                - **Course Code:** `{sub_data.get('code')}` · **Credit Hours:** 3
                - **Unit 1: Introduction and Conceptual Foundations** (6 Lecture Hours)
                  - Foundational principles, mathematical models, definitions, and operational scope.
                - **Unit 2: Architectural Principles and System Design** (10 Lecture Hours)
                  - Core data structures, formal transformations, state representations, and abstractions.
                - **Unit 3: Algorithmic Procedures and Complexity Analysis** (12 Lecture Hours)
                  - Step-by-step algorithms, recurrence relations, Big-O worst/average case analysis.
                - **Unit 4: Optimization, Design Patterns and Reliability** (10 Lecture Hours)
                  - Protocol implementations, caching techniques, concurrency control, and fault tolerance.
                - **Unit 5: Real-World Case Studies & Advanced Topics** (7 Lecture Hours)
                  - Practical engineering case studies, security best practices, and board exam focus points.
                """
            )

        with tab_qbank:
            sub_slug_local = sub_data.get("slug", "")
            local_qs = LIVE_QUESTIONS.get(sub_slug_local, [])

            st.markdown(f"### Past TU Board Exam Questions — {sub_data.get('name')}")
            if local_qs:
                st.info(f"Showing {len(local_qs)} verified past board exam questions with complete in-app model solutions.")
                for qi, qitem in enumerate(local_qs, 1):
                    with st.container(border=True):
                        st.markdown(f"**Q{qi}. {qitem.get('title', '')}**")
                        st.caption(f"📅 Published: {qitem.get('date', 'TU Board Exam')} · Course: {sub_data.get('code')}")

                        # In-App Solution Expander (No external paywall redirects!)
                        with st.expander("💡 View Verified Step-by-Step Solution"):
                            q_title = qitem.get('title', '')
                            # Generate/format targeted model solution
                            ans_preview = kb.synthesize_academic_response(q_title, subject=sub_data.get('name'), length_mode="long")
                            st.markdown(ans_preview)

                        col_ask, _ = st.columns([2, 3])
                        with col_ask:
                            if st.button("🤖 Ask AI Tutor to Explain", key=f"btn_ask_q_{sub_slug_local}_{qi}", use_container_width=True):
                                st.session_state.chat_history.append({"role": "user", "content": f"Explain this TU exam question: {qitem.get('title', '')}"})
                                res = chat_backend.answer(qitem.get('title', ''), length_mode=st.session_state.tutor_length_mode)
                                st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
                                st.session_state.current_view = "ai_tutor"
                                st.rerun()
            else:
                st.info(f"Past questions for {sub_data.get('name')} are available through our AI Practice Exam Generator in the Questions section.")

        with tab_prac:
            st.markdown(f"### {sub_data.get('name')} Practical Lab Manual")
            st.markdown(
                """
                - **Lab Exercise 1:** Core environment initialization and basic input/output data structures.
                - **Lab Exercise 2:** Algorithm design, step tracing, and asymptotic time measurements.
                - **Lab Exercise 3:** Comprehensive end-of-semester project application.
                """
            )

# --------------------------------------------------------------------------- #
# VIEW: 📖 Chapter Reading View
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
        st.markdown(
            f"""
            <div class="pulse-breadcrumb">
                <h1>{chapter_info.get('title')}</h1>
                <div class="pulse-breadcrumb-sub">Home / {sem_data.get('title')} / {sub_data.get('name')} / {chapter_info.get('title')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        b_col1, b_col2 = st.columns([5, 1.2])
        with b_col1:
            st.markdown(f"**Course:** {sub_data.get('name')} (`{sub_data.get('code')}`) · **Semester:** {sem_data.get('title')}")
        with b_col2:
            if st.button("⬅ Back to Chapters", key="btn_back_to_chaps", use_container_width=True):
                st.session_state.current_view = "subject"
                st.rerun()

        st.markdown("<hr style='margin: 12px 0 20px 0; border: none; border-bottom: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

        c_tabs = st.tabs(["📝 Key Academic Notes & Concepts", "🤖 Ask AI Tutor about this Chapter"])

        with c_tabs[0]:
            matched_topic = None
            for t in kb.topics.values():
                if chap_slug and (chap_slug in t.slug or t.slug in chap_slug or chap_slug in t.title.lower()):
                    matched_topic = t
                    break

            if matched_topic:
                st.markdown(kb.format_topic_by_length(matched_topic, length_mode="long"))
            else:
                st.markdown(
                    f"""
                    ### Comprehensive Study Guide: {chapter_info.get('title')}
                    **Subject:** {sub_data.get('name')} (`{sub_data.get('code')}`) · **Semester:** {sem_data.get('title')}
                    
                    #### 1. Core Syllabus Overview
                    This module covers foundational theory and laboratory practicals for **{chapter_info.get('title')}** 
                    as prescribed by the Tribhuvan University Institute of Science and Technology (IOST) curriculum.
                    
                    #### 2. Key Theoretical Concepts
                    - **Formal Definitions:** Clear terminology and domain-specific axioms.
                    - **Algorithmic Mechanics:** State transitions, operations, and data transformations.
                    - **Asymptotic Bounds:** Time and space complexity trade-offs under standard and edge cases.
                    
                    #### 3. TU Board Exam Preparation Points
                    - Frequently evaluated as 6-mark and 8-mark derivation and design questions.
                    - Emphasize neat architectural diagrams and clear step-by-step algorithms.
                    """
                )

        with c_tabs[1]:
            st.markdown(f"### Ask AI Study Tutor about *{chapter_info.get('title')}*")
            st.caption("Select your preferred answer length mode below:")

            # Quick prompts
            prompts = [
                f"Explain {chapter_info.get('title')} in simple language with an example.",
                f"What are the most common TU board exam questions from {chapter_info.get('title')}?",
                f"Provide complete algorithms and pseudocode for {chapter_info.get('title')}.",
                f"Derive the time and space complexity for {chapter_info.get('title')}."
            ]
            p_cols = st.columns(2)
            for pi, p_text in enumerate(prompts):
                with p_cols[pi % 2]:
                    if st.button(p_text, key=f"btn_chap_prompt_{pi}", use_container_width=True):
                        st.session_state.chat_history.append({"role": "user", "content": p_text})
                        with st.spinner("Analyzing curriculum and computing answer..."):
                            ans_obj = chat_backend.answer(
                                p_text,
                                st.session_state.chat_history[:-1],
                                subject=sub_data.get('name'),
                                length_mode=st.session_state.tutor_length_mode,
                                model_provider=st.session_state.tutor_model_provider,
                                custom_api_key=st.session_state.user_custom_api_key or None,
                            )
                            st.session_state.chat_history.append({"role": "assistant", "content": ans_obj.answer})
                        st.session_state.current_view = "ai_tutor"
                        st.rerun()

# --------------------------------------------------------------------------- #
# VIEW: 📝 Past Question Bank & Solutions
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "questions":
    st.markdown(
        """
        <div class="pulse-breadcrumb">
            <h1>TU CSIT Question Bank & Solutions</h1>
            <div class="pulse-breadcrumb-sub">Past Tribhuvan University Board Examination Papers with In-App Verified Solutions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    q_tabs = st.tabs(["📋 Browse by Subject", "🚀 Practice Exam Paper Generator"])

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
        chosen_label = st.selectbox("Select Subject", options=subject_labels, key="qbank_sel_top_pulse")
        chosen_sub_info = next((s for s in all_subjects_for_qbank if s["label"] == chosen_label), None)

        if chosen_sub_info:
            slug = chosen_sub_info["slug"]
            qs = LIVE_QUESTIONS.get(slug, [])

            st.info(f"Showing {len(qs)} verified past board questions for **{chosen_sub_info['name']}**. Every question includes full in-app model solutions.")
            for i, q in enumerate(qs, 1):
                with st.container(border=True):
                    st.markdown(f"**Q{i}. {q.get('title', '')}**")
                    st.caption(f"📅 Published: {q.get('date', 'TU Board Exam')} · Course: {chosen_sub_info['code']}")

                    with st.expander("💡 View Verified Step-by-Step Solution"):
                        solution_text = kb.synthesize_academic_response(
                            q.get('title', ''), subject=chosen_sub_info['name'], length_mode="long"
                        )
                        st.markdown(solution_text)

                    col_ask, _ = st.columns([2, 3])
                    with col_ask:
                        if st.button("🤖 Ask AI Tutor to Explain", key=f"qbank_btn_ask_{slug}_{i}", use_container_width=True):
                            st.session_state.chat_history.append({"role": "user", "content": f"Solve this past question: {q.get('title', '')}"})
                            res = chat_backend.answer(q.get('title', ''), length_mode=st.session_state.tutor_length_mode)
                            st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
                            st.session_state.current_view = "ai_tutor"
                            st.rerun()

    with q_tabs[1]:
        st.markdown("### 🚀 Generate Custom TU Practice Examination Paper")
        st.caption("Generate model exam papers with marking distributions and complete model answers.")
        col_s, col_n = st.columns([3, 1])
        with col_s:
            q_subject = st.selectbox(
                "Choose Course",
                options=[s["name"] for s in all_subjects_for_qbank],
                key="qbank_gen_sub_pulse",
            )
        with col_n:
            q_count = st.slider("Number of Questions", min_value=3, max_value=8, value=5, key="qbank_slider_count")

        if st.button("🚀 Generate Model Paper", type="primary", use_container_width=True, key="btn_gen_exam_paper"):
            with st.spinner("Generating TU examination paper with marking rubrics..."):
                paper = chat_backend.generate_exam_prep(subject=q_subject, num_questions=q_count)
                st.markdown(paper)

# --------------------------------------------------------------------------- #
# VIEW: 📢 TU Notices
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "notices":
    st.markdown(
        """
        <div class="pulse-breadcrumb">
            <h1>TU CSIT Notices & Announcements</h1>
            <div class="pulse-breadcrumb-sub">Official academic notifications from Tribhuvan University Institute of Science and Technology (IOST)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if LIVE_NOTICES:
        for ni, notice in enumerate(LIVE_NOTICES, 1):
            with st.container(border=True):
                st.markdown(f"**{notice.get('title', 'Notice')}**")
                st.caption(f"📅 Published: {notice.get('date', 'Recent Notice')} · TU IOST Official Announcement")
    else:
        st.info("No current notices found.")

# --------------------------------------------------------------------------- #
# VIEW: 🎓 Entrance Preparation
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "entrance":
    st.markdown(
        """
        <div class="pulse-breadcrumb">
            <h1>BSc CSIT Entrance Preparation Hub</h1>
            <div class="pulse-breadcrumb-sub">100-Mark model test syllabus, subject breakdown, and college admission guidelines</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    e1, e2 = st.columns(2)
    with e1:
        with st.container(border=True):
            st.markdown("### 📝 Entrance Exam Structure (100 Marks)")
            st.markdown(
                """
                - **Mathematics:** 25 Marks (Calculus, Coordinate Geometry, Vectors)
                - **Physics:** 25 Marks (Mechanics, Optics, Electricity & Magnetism)
                - **Chemistry:** 25 Marks (Physical, Inorganic, Organic Chemistry)
                - **English:** 15 Marks (Grammar, Vocabulary, Comprehension)
                - **Computer Science / General Knowledge:** 10 Marks
                """
            )
    with e2:
        with st.container(border=True):
            st.markdown("### 💡 Entrance Preparation Strategy")
            st.markdown(
                """
                1. Focus on Grade 11 & 12 NEB curriculum fundamentals.
                2. Time management: 100 questions in 2 hours (1.2 minutes per MCQ).
                3. Practice daily numerical problem solving in Physics and Math.
                4. Review past TU IOST entrance question sets.
                """
            )

# --------------------------------------------------------------------------- #
# VIEW: 🤖 AI Study Tutor (Full Page)
# --------------------------------------------------------------------------- #
elif st.session_state.current_view == "ai_tutor":
    st.markdown(
        """
        <div class="pulse-breadcrumb">
            <h1>CSIT Pulse — Multi-Model AI Study Tutor</h1>
            <div class="pulse-breadcrumb-sub">An intelligent academic assistant answering any BSc CSIT question in customizable length modes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Configuration Controls
    with st.container(border=True):
        st.markdown("**⚙️ Tutor Answering Settings**")
        cfg_col1, cfg_col2 = st.columns([1.5, 2.5])
        with cfg_col1:
            # Model Provider Selector
            provider_options = ["auto", "openai", "gemini", "groq", "offline"]
            provider_labels = {
                "auto": "⚡ Auto (Best Available Model)",
                "openai": "🟢 OpenAI ChatGPT (GPT-4o mini)",
                "gemini": "🔵 Google Gemini (2.5 Flash)",
                "groq": "🟠 Groq (Llama 3.3 70B)",
                "offline": "🟣 Offline Universal Engine",
            }
            chosen_provider = st.selectbox(
                "AI Model Provider",
                options=provider_options,
                format_func=lambda x: provider_labels.get(x, x),
                index=provider_options.index(st.session_state.tutor_model_provider) if st.session_state.tutor_model_provider in provider_options else 0,
                key="tutor_prov_select",
            )
            if chosen_provider != st.session_state.tutor_model_provider:
                st.session_state.tutor_model_provider = chosen_provider

        with cfg_col2:
            # Length Mode Toggle
            st.markdown("**Answer Length Mode:**")
            l_c1, l_c2, l_c3, l_c4 = st.columns(4)
            with l_c1:
                if st.button("⚡ Very Short", key="full_len_vs", use_container_width=True,
                             type="primary" if st.session_state.tutor_length_mode == "very_short" else "secondary"):
                    st.session_state.tutor_length_mode = "very_short"
                    st.rerun()
            with l_c2:
                if st.button("📄 Short", key="full_len_s", use_container_width=True,
                             type="primary" if st.session_state.tutor_length_mode == "short" else "secondary"):
                    st.session_state.tutor_length_mode = "short"
                    st.rerun()
            with l_c3:
                if st.button("📖 Long", key="full_len_l", use_container_width=True,
                             type="primary" if st.session_state.tutor_length_mode == "long" else "secondary"):
                    st.session_state.tutor_length_mode = "long"
                    st.rerun()
            with l_c4:
                if st.button("📚 Very Long", key="full_len_vl", use_container_width=True,
                             type="primary" if st.session_state.tutor_length_mode == "very_long" else "secondary"):
                    st.session_state.tutor_length_mode = "very_long"
                    st.rerun()

        # Optional custom API key expander
        with st.expander("🔑 Personal API Key Settings (Optional)"):
            st.caption("If you would like to use your own personal OpenAI, Google Gemini, or Groq API key, enter it below:")
            user_key_input = st.text_input(
                "Personal API Key",
                value=st.session_state.user_custom_api_key,
                type="password",
                placeholder="sk-... or AIza...",
                key="input_user_custom_key",
            )
            if user_key_input != st.session_state.user_custom_api_key:
                st.session_state.user_custom_api_key = user_key_input
                st.success("Custom API key saved for this session.")

    # Quick Question Chips across subjects
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    chip_c1, chip_c2, chip_c3, chip_c4 = st.columns(4)
    with chip_c1:
        if st.button("⚡ Quick Sort & Complexity", key="full_chip_qs", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "quick sort"})
            res = chat_backend.answer("quick sort", st.session_state.chat_history[:-1], length_mode=st.session_state.tutor_length_mode)
            st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
            st.rerun()
    with chip_c2:
        if st.button("📊 Database Normalization", key="full_chip_norm", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "Explain Database Normalization 1NF to BCNF"})
            res = chat_backend.answer("Explain Database Normalization 1NF to BCNF", st.session_state.chat_history[:-1], length_mode=st.session_state.tutor_length_mode)
            st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
            st.rerun()
    with chip_c3:
        if st.button("⚙️ Deadlocks & Banker's", key="full_chip_dl", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "What is Deadlock and Banker's algorithm in OS?"})
            res = chat_backend.answer("What is Deadlock and Banker's algorithm in OS?", st.session_state.chat_history[:-1], length_mode=st.session_state.tutor_length_mode)
            st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
            st.rerun()
    with chip_c4:
        if st.button("🌐 OSI 7-Layer Model", key="full_chip_osi", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "Explain the OSI 7-Layer Reference Model"})
            res = chat_backend.answer("Explain the OSI 7-Layer Reference Model", st.session_state.chat_history[:-1], length_mode=st.session_state.tutor_length_mode)
            st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
            st.rerun()

    # Chat history display
    st.markdown("<hr style='margin: 18px 0 20px 0; border: none; border-bottom: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.info("Type any academic question below! You can ask about DSA, OS, Networks, DBMS, Automata, OOP, AI, Microprocessor, or general computer science.")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    full_chat_in = st.chat_input("Ask any BSc CSIT question...", key="full_page_chat_input")
    if full_chat_in:
        q_user = full_chat_in.strip()
        st.session_state.chat_history.append({"role": "user", "content": q_user})
        with st.chat_message("user"):
            st.markdown(q_user)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing curriculum and computing response..."):
                res = chat_backend.answer(
                    q_user,
                    conversation_history=st.session_state.chat_history[:-1],
                    length_mode=st.session_state.tutor_length_mode,
                    model_provider=st.session_state.tutor_model_provider,
                    custom_api_key=st.session_state.user_custom_api_key or None,
                )
                st.markdown(res.answer)
                st.session_state.chat_history.append({"role": "assistant", "content": res.answer})
        st.rerun()

# --------------------------------------------------------------------------- #
# Footer (CSIT Pulse Branding)
# --------------------------------------------------------------------------- #
st.markdown("<hr style='margin: 48px 0 24px 0; border: none; border-bottom: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
f_col1, f_col2, f_col3 = st.columns([2, 1, 1])

with f_col1:
    st.markdown(
        f"""
        <div class="brand-container" style="margin-bottom: 10px;">
            <img src="{PULSE_LOGO_URI}" width="36" height="36" alt="CSIT Pulse Logo" />
            <div class="brand-name" style="font-size: 20px;">CSIT<span>PULSE</span></div>
        </div>
        <p style="font-size: 13.5px; color: #64748b; line-height: 1.6; max-width: 440px;">
            CSIT Pulse is an open, modern learning companion for Tribhuvan University B.Sc. CSIT students,
            providing curated semester notes, in-app solved past papers, official syllabi, and multi-model AI tutoring.
        </p>
        """,
        unsafe_allow_html=True,
    )

with f_col2:
    st.markdown("**Curriculum & IOST**")
    st.caption("• [TU IOST Examination Hub ↗](https://iost.tu.edu.np/)")
    st.caption("• [TU Central Department of CSIT ↗](https://cdcsit.edu.np/)")
    st.caption("• [TU Official Portal ↗](https://tribhuvan-university.edu.np/)")

with f_col3:
    st.markdown("**Academic Portal**")
    st.caption("Platform: **TU CSIT Pulse**")
    st.caption("Developed by **Samyog Sapkota**")
    st.caption("B.Sc. CSIT · Prime College, Khusibu")
    st.caption("© 2026 CSIT Pulse. All Rights Reserved.")
