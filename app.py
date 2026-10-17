import streamlit as st
import os
from pdf_processor import extract_text_from_pdf
from ai_engine import AIEngine

# Set Streamlit Page Config
st.set_page_config(
    page_title="CSIT AI Study Assistant | Samyog Sapkota",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (dark tech aesthetic matching portfolio)
st.markdown(
    """
<style>
    .stApp {
        background-color: #0b0d13;
        color: #e2e8f0;
    }
    .main-header {
        background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.15) 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(99,102,241,0.3);
        margin-bottom: 24px;
    }
    .header-badge {
        display: inline-block;
        background: rgba(99,102,241,0.2);
        color: #a5b4fc;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-family: monospace;
        margin-bottom: 8px;
        border: 1px solid rgba(99,102,241,0.4);
    }
    .metric-card {
        background: rgba(15,23,42,0.6);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .subject-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99,102,241,0.15);
        border: 1px solid rgba(99,102,241,0.35);
        color: #a5b4fc;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-family: monospace;
        margin-bottom: 12px;
    }
    .demo-banner {
        background: rgba(30,58,138,0.35);
        border: 1px solid rgba(99,102,241,0.35);
        border-radius: 12px;
        padding: 14px 18px;
        margin: 12px 0;
        font-size: 13px;
        line-height: 1.5;
    }
    .demo-banner b { color: #818cf8; }
    .source-note {
        font-size: 11.5px;
        font-family: monospace;
        color: #818cf8;
        border-top: 1px solid rgba(129,140,248,0.3);
        margin-top: 10px;
        padding-top: 8px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "extracted_doc" not in st.session_state:
    st.session_state.extracted_doc = None
if "active_file_name" not in st.session_state:
    st.session_state.active_file_name = None

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Settings & Configuration")

    provider = st.selectbox(
        "Select AI Provider",
        options=[
            "Demo Mode (No Key Needed)",
            "Google Gemini",
            "Groq (Llama-3.3-70B)",
        ],
        index=0,
        help="Demo Mode runs offline with no API key. Pick Gemini or Groq for live AI.",
    )

    api_key = None
    if "Gemini" in provider:
        api_key = st.text_input(
            "Gemini API Key", type="password", help="Get a free key at aistudio.google.com"
        )
        engine_provider = "gemini"
    elif "Groq" in provider:
        api_key = st.text_input(
            "Groq API Key", type="password", help="Get a free key at console.groq.com"
        )
        engine_provider = "groq"
    else:
        engine_provider = "demo"
        st.markdown(
            '<div class="demo-banner">'
            "<b>💡 Demo Mode Active</b> — Instant, offline CSIT responses without API keys. "
            "Upload a lecture PDF to see answers grounded in your notes.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 📚 CSIT Subject Context")
    subject = st.selectbox(
        "Current Subject",
        options=[
            "Data Structures & Algorithms",
            "C / C++ Programming",
            "Artificial Intelligence",
            "Database Management Systems (DBMS)",
            "Operating Systems",
            "Computer Networks",
            "Web Technologies",
            "General CSIT",
        ],
    )
    st.markdown(
        f'<div class="subject-chip">SUBJECT: {subject.upper()}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 📄 Upload Lecture Material")
    uploaded_file = st.file_uploader(
        "Upload PDF Notes / Syllabus",
        type=["pdf"],
        help="Upload lecture slides, chapters, or syllabus PDF.",
    )

    if uploaded_file is not None:
        if st.session_state.active_file_name != uploaded_file.name:
            with st.spinner("Parsing and chunking document text..."):
                file_bytes = uploaded_file.read()
                result = extract_text_from_pdf(file_bytes)
                if result["success"]:
                    st.session_state.extracted_doc = result
                    st.session_state.active_file_name = uploaded_file.name
                    st.session_state.chat_history = []
                    st.success(
                        f"Loaded: {uploaded_file.name} "
                        f"({result['total_pages']} pages)"
                    )
                else:
                    st.error(f"Error parsing PDF: {result.get('error')}")

    if st.session_state.extracted_doc:
        st.markdown("---")
        if st.button("🗑️ Clear Document & Chat", use_container_width=True):
            st.session_state.extracted_doc = None
            st.session_state.active_file_name = None
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("---")
    st.markdown("👨‍💻 **Developer:** [Samyog Sapkota](https://github.com/hola-mundo999)")
    st.caption("BSc CSIT · Prime College · PR Director, Prime IT Club")

# Initialize AI Engine
engine = AIEngine(provider=engine_provider, api_key=api_key)

# Main Header
st.markdown(
    f"""
<div class="main-header">
    <div class="header-badge">BSc CSIT STUDY SUITE · TRIBHUVAN UNIVERSITY</div>
    <h1 style="margin: 0; font-size: 32px; font-weight: 800;">🎓 AI CSIT Study & Lecture Assistant</h1>
    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 15px;">
        Upload your semester lecture notes or past board questions to chat, generate model exam papers, and review flashcards.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Document Stats Banner
if st.session_state.extracted_doc:
    doc = st.session_state.extracted_doc
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 11px; font-family: monospace; color: #818cf8;">ACTIVE DOCUMENT</div>
                <div style="font-size: 16px; font-weight: 700; color: white;">{st.session_state.active_file_name}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 11px; font-family: monospace; color: #c084fc;">TOTAL PAGES</div>
                <div style="font-size: 16px; font-weight: 700; color: white;">{doc['total_pages']} Pages</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 11px; font-family: monospace; color: #38bdf8;">TOTAL CHARACTERS</div>
                <div style="font-size: 16px; font-weight: 700; color: white;">{len(doc['full_text']):,} Characters</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info(
        "📌 **Get Started:** Upload a CSIT lecture PDF from the sidebar, or explore the features below using built-in CSIT demo context."
    )

# Feature Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["💬 Lecture Q&A Chat", "📝 Exam Prep & Model Questions", "⚡ Revision Flashcards", "📄 Document Text Preview"]
)

# ------------------------------------------------------------------ #
# TAB 1: Chatbot Q&A
# ------------------------------------------------------------------ #
with tab1:
    st.subheader("Ask Anything About Your Notes")
    st.caption("Answers are academically referenced and grounded in your course materials.")

    col_chat, col_actions = st.columns([5, 1])
    with col_actions:
        if st.button("🗑️ Clear Chat", use_container_width=True, disabled=not st.session_state.chat_history):
            st.session_state.chat_history = []
            st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input(
        "Ask a question (e.g., 'Explain QuickSort time complexity with code' or 'Summarize Chapter 2')..."
    )
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        context = st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else ""
        pages = st.session_state.extracted_doc["pages"] if st.session_state.extracted_doc else None

        with st.chat_message("assistant"):
            with st.spinner("Analyzing lecture notes..."):
                response = engine.answer_question(user_query, context, subject=subject, pages=pages)
                st.markdown(response)
                if pages and st.session_state.extracted_doc:
                    st.markdown(
                        f'<div class="source-note">Grounded in uploaded document: '
                        f"{st.session_state.active_file_name}</div>",
                        unsafe_allow_html=True,
                    )
                st.session_state.chat_history.append({"role": "assistant", "content": response})

    if st.session_state.chat_history:
        export_text = "\n\n".join(
            f"[{msg['role'].upper()}]\n{msg['content']}" for msg in st.session_state.chat_history
        )
        st.download_button(
            "📥 Export Chat History (.txt)",
            data=export_text,
            file_name="csit_chat_history.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ------------------------------------------------------------------ #
# TAB 2: Exam Prep
# ------------------------------------------------------------------ #
with tab2:
    st.subheader("TU-Style Practice Exam Sheet")
    st.caption("Generates practice exam questions, marking rubrics, and model answers from your notes.")

    col_q, col_btn = st.columns([3, 1])
    with col_q:
        num_q = st.slider("Number of Practice Questions", min_value=3, max_value=8, value=5)
    with col_btn:
        generate = st.button("🚀 Generate Practice Exam Paper", type="primary", use_container_width=True)

    if generate:
        context = st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else ""
        pages = st.session_state.extracted_doc["pages"] if st.session_state.extracted_doc else None
        with st.spinner(f"Generating {num_q} exam questions with model answers..."):
            exam_sheet = engine.generate_exam_prep(context, subject=subject, num_questions=num_q, pages=pages)
            st.markdown(exam_sheet)
            st.download_button(
                "📥 Download Exam Sheet (.txt)",
                data=exam_sheet,
                file_name=f"{subject.lower().replace(' ', '_')}_exam_prep.txt",
                mime="text/plain",
                use_container_width=True,
            )

# ------------------------------------------------------------------ #
# TAB 3: Flashcards & Revision
# ------------------------------------------------------------------ #
with tab3:
    st.subheader("Rapid Revision Flashcards & Formula Bank")
    st.caption("High-yield definitions, mathematical formulas, and algorithmic complexities from your notes.")

    if st.button("⚡ Extract Flashcards & Summary", type="primary", use_container_width=True):
        context = st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else ""
        pages = st.session_state.extracted_doc["pages"] if st.session_state.extracted_doc else None
        with st.spinner("Extracting high-yield concepts..."):
            summary_content = engine.generate_summary_flashcards(context, subject=subject, pages=pages)
            st.markdown(summary_content)

# ------------------------------------------------------------------ #
# TAB 4: Text Preview
# ------------------------------------------------------------------ #
with tab4:
    st.subheader("Raw Extracted Text")
    if st.session_state.extracted_doc:
        st.text_area(
            "Extracted PDF Content",
            value=st.session_state.extracted_doc["full_text"][:20000],
            height=400,
            disabled=True,
        )
        st.caption(
            f"{st.session_state.active_file_name} · "
            f"{st.session_state.extracted_doc['total_pages']} pages · "
            f"{len(st.session_state.extracted_doc['full_text']):,} characters extracted"
        )
    else:
        st.info("No document uploaded yet. Upload a PDF from the sidebar to inspect its raw text.")
