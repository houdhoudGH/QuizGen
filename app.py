import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQgenerator import combined_chain

load_dotenv()

with open("./Response.json", "r") as file:
    RESPONSE_JSON = json.load(file)

# ============================================================
#  PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="QuizGen",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
#  CUSTOM CSS — light, airy, modern
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif !important; }

    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background: linear-gradient(135deg, #faf5ff 0%, #f5f3ff 50%, #ede9fe 100%);
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero {
        background: linear-gradient(135deg, #a78bfa 0%, #c084fc 50%, #e879f9 100%);
        padding: 2.5rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(168, 85, 247, 0.25);
    }
    .hero h1 {
        color: white;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    .hero p {
        color: rgba(255,255,255,0.95);
        font-size: 1.15rem;
        margin-top: 0.6rem;
        font-weight: 500;
    }

    .section-title {
        color: #1f2937;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    .stat-pill {
        background: white;
        border: 1.5px solid #e9d5ff;
        color: #7c3aed;
        padding: 0.5rem 1.2rem;
        border-radius: 24px;
        display: inline-block;
        font-size: 0.9rem;
        margin: 0.2rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(168, 85, 247, 0.08);
    }

    .mcq-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.08);
        border: 1px solid #f3e8ff;
        transition: all 0.3s ease;
    }
    .mcq-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(168, 85, 247, 0.15);
    }
    .mcq-question {
        color: #1f2937;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px dashed #e9d5ff;
    }
    .mcq-number {
        display: inline-block;
        background: linear-gradient(135deg, #a78bfa, #c084fc);
        color: white;
        width: 32px;
        height: 32px;
        line-height: 32px;
        text-align: center;
        border-radius: 50%;
        margin-right: 0.6rem;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .mcq-choice {
        color: #374151;
        padding: 0.6rem 1rem;
        margin: 0.4rem 0;
        background: #faf5ff;
        border-radius: 10px;
        border-left: 3px solid #c084fc;
        font-size: 0.95rem;
    }
    .mcq-answer {
        background: linear-gradient(90deg, #10b981, #059669);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        margin-top: 1rem;
        font-weight: 600;
        display: inline-block;
        font-size: 0.95rem;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
    }

    .stButton > button {
        background: linear-gradient(135deg, #a78bfa, #c084fc) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(168, 85, 247, 0.45) !important;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.45) !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: white !important;
        color: #1f2937 !important;
        border: 1.5px solid #e9d5ff !important;
        border-radius: 12px !important;
    }

    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #c084fc;
        border-radius: 16px;
        padding: 1rem;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #a78bfa;
        background: #faf5ff;
    }

    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #f3e8ff;
    }
    [data-testid="stSidebar"] * { color: #374151 !important; }
    [data-testid="stSidebar"] h3 {
        color: #7c3aed !important;
        font-weight: 700 !important;
    }

    h1, h2, h3, h4 { color: #1f2937 !important; }

    .review-card {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        margin: 1rem 0;
        color: #78350f;
        box-shadow: 0 4px 15px rgba(251, 191, 36, 0.15);
        border-left: 4px solid #f59e0b;
    }
    .review-card h4 {
        color: #92400e !important;
        margin: 0 0 0.6rem 0;
        font-weight: 700;
    }
    .review-card p {
        color: #78350f !important;
        margin: 0;
        line-height: 1.6;
    }

    .success-banner {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        border-left: 4px solid #10b981;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: #065f46;
        font-weight: 600;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ✨ QuizGen")
    st.caption("*Made with 💜 by Gheffari Nour El Houda*")

    st.markdown("---")
    st.markdown("#### 🚀 How it works")
    st.markdown(
        """
        1. **Upload** a PDF or TXT file
        2. **Configure** subject, difficulty, count
        3. **Generate** — Llama 3.1 writes the quiz
        4. **Review** — a second AI pass checks quality
        5. **Download** as CSV
        """
    )

    st.markdown("---")
    st.markdown("#### 🛠️ Tech stack")
    st.markdown(
        """
        - 🧠 Llama 3.1 8B Instruct
        - 🦜 LangChain SequentialChain
        - 🤗 HuggingFace Inference
        - 🎨 Streamlit UI
        """
    )

    st.markdown("---")
    st.caption("v1.0 · 2026")

# ============================================================
#  HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <h1>✨ QuizGen</h1>
        <p>Turn any document into ready-to-use multiple-choice quizzes — powered by Llama 3.1 & LangChain</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  INPUT FORM
# ============================================================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown(
        '<div class="section-title">📂 1. Upload your document</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        " ",
        type=["pdf", "txt"],
        help="PDF or plain text. The AI will generate quiz questions from the content.",
        label_visibility="collapsed",
    )

with col_right:
    st.markdown(
        '<div class="section-title">⚙️ 2. Configure your quiz</div>',
        unsafe_allow_html=True,
    )
    subj_col, diff_col = st.columns(2)
    with subj_col:
        subject = st.text_input(
            "📚 Subject", placeholder="e.g. Machine Learning", max_chars=30
        )
    with diff_col:
        difficulty = st.selectbox(
            "🎯 Difficulty",
            options=["Simple", "Medium", "Hard"],
            index=1,
        )
    mcq_count = st.slider("📊 Number of MCQs", min_value=1, max_value=20, value=5)

st.markdown("<br>", unsafe_allow_html=True)

btn_left, btn_mid, btn_right = st.columns([1, 1, 1])
with btn_mid:
    submit_btn = st.button("✨ Generate MCQs", use_container_width=True)

# ============================================================
#  GENERATION
# ============================================================
quiz_df = None
review = None

if submit_btn:
    if uploaded_file is None or not subject:
        st.warning("⚠️ Please upload a file and fill in the subject.")
    else:
        with st.spinner("🧠 Llama 3.1 is generating your MCQs..."):
            try:
                text = read_file(uploaded_file)
                response = combined_chain(
                    {
                        "system_msg": "/no_think Answer very briefly and do not explain your reasoning.",
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "difficulty": difficulty,
                        "response_json": json.dumps(RESPONSE_JSON),
                    }
                )

                quiz = response.get("quiz")
                review = response.get("review")

                if quiz:
                    table_data = get_table_data(quiz)
                    if table_data:
                        quiz_df = pd.DataFrame(table_data)
                        quiz_df.index += 1
                    else:
                        st.error("❌ Could not extract table data.")
                else:
                    st.error("❌ No MCQ data returned.")

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("❌ Error generating MCQs. Check logs for details.")

# ============================================================
#  RESULTS
# ============================================================
if quiz_df is not None:
    st.markdown("---")

    st.markdown(
        f"""
        <div class="success-banner">
            ✅ Your quiz is ready! Generated {len(quiz_df)} questions.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="text-align: center; margin: 1.5rem 0;">
            <span class="stat-pill">📚 {subject}</span>
            <span class="stat-pill">🎯 {difficulty}</span>
            <span class="stat-pill">📊 {len(quiz_df)} questions</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📋 Your Quiz")

    for idx, row in quiz_df.iterrows():
        choices_html = ""
        for choice in row["Choices"].split(" | "):
            choices_html += f'<div class="mcq-choice">{choice}</div>'

        st.markdown(
            f"""
            <div class="mcq-card">
                <div class="mcq-question">
                    <span class="mcq-number">{idx}</span>{row["MCQ"]}
                </div>
                {choices_html}
                <div class="mcq-answer">✓ Correct answer: {row["Correct"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if review:
        st.markdown(
            f"""
            <div class="review-card">
                <h4>🔍 AI Quality Review</h4>
                <p>{review}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 💾 Export")
    csv_data = quiz_df.to_csv(index=False).encode("utf-8")
    dl_left, dl_mid, dl_right = st.columns([1, 1, 1])
    with dl_mid:
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name=f"quizgen_{subject.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
