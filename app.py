import streamlit as st
import os
from pdf_processor import extract_text_from_pdf
from ai_engine import AIEngine

# Set Streamlit Page Config
st.set_page_config(
    page_title="CSIT AI Study Assistant | Samyog Sapkota",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark tech aesthetic matching portfolio)
st.markdown("""
<style>
    /* Global styles */
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
</style>
""", unsafe_allow_html=True)

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
        options=["Demo Mode (No Key Needed)", "Google Gemini", "Groq (Llama-3.3-70B)"],
        index=0,
        help="Use Demo Mode for instant testing, or select Gemini / Groq for live AI with your free API key."
    )
    
    api_key = None
    if "Gemini" in provider:
        api_key = st.text_input("Enter Gemini API Key", type="password", help="Get free key at aistudio.google.com")
        engine_provider = "gemini"
    elif "Groq" in provider:
        api_key = st.text_input("Enter Groq API Key", type="password", help="Get free key at console.groq.com")
        engine_provider = "groq"
    else:
        engine_provider = "demo"
        st.info("💡 **Demo Mode Active**: Testing mock CSIT responses without requiring external API keys.")

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
            "General CSIT"
        ]
    )

    st.markdown("---")
    st.markdown("### 📄 Upload Lecture Material")
    uploaded_file = st.file_uploader(
        "Upload PDF Notes / Syllabus",
        type=["pdf"],
        help="Upload lecture slides, chapters, or syllabus PDF."
    )

    if uploaded_file is not None:
        if st.session_state.active_file_name != uploaded_file.name:
            with st.spinner("Parsing and chunking document text..."):
                file_bytes = uploaded_file.read()
                result = extract_text_from_pdf(file_bytes)
                if result["success"]:
                    st.session_state.extracted_doc = result
                    st.session_state.active_file_name = uploaded_file.name
                    st.success(f"Loaded: {uploaded_file.name} ({result['total_pages']} pages)")
                else:
                    st.error(f"Error parsing PDF: {result.get('error')}")

    st.markdown("---")
    st.markdown("👨‍💻 **Developer:** [Samyog Sapkota](https://github.com/hola-mundo999)")
    st.caption("BSc CSIT · Prime College · PR Director, Prime IT Club")

# Initialize AI Engine
engine = AIEngine(provider=engine_provider, api_key=api_key)

# Main Header
st.markdown(f"""
<div class="main-header">
    <div class="header-badge">BSc CSIT STUDY SUITE · TRIBHUVAN UNIVERSITY</div>
    <h1 style="margin: 0; font-size: 32px; font-weight: 800;">🎓 AI CSIT Study & Lecture Assistant</h1>
    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 15px;">
        Upload your semester lecture notes or past board questions to chat, generate model exam papers, and review flashcards.
    </p>
</div>
""", unsafe_allow_html=True)

# Document Stats Banner
if st.session_state.extracted_doc:
    doc = st.session_state.extracted_doc
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; font-family: monospace; color: #818cf8;">ACTIVE DOCUMENT</div>
            <div style="font-size: 16px; font-weight: 700; color: white;">{st.session_state.active_file_name}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; font-family: monospace; color: #c084fc;">TOTAL PAGES</div>
            <div style="font-size: 16px; font-weight: 700; color: white;">{doc['total_pages']} Pages</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; font-family: monospace; color: #38bdf8;">TOTAL CHARACTERS</div>
            <div style="font-size: 16px; font-weight: 700; color: white;">{len(doc['full_text']):,} Characters</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("📌 **Get Started:** Upload a CSIT lecture PDF from the sidebar, or explore the features below using built-in CSIT demo context.")

# Feature Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Lecture Q&A Chat",
    "📝 Exam Prep & Model Questions",
    "⚡ Revision Flashcards",
    "📄 Document Text Preview"
])

# TAB 1: Chatbot Q&A
with tab1:
    st.subheader("Ask Anything About Your Notes")
    st.caption("Answers are academically referenced and grounded in your course materials.")

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_query = st.chat_input("Ask a question (e.g., 'Explain QuickSort time complexity with code' or 'Summarize Chapter 2')...")
    if user_query:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Get context
        context = st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else "Sample Context: BSc CSIT Algorithms & Data Structures."

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing lecture notes..."):
                response = engine.answer_question(user_query, context, subject=subject)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

# TAB 2: Exam Prep
with tab2:
    st.subheader("TU-Style Practice Exam Sheet")
    st.caption("Generates 5 high-yield exam questions, marking rubric, and model answers from your notes.")
    
    num_q = st.slider("Number of Practice Questions", min_value=3, max_value=8, value=5)
    if st.button("🚀 Generate Practice Exam Paper", type="primary"):
        context = st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else "General Data Structures, Trees, Graph algorithms, and Sorting."
        with st.spinner(f"Generating {num_q} exam questions with model answers..."):
            exam_sheet = engine.generate_exam_prep(context, subject=subject, num_questions=num_q)
            st.markdown(exam_sheet)
            st.download_button(
                "📥 Download Exam Sheet (.txt)",
                data=exam_sheet,
                file_name=f"{subject.lower().replace(' ', '_')}_exam_prep.txt",
                mime="text/plain"
            )

# TAB 3: Flashcards & Revision
with tab3:
    st.subheader("Rapid Revision Flashcards & Formula Bank")
    st.caption("Instant cheat-sheet covering key definitions, mathematical formulas, and algorithmic complexities.")

    if st.button("⚡ Extract Flashcards & Summary"):
        context = st.session_state.extracted_doc["full_text"] if st.session_state.extracted_doc else "General Data Structures, Memory management, Big-O complexities."
        with st.spinner("Extracting high-yield concepts..."):
            summary_content = engine.generate_summary_flashcards(context, subject=subject)
            st.markdown(summary_content)

# TAB 4: Text Preview
with tab4:
    st.subheader("Raw Extracted Text")
    if st.session_state.extracted_doc:
        st.text_area(
            "Extracted PDF Content",
            value=st.session_state.extracted_doc["full_text"][:20000],
            height=400,
            disabled=True
        )
    else:
        st.write("No document uploaded yet. Upload a PDF from the sidebar to inspect its raw text.")
