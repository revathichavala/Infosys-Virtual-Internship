"""
AI Smart Quiz - Adaptive AI-Based Quiz Generator
Streamlit Application
"""

import streamlit as st
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from quiz_engine import QuizEngine
from question_generator import QuestionGenerator
from analytics import QuizAnalytics
from utils import extract_text_from_file, fetch_article_content

# Page configuration
st.set_page_config(
    page_title="AI Smart Quiz - AI Quiz Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    /* Main Container - Bigger layout */
    .main .block-container {
        padding: 3rem 4rem;
        max-width: 1400px;
    }
    
    /* Main Header - HUGE with brain symbol */
    .main-header {
        font-size: 5.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: -0.02em;
        animation: fadeInDown 0.8s ease-out;
        text-shadow: 0 2px 10px rgba(102, 126, 234, 0.2);
        line-height: 1.2;
    }
    
    .sub-header {
        text-align: center;
        color: #0f172a;
        font-size: 1.8rem;
        margin-bottom: 3.5rem;
        font-weight: 700;
        animation: fadeInUp 0.8s ease-out 0.2s both;
        line-height: 1.6;
    }
    
    /* Hero section styling */
    .hero-section {
        text-align: center;
        padding: 3rem 0;
        margin-bottom: 2rem;
    }
    
    .brain-icon {
        font-size: 8rem;
        display: block;
        margin-bottom: 1.5rem;
        animation: pulse 2s infinite;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* Cards - Bigger with more padding */
    .glass-card {
        background: #ffffff;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 1.5rem;
        border: 2px solid #e2e8f0;
        box-shadow: 0 12px 45px rgba(0, 0, 0, 0.12), 0 6px 15px rgba(0, 0, 0, 0.06);
        padding: 2.5rem;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.18), 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .question-card {
        background: #ffffff;
        padding: 3rem;
        border-radius: 1.75rem;
        border: 3px solid #e2e8f0;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
        position: relative;
        overflow: hidden;
    }
    
    .question-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    }
    
    /* Metric Cards - Bigger */
    .metric-card {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 12px 45px rgba(0, 0, 0, 0.12);
        text-align: center;
        border: 3px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 70px rgba(102, 126, 234, 0.25);
    }
    
    .metric-card h3 {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    
    .score-display {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    /* Difficulty Badges - Bold and visible */
    .difficulty-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1.2rem;
        border-radius: 2rem;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.02em;
        border: 2px solid;
    }
    
    .difficulty-easy { 
        background: #d1fae5;
        color: #065f46;
        border-color: #10b981;
    }
    .difficulty-medium { 
        background: #fef3c7;
        color: #92400e;
        border-color: #f59e0b;
    }
    .difficulty-hard { 
        background: #fee2e2;
        color: #991b1b;
        border-color: #ef4444;
    }
    
    /* Progress Bar Enhancement */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        border-radius: 1rem;
        height: 12px !important;
    }
    
    .stProgress > div > div {
        background: #d1d5db;
    }
    
    /* Back to Home Button - Blue gradient */
    .back-home-btn button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.75rem !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .back-home-btn button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
    }
    
    /* Clear History Button - Red gradient */
    .clear-history-btn button {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.75rem !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .clear-history-btn button:hover {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5) !important;
    }
    
    /* URL and Content Input Styling - Complete boxes */
    [data-testid="column"]:first-child [data-testid="stTextInput"] input {
        background: #f8fafc !important;
        border: 2px solid #667eea !important;
        border-radius: 0.75rem !important;
        padding: 0.875rem 1rem !important;
        font-size: 1rem !important;
        color: #0f172a !important;
        font-weight: 500 !important;
        margin-top: -0.5rem !important;
    }
    
    [data-testid="column"]:first-child [data-testid="stTextInput"] input:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.25) !important;
    }
    
    [data-testid="column"]:last-child [data-testid="stTextArea"] textarea {
        background: #f8fafc !important;
        border: 2px solid #10b981 !important;
        border-radius: 0.75rem !important;
        padding: 0.875rem 1rem !important;
        font-size: 1rem !important;
        color: #0f172a !important;
        font-weight: 500 !important;
        margin-top: -0.5rem !important;
    }
    
    [data-testid="column"]:last-child [data-testid="stTextArea"] textarea:focus {
        border-color: #059669 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25) !important;
    }

    /* Button Enhancements - Much bigger */
    .stButton > button {
        border-radius: 1rem !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        padding: 1.1rem 2.25rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        min-height: 60px !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.65) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #667eea !important;
        border: 3px solid #667eea !important;
        font-weight: 800 !important;
    }
    
    /* File Uploader - Much bigger */
    .stFileUploader > div {
        border-radius: 1.25rem !important;
        border: 4px dashed #64748b !important;
        padding: 3.5rem !important;
        background: #ffffff !important;
        transition: all 0.3s ease !important;
        min-height: 180px !important;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea !important;
        background: #f5f3ff !important;
    }
    
    /* Text Input & Text Area - Much bigger */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 1rem !important;
        border: 3px solid #94a3b8 !important;
        padding: 1.25rem !important;
        font-size: 1.15rem !important;
        background: #ffffff !important;
        color: #000000 !important;
        transition: all 0.3s ease !important;
        min-height: 55px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.25) !important;
    }
    
    /* Radio Buttons - HUGE and DARK */
    .stRadio > div {
        gap: 1.75rem !important;
    }
    
    .stRadio > div > label {
        background: #ffffff !important;
        padding: 2rem 2.5rem !important;
        border-radius: 1.25rem !important;
        border: 3px solid #1e293b !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        font-size: 2rem !important;
        color: #000000 !important;
        font-weight: 800 !important;
        min-height: 90px !important;
    }
    
    .stRadio > div > label span,
    .stRadio > div > label p,
    .stRadio > div > label div {
        font-size: 1.6rem !important;
        color: #000000 !important;
        font-weight: 700 !important;
        line-height: 1.5 !important;
    }
    
    .stRadio > div > label:hover {
        border-color: #667eea !important;
        background: #f5f3ff !important;
        transform: translateX(8px) !important;
    }
    
    .stRadio > div > label[data-checked="true"] {
        border-color: #667eea !important;
        background: #ede9fe !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stRadio > div > label:hover {
        border-color: #667eea !important;
        background: #f5f3ff !important;
    }
    
    .stRadio > div > label[data-checked="true"] {
        border-color: #667eea !important;
        background: #ede9fe !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Radio option text specifically */
    .stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 1.6rem !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar Styling - Clear and visible */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Expander - More visible */
    .streamlit-expanderHeader {
        border-radius: 0.75rem !important;
        background: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: 2px solid #e2e8f0 !important;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    /* Success/Error/Warning Messages - Larger text */
    .stSuccess {
        background: #d1fae5 !important;
        border: 2px solid #10b981 !important;
        border-radius: 0.75rem !important;
        padding: 1.25rem 1.5rem !important;
        font-size: 1.05rem !important;
    }
    
    .stError {
        background: #fee2e2 !important;
        border: 2px solid #ef4444 !important;
        border-radius: 0.75rem !important;
        padding: 1.25rem 1.5rem !important;
        font-size: 1.05rem !important;
    }
    
    .stWarning {
        background: #fef3c7 !important;
        border: 2px solid #f59e0b !important;
        border-radius: 0.75rem !important;
        padding: 1.25rem 1.5rem !important;
        font-size: 1.05rem !important;
    }
    
    /* Multiselect - Clearer */
    .stMultiSelect > div > div {
        border-radius: 0.75rem !important;
        border: 2px solid #cbd5e1 !important;
        background: #ffffff !important;
    }
    
    /* Section Headers - Larger and bolder */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.4rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1.5rem 0 1rem 0;
    }
    
    .section-header-icon {
        font-size: 1.6rem;
    }
    
    /* Dividers */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent) !important;
        margin: 2rem 0 !important;
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Timer Styles - Much bigger */
    .timer-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
    }
    
    .timer-display {
        font-size: 4rem;
        font-weight: 800;
        font-family: 'Courier New', monospace;
        padding: 1.25rem 2.5rem;
        border-radius: 1.25rem;
        background: #0f172a;
        color: #10b981;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        border: 4px solid #10b981;
        letter-spacing: 0.08em;
    }
    
    .timer-warning {
        color: #f59e0b !important;
        border-color: #f59e0b !important;
    }
    
    .timer-danger {
        color: #ef4444 !important;
        border-color: #ef4444 !important;
        animation: pulse 0.5s infinite;
    }
    
    /* Key Concepts Card - Bigger */
    .concepts-card {
        background: #ffffff;
        border: 3px solid #667eea;
        border-radius: 1.5rem;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 12px 45px rgba(102, 126, 234, 0.18);
    }
    
    .concept-tag {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.85rem 1.5rem;
        border-radius: 2.5rem;
        margin: 0.5rem;
        font-size: 1.1rem;
        font-weight: 700;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.35);
    }
    
    /* History Card - Bigger */
    .history-card {
        background: #ffffff;
        border: 3px solid #e2e8f0;
        border-radius: 1.5rem;
        padding: 2rem;
        margin-bottom: 1.75rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .history-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        border-color: #667eea;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    /* Labels and text - Larger and DARKER */
    .stMarkdown p {
        font-size: 1.1rem;
        color: #0f172a;
        line-height: 1.7;
        font-weight: 500;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #000000;
        font-weight: 800;
    }
    
    /* All labels darker */
    label, .stMarkdown label {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
    }
    
    /* Selectbox text */
    .stSelectbox label, .stMultiSelect label, .stSlider label {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
    }
    
    /* Option text in quiz - HUGE and DARK */
    .stRadio label span {
        font-size: 1.8rem !important;
        color: #000000 !important;
        font-weight: 800 !important;
    }
    
    /* Radio button labels */
    .stRadio > label {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }
    
    /* Radio button circle */
    .stRadio input[type="radio"] {
        width: 28px !important;
        height: 28px !important;
    }
    
    /* Checkbox text */
    .stCheckbox label span {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
    }
    
    /* Input placeholder - darker */
    input::placeholder, textarea::placeholder {
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 1.15rem !important;
    }
    
    /* Text inputs - bigger */
    .stTextInput input, .stTextArea textarea {
        font-size: 1.3rem !important;
        padding: 1rem 1.25rem !important;
        color: #000000 !important;
    }
    
    /* File uploader text */
    .stFileUploader label {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }
    
    /* Strong/Bold text */
    strong, b {
        color: #000000 !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'quiz_engine' not in st.session_state:
        st.session_state.quiz_engine = QuizEngine()
    if 'question_generator' not in st.session_state:
        st.session_state.question_generator = QuestionGenerator()
    if 'analytics' not in st.session_state:
        st.session_state.analytics = QuizAnalytics()
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 'upload'  # upload, concepts, quiz, results, history
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_question_idx' not in st.session_state:
        st.session_state.current_question_idx = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'current_difficulty' not in st.session_state:
        st.session_state.current_difficulty = 'medium'
    if 'quiz_start_time' not in st.session_state:
        st.session_state.quiz_start_time = None
    if 'question_start_time' not in st.session_state:
        st.session_state.question_start_time = None
    if 'uploaded_content' not in st.session_state:
        st.session_state.uploaded_content = None
    if 'key_concepts' not in st.session_state:
        st.session_state.key_concepts = []
    if 'timer_duration' not in st.session_state:
        st.session_state.timer_duration = 30  # seconds per question
    if 'show_timer' not in st.session_state:
        st.session_state.show_timer = True

init_session_state()

def reset_quiz():
    st.session_state.current_stage = 'upload'
    st.session_state.questions = []
    st.session_state.current_question_idx = 0
    st.session_state.user_answers = []
    st.session_state.current_difficulty = 'medium'
    st.session_state.quiz_start_time = None
    st.session_state.question_start_time = None
    st.session_state.uploaded_content = None
    st.session_state.key_concepts = []

def render_timer():
    """Render countdown timer for current question."""
    if not st.session_state.show_timer or st.session_state.question_start_time is None:
        return
    
    elapsed = time.time() - st.session_state.question_start_time
    remaining = max(0, st.session_state.timer_duration - elapsed)
    
    minutes = int(remaining // 60)
    seconds = int(remaining % 60)
    
    # Determine timer class based on remaining time
    if remaining <= 5:
        timer_class = "timer-danger"
    elif remaining <= 10:
        timer_class = "timer-warning"
    else:
        timer_class = ""
    
    st.markdown(f"""
    <div class="timer-container">
        <div class="timer-display {timer_class}">
            ⏱️ {minutes:02d}:{seconds:02d}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_upload_stage():
    st.markdown('<h1 class="main-header">🧠 AI Smart Quiz</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your study materials into interactive quizzes powered by AI</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Upload Section
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2.5rem;">
            <span style="font-size: 5rem;">📚</span>
            <h3 style="margin-top: 1rem; margin-bottom: 0.75rem; color: #000000; font-size: 2.2rem; font-weight: 800;">Upload Your Study Material</h3>
            <p style="color: #1e293b; margin: 0; font-size: 1.4rem; font-weight: 600;">Drag and drop or browse to upload</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF or Text file",
            type=['pdf', 'txt'],
            help="Upload your study material to generate quiz questions",
            label_visibility="collapsed"
        )
        
        # Divider with "or"
        st.markdown("""
        <div style="display: flex; align-items: center; margin: 2.5rem 0;">
            <div style="flex: 1; height: 3px; background: linear-gradient(90deg, transparent, #667eea);"></div>
            <span style="padding: 0 1.5rem; color: #000000; font-weight: 800; font-size: 1.2rem;">OR</span>
            <div style="flex: 1; height: 3px; background: linear-gradient(90deg, #667eea, transparent);"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Two columns for URL and Content boxes
        col_url, col_content = st.columns(2)
        
        with col_url:
            # URL Input Box - Complete unified box
            st.markdown("""
            <div style="background: #ffffff; border: 3px solid #667eea; border-radius: 1.25rem 1.25rem 0 0; padding: 1.5rem 1.5rem 1rem 1.5rem; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15); margin-bottom: 0; min-height: 80px;">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 2rem;">🔗</span>
                    <h4 style="margin: 0; color: #000000; font-size: 1.3rem; font-weight: 800;">Article URL</h4>
                </div>
                <p style="color: #1e293b; font-size: 1rem; margin-bottom: 0; font-weight: 500;">Paste a link to fetch content from any online article</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Style the input to connect with box above
            st.markdown("""
            <style>
            .url-box-input input {
                border: 3px solid #667eea !important;
                border-top: none !important;
                border-radius: 0 0 1.25rem 1.25rem !important;
                margin-top: -3px !important;
                padding: 1rem 1.25rem !important;
                font-size: 1.1rem !important;
                background: #f8fafc !important;
                color: #0f172a !important;
                height: 50px !important;
            }
            .url-box-input input:focus {
                border-color: #4f46e5 !important;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
            }
            </style>
            <div class="url-box-input">
            """, unsafe_allow_html=True)
            
            article_url = st.text_input(
                "Article URL",
                placeholder="https://example.com/article",
                help="Paste a URL to fetch content from an online article",
                label_visibility="collapsed"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_content:
            # Paste Content Box - Complete unified box
            st.markdown("""
            <div style="background: #ffffff; border: 3px solid #10b981; border-radius: 1.25rem 1.25rem 0 0; padding: 1.5rem 1.5rem 1rem 1.5rem; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.15); margin-bottom: 0; min-height: 80px;">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 2rem;">📝</span>
                    <h4 style="margin: 0; color: #000000; font-size: 1.3rem; font-weight: 800;">Paste Content</h4>
                </div>
                <p style="color: #1e293b; font-size: 1rem; margin-bottom: 0; font-weight: 500;">Or paste your notes, chapter content, or study material</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Style the textarea to connect with box above
            st.markdown("""
            <style>
            .content-box-input textarea {
                border: 3px solid #10b981 !important;
                border-top: none !important;
                border-radius: 0 0 1.25rem 1.25rem !important;
                margin-top: -3px !important;
                padding: 1rem 1.25rem !important;
                font-size: 1.1rem !important;
                background: #f8fafc !important;
                color: #0f172a !important;
                min-height: 50px !important;
                height: 50px !important;
                resize: none !important;
            }
            .content-box-input textarea:focus {
                border-color: #059669 !important;
                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2) !important;
            }
            </style>
            <div class="content-box-input">
            """, unsafe_allow_html=True)
            
            pasted_text = st.text_area(
                "Paste your study content here",
                height=50,
                placeholder="Paste your notes, chapter content, or any study material here...",
                label_visibility="collapsed"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Quiz Settings Section
        st.markdown("""
        <div style="margin-top: 3rem; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 2.5rem;">⚙️</span>
                <h3 style="margin: 0; color: #000000; font-size: 1.8rem; font-weight: 800;">Quiz Settings</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**📊 Number of Questions**")
            num_questions = st.slider("Number of Questions", 5, 20, 10, label_visibility="collapsed")
        with col_b:
            st.markdown("**🎯 Question Types**")
            question_types = st.multiselect(
                "Question Types",
                ["MCQ", "True/False", "Fill in the Blank", "Short Answer"],
                default=["MCQ", "True/False"],
                label_visibility="collapsed"
            )
        
        # Timer settings
        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown("**⏱️ Timer per Question (seconds)**")
            timer_duration = st.slider("Timer Duration", 15, 120, 30, label_visibility="collapsed")
        with col_d:
            st.markdown("**🔔 Enable Timer**")
            show_timer = st.checkbox("Show countdown timer", value=True)
        
        st.session_state.timer_duration = timer_duration
        st.session_state.show_timer = show_timer
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # Generate button with new symbol
        if st.button("✨ Generate Quiz", use_container_width=True, type="primary"):
            content = None
            
            if uploaded_file:
                with st.spinner("📄 Reading your file... This may take a moment for large documents."):
                    content = extract_text_from_file(uploaded_file)
                    if content and content.startswith("Error"):
                        st.error(f"📁 {content}")
                        content = None
            elif article_url.strip():
                with st.spinner("🌐 Fetching article from the web... Please wait."):
                    content = fetch_article_content(article_url.strip())
                    if content and content.startswith("Error"):
                        st.error(f"🔗 {content}")
                        content = None
            elif pasted_text.strip():
                content = pasted_text.strip()
            
            if content:
                st.session_state.uploaded_content = content
                
                # Extract key concepts first
                with st.spinner("🔍 AI is analyzing your content and extracting key concepts..."):
                    concepts = st.session_state.question_generator.extract_key_concepts(content)
                    st.session_state.key_concepts = concepts
                
                with st.spinner("🤖 AI is crafting personalized quiz questions just for you... This usually takes 10-20 seconds."):
                    questions = st.session_state.question_generator.generate_questions(
                        content=content,
                        num_questions=num_questions,
                        question_types=question_types
                    )
                
                if questions:
                    st.session_state.questions = questions
                    st.session_state.current_stage = 'concepts'
                    st.balloons()  # Celebrate success!
                    st.rerun()
                else:
                    st.error("😕 Oops! We couldn't generate questions from this content. Try adding more text or using different material.")
            else:
                st.warning("👆 Please upload a file, enter a URL, or paste some text to get started!")

def render_concepts_stage():
    """Display extracted key concepts before starting quiz."""
    st.markdown('<h1 class="main-header">🔑 Key Concepts Identified</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI has identified these main concepts from your material</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Display key concepts
        if st.session_state.key_concepts:
            st.markdown("""
            <div class="concepts-card">
                <h4 style="margin: 0 0 1rem 0; color: #0369a1;">📚 Main Topics & Concepts</h4>
            """, unsafe_allow_html=True)
            
            concepts_html = ""
            for concept in st.session_state.key_concepts:
                concepts_html += f'<span class="concept-tag">{concept}</span>'
            
            st.markdown(f"""
                <div style="line-height: 2.5;">
                    {concepts_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No specific concepts were extracted. The quiz will cover general content.")
        
        # Quiz summary
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="margin: 0 0 1rem 0; color: #1e293b;">📋 Quiz Summary</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <span style="color: #64748b;">Questions:</span>
                    <strong style="color: #667eea;"> {len(st.session_state.questions)}</strong>
                </div>
                <div>
                    <span style="color: #64748b;">Timer:</span>
                    <strong style="color: #667eea;"> {st.session_state.timer_duration}s per question</strong>
                </div>
                <div>
                    <span style="color: #64748b;">Starting Difficulty:</span>
                    <strong style="color: #f59e0b;"> Medium</strong>
                </div>
                <div>
                    <span style="color: #64748b;">Adaptive:</span>
                    <strong style="color: #10b981;"> Enabled</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("⬅️ Go Back", use_container_width=True):
                reset_quiz()
                st.rerun()
        with col_b:
            if st.button("🚀 Start Quiz", use_container_width=True, type="primary"):
                st.session_state.current_stage = 'quiz'
                st.session_state.quiz_start_time = time.time()
                st.session_state.question_start_time = time.time()
                st.rerun()

def render_quiz_stage():
    questions = st.session_state.questions
    current_idx = st.session_state.current_question_idx
    
    if current_idx >= len(questions):
        st.session_state.current_stage = 'results'
        st.rerun()
        return
    
    current_question = questions[current_idx]
    
    # Render countdown timer
    render_timer()
    
    # Progress section with animation
    progress = (current_idx + 1) / len(questions)
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <span style="color: #000000; font-weight: 800; font-size: 1.5rem;">Question {current_idx + 1} of {len(questions)}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(progress)
    
    # Stats row with better styling
    correct_count = sum(1 for a in st.session_state.user_answers if a['is_correct'])
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.75rem; text-align: center;">
            <div style="font-size: 1.1rem; color: #000000; text-transform: uppercase; font-weight: 800;">Progress</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #667eea;">{current_idx + 1}/{len(questions)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.75rem; text-align: center;">
            <div style="font-size: 1.1rem; color: #000000; text-transform: uppercase; font-weight: 800;">Correct</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #059669;">✓ {correct_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        difficulty_styles = {
            'easy': ('🟢', '#047857', '#d1fae5'),
            'medium': ('🟡', '#b45309', '#fef3c7'), 
            'hard': ('🔴', '#b91c1c', '#fee2e2')
        }
        icon, color, bg = difficulty_styles.get(st.session_state.current_difficulty, ('🟡', '#b45309', '#fef3c7'))
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.75rem; text-align: center;">
            <div style="font-size: 1.1rem; color: #000000; text-transform: uppercase; font-weight: 800;">Difficulty</div>
            <div style="font-size: 1.75rem; font-weight: 800; color: {color};">{icon} {st.session_state.current_difficulty.title()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        topic = current_question.get('topic', 'General')[:12]
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.75rem; text-align: center;">
            <div style="font-size: 1.1rem; color: #000000; text-transform: uppercase; font-weight: 800;">Topic</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #5b21b6;">📖 {topic}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Question card with enhanced styling
    difficulty_badge = {
        'easy': '<span class="difficulty-badge difficulty-easy">🟢 Easy</span>',
        'medium': '<span class="difficulty-badge difficulty-medium">🟡 Medium</span>',
        'hard': '<span class="difficulty-badge difficulty-hard">🔴 Hard</span>'
    }
    
    st.markdown(f"""
    <div class="question-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <span style="font-size: 1.6rem; color: #000000; font-weight: 800; letter-spacing: 0.05em;">QUESTION {current_idx + 1}</span>
            {difficulty_badge.get(current_question.get('difficulty', 'medium'), difficulty_badge['medium'])}
        </div>
        <h2 style="color: #000000; font-size: 2.5rem; font-weight: 700; line-height: 1.6; margin: 0;">{current_question['question']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    question_type = current_question.get('type', 'mcq')
    
    # Handle different question types
    if question_type == 'mcq':
        options = [current_question['answer']] + current_question.get('distractors', [])
        import random
        if 'shuffled_options' not in st.session_state or st.session_state.get('last_question_idx') != current_idx:
            random.shuffle(options)
            st.session_state.shuffled_options = options
            st.session_state.last_question_idx = current_idx
        
        st.markdown("<p style='font-size: 1.5rem; font-weight: 700; color: #000000; margin-bottom: 0.5rem;'>Select your answer:</p>", unsafe_allow_html=True)
        selected = st.radio(
            "Select your answer:",
            st.session_state.shuffled_options,
            index=None,
            key=f"q_{current_idx}",
            label_visibility="collapsed"
        )
        
        if st.button("✅ Submit Answer", type="primary", use_container_width=True, disabled=(selected is None)):
            if selected is not None:
                submit_answer(selected, current_question)
            else:
                st.warning("Please select an answer first.")
            
    elif question_type == 'true_false':
        st.markdown("<p style='font-size: 1.5rem; font-weight: 700; color: #000000; margin-bottom: 0.5rem;'>Select your answer:</p>", unsafe_allow_html=True)
        selected = st.radio(
            "Select your answer:",
            ["True", "False"],
            index=None,
            key=f"q_{current_idx}",
            label_visibility="collapsed"
        )
        
        if st.button("✅ Submit Answer", type="primary", use_container_width=True, disabled=(selected is None)):
            if selected is not None:
                submit_answer(selected, current_question)
            else:
                st.warning("Please select an answer first.")
    
    elif question_type == 'fill_blank':
        st.markdown("<p style='font-size: 1.5rem; font-weight: 700; color: #000000; margin-bottom: 1rem;'>Fill in the blank:</p>", unsafe_allow_html=True)
        answer = st.text_input("Your answer:", key=f"q_{current_idx}", placeholder="Type the missing word(s)...")
        
        if st.button("✅ Submit Answer", type="primary", use_container_width=True, disabled=(not answer.strip())):
            if answer.strip():
                submit_answer(answer, current_question)
            else:
                st.warning("Please fill in the blank first.")
            
    elif question_type == 'short_answer':
        answer = st.text_input("Your answer:", key=f"q_{current_idx}")
        
        if st.button("✅ Submit Answer", type="primary", use_container_width=True, disabled=(not answer.strip())):
            if answer.strip():
                submit_answer(answer, current_question)
            else:
                st.warning("Please enter an answer first.")

def submit_answer(user_answer, question):
    response_time = time.time() - st.session_state.question_start_time
    
    is_correct = st.session_state.quiz_engine.check_answer(
        user_answer=user_answer,
        correct_answer=question['answer'],
        question_type=question.get('type', 'mcq')
    )
    
    # Record answer
    st.session_state.user_answers.append({
        'question': question['question'],
        'user_answer': user_answer,
        'correct_answer': question['answer'],
        'is_correct': is_correct,
        'difficulty': question.get('difficulty', 'medium'),
        'topic': question.get('topic', 'General'),
        'response_time': response_time
    })
    
    # Update difficulty based on performance
    st.session_state.current_difficulty = st.session_state.quiz_engine.get_next_difficulty(
        current_difficulty=st.session_state.current_difficulty,
        is_correct=is_correct,
        recent_answers=st.session_state.user_answers[-5:]
    )
    
    # Show feedback
    if is_correct:
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Not quite! The correct answer was: **{question['answer']}**. Keep going, you're learning!")
    
    time.sleep(1)
    
    # Move to next question
    st.session_state.current_question_idx += 1
    st.session_state.question_start_time = time.time()
    st.rerun()

def render_results_stage():
    results = st.session_state.analytics.calculate_results(st.session_state.user_answers)
    accuracy = results['accuracy']
    
    # Celebration based on performance
    if accuracy >= 80:
        st.balloons()
    
    # Dynamic header based on performance
    if accuracy >= 90:
        header_emoji = "🏆"
        header_text = "Outstanding Performance!"
        sub_text = "You absolutely crushed it! You're ready for anything!"
    elif accuracy >= 70:
        header_emoji = "🌟"
        header_text = "Great Job!"
        sub_text = "You're doing really well. Keep up the great work!"
    elif accuracy >= 50:
        header_emoji = "💪"
        header_text = "Good Effort!"
        sub_text = "You're on the right track. A little more practice and you'll master this!"
    else:
        header_emoji = "📚"
        header_text = "Keep Learning!"
        sub_text = "Every attempt makes you better. Review the material and try again!"
    
    st.markdown(f'''
    <div class="hero-section">
        <h1 class="main-header">{header_emoji} {header_text}</h1>
        <p class="sub-header">{sub_text}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Main score cards with enhanced styling
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 YOUR SCORE</h3>
            <p class="score-display">{results['correct']}/{results['total']}</p>
            <p style="color: #000000; margin-top: 1rem; font-weight: 800; font-size: 1.4rem;">{results['accuracy']}% Accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Performance rating based on accuracy
        accuracy = results['accuracy']
        if accuracy >= 90:
            rating = "🏆 Excellent!"
            rating_color = "#047857"
        elif accuracy >= 70:
            rating = "⭐ Great Job!"
            rating_color = "#4f46e5"
        elif accuracy >= 50:
            rating = "👍 Good Effort"
            rating_color = "#b45309"
        else:
            rating = "📚 Keep Learning"
            rating_color = "#b91c1c"
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏅 PERFORMANCE</h3>
            <p class="score-display" style="font-size: 2.25rem;">{rating}</p>
            <p style="color: {rating_color}; margin-top: 1rem; font-weight: 800; font-size: 1.4rem;">{accuracy}% Correct</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_time = results.get('avg_response_time', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ AVG RESPONSE TIME</h3>
            <p class="score-display">{avg_time:.1f}s</p>
            <p style="color: #000000; margin-top: 1rem; font-weight: 800; font-size: 1.4rem;">Per Question</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Charts section with better headers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <span style="font-size: 2.5rem;">📈</span>
            <h3 style="margin: 0; color: #000000; font-weight: 800; font-size: 1.6rem;">Accuracy Breakdown</h3>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.analytics.plot_accuracy_pie(results)
    
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <span style="font-size: 2.5rem;">📊</span>
            <h3 style="margin: 0; color: #000000; font-weight: 800; font-size: 1.6rem;">Topic Performance</h3>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.analytics.plot_topic_performance(st.session_state.user_answers)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Difficulty progression with better header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
        <span style="font-size: 2.5rem;">📉</span>
        <h3 style="margin: 0; color: #000000; font-weight: 800; font-size: 1.6rem;">Difficulty Progression</h3>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.analytics.plot_difficulty_progression(st.session_state.user_answers)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Recommendations with enhanced styling
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
        <span style="font-size: 1.5rem;">💡</span>
        <h3 style="margin: 0; color: #1e293b;">Personalized Recommendations</h3>
    </div>
    """, unsafe_allow_html=True)
    recommendations = st.session_state.analytics.get_recommendations(st.session_state.user_answers)
    
    for rec in recommendations:
        if rec['type'] == 'strength':
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #d1fae5 0%, #a7f3d0 100%); padding: 1rem 1.25rem; border-radius: 0.75rem; margin-bottom: 0.75rem; border-left: 4px solid #10b981;">
                <strong style="color: #065f46;">✅ Strength:</strong> <span style="color: #047857;">{rec['message']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #fef3c7 0%, #fde68a 100%); padding: 1rem 1.25rem; border-radius: 0.75rem; margin-bottom: 0.75rem; border-left: 4px solid #f59e0b;">
                <strong style="color: #92400e;">📚 Area to Improve:</strong> <span style="color: #b45309;">{rec['message']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Detailed answers with enhanced expander
    with st.expander("📝 View Detailed Answers", expanded=False):
        for i, answer in enumerate(st.session_state.user_answers):
            is_correct = answer['is_correct']
            bg_color = "#d1fae5" if is_correct else "#fee2e2"
            border_color = "#10b981" if is_correct else "#ef4444"
            icon = "✅" if is_correct else "❌"
            
            st.markdown(f"""
            <div style="background: {bg_color}; padding: 1rem; border-radius: 0.75rem; margin-bottom: 0.75rem; border-left: 4px solid {border_color};">
                <strong>Q{i+1}:</strong> {answer['question']}<br>
                <span style="margin-top: 0.5rem; display: inline-block;">Your answer: <strong>{answer['user_answer']}</strong> {icon}</span>
                {"<br><span style='color: #991b1b;'>Correct answer: <strong>" + answer['correct_answer'] + "</strong></span>" if not is_correct else ""}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            reset_quiz()
            st.rerun()
    with col2:
        if st.button("📥 Export Results", use_container_width=True):
            export_data = {
                'results': results,
                'answers': st.session_state.user_answers,
                'timestamp': datetime.now().isoformat()
            }
            st.download_button(
                "Download JSON",
                json.dumps(export_data, indent=2),
                "quiz_results.json",
                "application/json"
            )
    with col3:
        if st.button("📊 Save to History", use_container_width=True):
            st.session_state.analytics.save_to_history(results, st.session_state.user_answers)
            st.success("Results saved!")

def render_history_stage():
    """Display quiz history."""
    st.markdown('''
    <div class="hero-section">
        <h1 class="main-header">📜 Quiz History</h1>
        <p class="sub-header">Review your past quiz attempts and track your progress</p>
    </div>
    ''', unsafe_allow_html=True)
    
    history = st.session_state.analytics.get_history()
    
    if not history:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #64748b;">
            <span style="font-size: 4rem;">📭</span>
            <h3 style="margin-top: 1rem;">No quiz history yet</h3>
            <p>Complete a quiz and save it to see your history here!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary stats
        total_quizzes = len(history)
        avg_accuracy = sum(h.get('accuracy', 0) for h in history) / total_quizzes if total_quizzes > 0 else 0
        total_questions = sum(h.get('num_questions', 0) for h in history)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📝 Total Quizzes</h3>
                <p class="score-display">{total_quizzes}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Average Accuracy</h3>
                <p class="score-display">{avg_accuracy:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>❓ Total Questions</h3>
                <p class="score-display">{total_questions}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # Plot accuracy over time
        if len(history) > 1:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">📈</span>
                <h3 style="margin: 0; color: #1e293b;">Accuracy Trend</h3>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.analytics.plot_history_trend(history)
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # Individual quiz records
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">📋</span>
            <h3 style="margin: 0; color: #1e293b;">Quiz Records</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for i, record in enumerate(reversed(history)):
            timestamp = record.get('timestamp', 'Unknown')
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%B %d, %Y at %I:%M %p")
                except:
                    pass
            
            accuracy = record.get('accuracy', 0)
            num_questions = record.get('num_questions', 0)
            
            # Color based on accuracy
            if accuracy >= 80:
                accent_color = "#10b981"
                badge = "🏆 Excellent"
            elif accuracy >= 60:
                accent_color = "#667eea"
                badge = "⭐ Good"
            elif accuracy >= 40:
                accent_color = "#f59e0b"
                badge = "👍 Fair"
            else:
                accent_color = "#ef4444"
                badge = "📚 Needs Work"
            
            st.markdown(f"""
            <div class="history-card" style="border-left: 4px solid {accent_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #1e293b;">Quiz #{len(history) - i}</strong>
                        <span style="color: #64748b; margin-left: 0.5rem; font-size: 0.85rem;">{timestamp}</span>
                    </div>
                    <span style="background: {accent_color}20; color: {accent_color}; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85rem; font-weight: 600;">{badge}</span>
                </div>
                <div style="display: flex; gap: 2rem; margin-top: 0.75rem; color: #64748b;">
                    <span>📊 <strong style="color: {accent_color};">{accuracy}%</strong> accuracy</span>
                    <span>❓ <strong>{num_questions}</strong> questions</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="back-home-btn">', unsafe_allow_html=True)
        if st.button("🏠 Back to Home", use_container_width=True):
            reset_quiz()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="clear-history-btn">', unsafe_allow_html=True)
        if history and st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.analytics.clear_history()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <span style="font-size: 2.5rem;">🧠</span>
        <h2 style="margin: 0.5rem 0 0 0; font-size: 1.5rem;">AI Smart Quiz</h2>
        <p style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.25rem;">Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation buttons
    if st.session_state.current_stage != 'upload':
        st.markdown('<div class="back-home-btn">', unsafe_allow_html=True)
        if st.button("🏠 Back to Home", use_container_width=True):
            reset_quiz()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    if st.session_state.current_stage != 'history':
        if st.button("📜 View History", use_container_width=True):
            st.session_state.current_stage = 'history'
            st.rerun()
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 0.75rem; margin-bottom: 1rem;">
        <h4 style="margin: 0 0 0.75rem 0; font-size: 0.9rem; opacity: 0.9;">📖 How it works</h4>
        <ol style="margin: 0; padding-left: 1.25rem; font-size: 0.85rem; line-height: 1.8; opacity: 0.85;">
            <li>Upload your study material</li>
            <li>AI extracts key concepts</li>
            <li>AI generates quiz questions</li>
            <li>Take the adaptive quiz</li>
            <li>Review your analytics</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 0.75rem;">
        <h4 style="margin: 0 0 0.75rem 0; font-size: 0.9rem; opacity: 0.9;">✨ Features</h4>
        <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.85rem; line-height: 1.8; opacity: 0.85;">
            <li>🤖 AI-powered questions</li>
            <li>📈 Adaptive difficulty</li>
            <li>⏱️ Countdown timer</li>
            <li>🔗 URL article support</li>
            <li>📊 Detailed analytics</li>
            <li>📜 Quiz history</li>
            <li>💡 Smart recommendations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Main content
if st.session_state.current_stage == 'upload':
    render_upload_stage()
elif st.session_state.current_stage == 'concepts':
    render_concepts_stage()
elif st.session_state.current_stage == 'quiz':
    render_quiz_stage()
elif st.session_state.current_stage == 'results':
    render_results_stage()
elif st.session_state.current_stage == 'history':
    render_history_stage()
