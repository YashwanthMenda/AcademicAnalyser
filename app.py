"""
AcademicAnalyser - Main Application
AI-Powered PDF Learning & Quiz Evaluation System
"""

import streamlit as st
import os
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Import custom modules
from datetime import datetime
from modules.pdf_reader import extract_text_from_file, validate_pdf, get_pdf_info
from modules.text_cleaner import clean_text, get_text_stats, truncate_text
from modules.summary import generate_summary
from modules.topic_extractor import extract_important_topics, display_topics
from modules.quiz_generator import generate_quiz, display_question
from modules.evaluator import evaluate_quiz, display_score_report
from modules.mistake_analysis import analyze_mistakes, detect_weak_topics, display_weak_topics, get_weak_topic_list
from modules.recommendation import generate_revision_plan, display_revision_plan
from modules.auth import handle_google_oauth_callback, render_auth_page, logout_user
from modules.auth_db import add_history_record, update_history_quiz, get_user_history, delete_history_record


# Verify API key on startup
def verify_api_key():
    """Verify that Gemini API key is configured"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found in environment variables!")
        st.info("📝 Please follow these steps:")
        st.code("""
1. Create a .env file in the project root directory
2. Add this line:
   GEMINI_API_KEY=your_actual_api_key_here
3. Get your API key from: https://makersuite.google.com/app/apikey
4. Restart the application
        """)
        st.stop()
    
    return api_key


# Page configuration
st.set_page_config(
    page_title="AcademicAnalyser",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .quiz-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    
    if 'page' not in st.session_state:
        st.session_state.page = 'upload'
    
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = None
    
    if 'cleaned_text' not in st.session_state:
        st.session_state.cleaned_text = None
    
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    
    if 'topics' not in st.session_state:
        st.session_state.topics = None
    
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = None
    
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
        
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if 'user' not in st.session_state:
        st.session_state.user = None
        
    if 'revision_plan' not in st.session_state:
        st.session_state.revision_plan = None
        
    if 'filename' not in st.session_state:
        st.session_state.filename = None
        
    if 'history_id' not in st.session_state:
        st.session_state.history_id = None
        
    if 'history_view_id' not in st.session_state:
        st.session_state.history_view_id = None
        
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = verify_api_key()
        
    if 'generating_insights' not in st.session_state:
        st.session_state.generating_insights = False
        
    if 'insight_results' not in st.session_state:
        st.session_state.insight_results = {}


def display_header():
    """Display application header"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📚 ACADEMICANALYSER</h1>
        <p><i>"Upload. Learn. Test. Improve."</i></p>
        <p>AI-Powered PDF Learning & Quiz Evaluation System</p>
    </div>
    """, unsafe_allow_html=True)


def upload_page():
    """File Upload and Processing Page"""
    
    st.markdown("## 📄 Step 1: Upload Your Study Material")
    st.markdown("---")
    
    if st.session_state.cleaned_text:
        st.success("✅ Text extracted and processed successfully!")
        
        # Display stats
        stats = get_text_stats(st.session_state.cleaned_text)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", f"{stats['words']:,}")
        with col2:
            st.metric("Sentences", stats['sentences'])
        with col3:
            st.metric("Characters", f"{stats['characters']:,}")
        
        # Show preview
        with st.expander("📖 Preview Extracted Text", expanded=True):
            preview = st.session_state.cleaned_text[:1000] + "..." if len(st.session_state.cleaned_text) > 1000 else st.session_state.cleaned_text
            st.text_area("Preview", preview, height=250, disabled=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Upload New File / Reset", key="reset_upload", use_container_width=True):
                # Clear session state variables for file upload
                st.session_state.pdf_text = None
                st.session_state.cleaned_text = None
                st.session_state.summary = None
                st.session_state.topics = None
                st.session_state.quiz_questions = None
                st.session_state.user_answers = []
                st.session_state.current_question = 0
                st.session_state.quiz_submitted = False
                st.session_state.revision_plan = None
                st.session_state.filename = None
                st.session_state.history_id = None
                st.session_state.uploader_key += 1
                st.rerun()
        with col2:
            if st.button("Continue to Study Insights →", type="primary", key="continue_summary", use_container_width=True):
                st.session_state.page = 'study'
                st.rerun()
        return
        
    # Create tabs
    tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Paste Text"])
    
    with tab1:
        st.info("""
        **Supported formats:** PDF, TXT, DOCX (text-based files only)  
        **What gets extracted:** Text content only  
        **What gets ignored:** Images, diagrams, scanned content  
        **Maximum file size:** 200 MB
        
        ⚠️ **Note:** PDF must have selectable text (not scanned images)
        """)
        
        uploaded_file = st.file_uploader(
            "Choose your study notes",
            type=['pdf', 'txt', 'docx'],
            key=f"file_uploader_{st.session_state.uploader_key}",
            help="Upload text-based study materials"
        )
        
        if uploaded_file is not None:
            
            if validate_pdf(uploaded_file):
                
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                # Display file info
                file_info = get_pdf_info(uploaded_file)
                uploaded_file.seek(0)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("File Size", f"{file_info['size_mb']:.2f} MB")
                with col2:
                    if file_info['pages'] > 0:
                        st.metric("Pages", file_info['pages'])
                
                if st.button("🚀 Extract Text", type="primary", key="process_file"):
                    raw_text = extract_text_from_file(uploaded_file)
                    
                    if raw_text:
                        process_extracted_text(raw_text, filename=uploaded_file.name)
    
    with tab2:
        st.info("📝 **Can't extract text from your file?** Paste it manually:")
        
        manual_text = st.text_area(
            "Paste your study material:",
            height=300,
            placeholder="Copy and paste your notes, textbook content, or study material here...",
            help="Minimum 100 characters required"
        )
        
        if manual_text:
            word_count = len(manual_text.split())
            char_count = len(manual_text.strip())
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Words", f"{word_count:,}")
            with col2:
                st.metric("Characters", f"{char_count:,}")
            
            if char_count >= 100:
                if st.button("🚀 Process Text", type="primary", key="process_manual"):
                    process_extracted_text(manual_text, filename="Pasted Text Study Session")
            else:
                st.warning(f"⚠️ Please enter at least 100 characters (current: {char_count})")


def process_extracted_text(raw_text, filename="Pasted Text Study Session"):
    """Process extracted text and move to next step"""
    
    st.session_state.pdf_text = raw_text
    st.session_state.filename = filename
    
    # Clean text
    with st.spinner("🧹 Cleaning and formatting text..."):
        cleaned = clean_text(raw_text)
        cleaned = truncate_text(cleaned, max_length=50000)
        st.session_state.cleaned_text = cleaned
    
    # Rerun so that it displays the stats page at the top level
    st.rerun()


def bg_generate_insights_worker(cleaned_text, api_key, result_dict):
    """Worker function to generate summary and topics in a background thread"""
    try:
        from modules.gemini_config import generate_content_with_fallback
        
        # 1. Generate Summary
        from modules.summary import get_summary_prompt
        summary_prompt = get_summary_prompt(cleaned_text)
        summary_response = generate_content_with_fallback(api_key, summary_prompt)
        summary_text = summary_response.text
        
        # 2. Extract Topics
        from modules.topic_extractor import get_topics_prompt, parse_topics
        topics_prompt = get_topics_prompt(cleaned_text)
        topics_response = generate_content_with_fallback(api_key, topics_prompt)
        topics_text = topics_response.text
        topics_list = parse_topics(topics_text)
        
        result_dict["summary"] = summary_text
        result_dict["topics"] = topics_list
        result_dict["status"] = "success"
    except Exception as e:
        result_dict["status"] = "error"
        result_dict["error"] = str(e)


def study_page():
    """Unified Study Page displaying Summary and Topics side-by-side"""
    
    st.markdown("## 🎓 Step 2: Study Insights")
    st.markdown("---")
    
    api_key = st.session_state.api_key
    
    # Check if we are currently generating insights in the background
    if st.session_state.get('generating_insights', False):
        st.info("🤖 AI is analyzing your document, generating summary and extracting key topics. Please wait...")
        
        # Render a spinner
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0;">
                <div class="stSpinner" style="width: 24px; height: 24px; border: 3px solid #6366f1; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <span style="font-weight: 500; color: #4b5563;">Generating summary and extracting topics...</span>
            </div>
            <style>
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Wait a tiny bit and rerun to check thread status
        import time
        time.sleep(0.3)
        
        results = st.session_state.get('insight_results', {})
        status = results.get('status')
        
        if status == 'success':
            st.session_state.summary = results.get('summary')
            st.session_state.topics = results.get('topics')
            st.session_state.generating_insights = False
            
            # Save to history database
            if st.session_state.user and st.session_state.summary and st.session_state.topics:
                title = st.session_state.filename or "Untitled Study Session"
                history_id = add_history_record(
                    user_id=st.session_state.user['id'],
                    title=title,
                    summary=st.session_state.summary,
                    topics=st.session_state.topics,
                    cleaned_text=st.session_state.cleaned_text
                )
                st.session_state.history_id = history_id
                
            st.session_state.insight_results = {}
            st.rerun()
            
        elif status == 'error':
            error_msg = results.get('error', 'Unknown error')
            st.error(f"❌ Insight generation error: {error_msg}")
            if "429" in error_msg or "quota" in error_msg.lower():
                st.warning("⚠️ API rate limit reached. Please wait and try again.")
            st.session_state.generating_insights = False
            st.session_state.insight_results = {}
            st.rerun()
            
        else:
            # Still running, trigger a rerun to keep checking
            st.rerun()
        return
        
    if st.session_state.summary is None or st.session_state.topics is None:
        st.info("Click the button below to generate an AI-powered summary and extract important exam-focused topics for your study material.")
        
        if st.button("⚡ Generate Study Insights", type="primary", use_container_width=True):
            # Start background thread
            st.session_state.insight_results = {"status": "running"}
            st.session_state.generating_insights = True
            
            thread = threading.Thread(
                target=bg_generate_insights_worker,
                args=(st.session_state.cleaned_text, api_key, st.session_state.insight_results),
                daemon=True
            )
            thread.start()
            st.rerun()
    else:
        # Side-by-side display of Summary and Topics
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            with st.container():
                st.markdown("### 📄 Content Summary")
                st.markdown("---")
                st.markdown(st.session_state.summary)
                
        with col2:
            with st.container():
                st.markdown("### 📌 Important Topics")
                st.markdown("---")
                if st.session_state.topics:
                    for idx, topic in enumerate(st.session_state.topics, 1):
                        st.markdown(f"**{idx}.** {topic}")
                else:
                    st.info("No topics extracted.")
        
        st.markdown("---")
        
        # Navigation buttons
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("← Back to Upload", key="study_back_upload", use_container_width=True):
                st.session_state.page = 'upload'
                st.rerun()
        with nav_col2:
            if st.button("Continue to Quiz Setup →", type="primary", key="study_continue_quiz", use_container_width=True):
                st.session_state.page = 'quiz_setup'
                st.rerun()


def quiz_setup_page():
    """Quiz Setup Page"""
    
    st.markdown("## 🎯 Step 4: Quiz Setup")
    st.markdown("---")
    
    st.info("Select the number of questions for your quiz:")
    
    # Quiz size selection
    num_questions = st.radio(
        "Quiz Size:",
        options=[5, 10, 20],
        format_func=lambda x: f"{x} Questions ({'Quick' if x == 5 else 'Standard' if x == 10 else 'Full'} Test)",
        horizontal=True,
        help="Choose how many questions you want in your quiz"
    )
    
    st.markdown("---")
    
    # Display estimated time
    estimated_time = {5: "5-7 minutes", 10: "10-15 minutes", 20: "20-30 minutes"}
    st.info(f"⏱️ Estimated time to complete: **{estimated_time[num_questions]}**")
    
    api_key = st.session_state.api_key
    
    if st.button("🎲 Generate Quiz", type="primary"):
        
        questions = generate_quiz(st.session_state.cleaned_text, num_questions, api_key)
        
        if questions:
            st.session_state.quiz_questions = questions
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.current_question = 0
            st.session_state.quiz_submitted = False
            st.session_state.page = 'quiz'
            st.rerun()
    
    st.markdown("---")
    
    if st.button("← Back to Study Insights", key="quiz_setup_back_study"):
        st.session_state.page = 'study'
        st.rerun()


def quiz_page():
    """Quiz Taking Page"""
    
    st.markdown("## 📝 Take Your Quiz")
    st.markdown("---")
    
    questions = st.session_state.quiz_questions
    current_q = st.session_state.current_question
    total_q = len(questions)
    
    # Display current question
    question = questions[current_q]
    
    with st.container():
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
        
        selected_answer = display_question(
            question, 
            current_q + 1, 
            total_q,
            default_answer=st.session_state.user_answers[current_q]
        )
        
        # Store answer if selected
        if selected_answer:
            st.session_state.user_answers[current_q] = selected_answer
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show answer status
    answered = sum(1 for ans in st.session_state.user_answers if ans is not None)
    st.info(f"📊 Progress: {answered}/{total_q} questions answered")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_q > 0:
            if st.button("← Previous", key=f"prev_btn_{current_q}", use_container_width=True):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col2:
        # Show current answer status
        if st.session_state.user_answers[current_q]:
            st.success(f"✅ Current answer: {st.session_state.user_answers[current_q]}")
        else:
            st.warning("⚠️ Not answered yet")
    
    with col3:
        if current_q < total_q - 1:
            if st.button("Next →", key=f"next_btn_{current_q}", use_container_width=True):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button("Submit Quiz", key=f"submit_btn_{current_q}", type="primary", use_container_width=True):
                # Check if all questions answered
                if None in st.session_state.user_answers:
                    unanswered = [i+1 for i, ans in enumerate(st.session_state.user_answers) if ans is None]
                    st.error(f"⚠️ Please answer all questions before submitting")
                    st.error(f"Unanswered questions: {', '.join(map(str, unanswered))}")
                else:
                    st.session_state.quiz_submitted = True
                    
                    # Update history record if we have one
                    if st.session_state.history_id:
                        score_percentage, total_questions, mistakes, correct_count = evaluate_quiz(
                            st.session_state.quiz_questions,
                            st.session_state.user_answers
                        )
                        update_history_quiz(
                            history_id=st.session_state.history_id,
                            quiz_questions=st.session_state.quiz_questions,
                            user_answers=st.session_state.user_answers,
                            score_percentage=score_percentage,
                            correct_count=correct_count,
                            total_questions=total_questions
                        )
                    
                    st.session_state.page = 'results'
                    st.rerun()


def results_page():
    """Results and Analysis Page"""
    
    st.markdown("## 📊 Quiz Results & Performance Analysis")
    st.markdown("---")
    
    # Evaluate quiz
    score_percentage, total_questions, mistakes, correct_count = evaluate_quiz(
        st.session_state.quiz_questions,
        st.session_state.user_answers
    )
    
    wrong_count = total_questions - correct_count
    
    # Display score report
    display_score_report(score_percentage, total_questions, correct_count, wrong_count)
    
    # Mistake analysis
    if mistakes:
        st.markdown("---")
        analyze_mistakes(mistakes)
        
        # Weak topics detection
        st.markdown("---")
        weak_topics = detect_weak_topics(mistakes)
        display_weak_topics(weak_topics)
        
        # Revision recommendations
        if weak_topics:
            st.markdown("---")
            api_key = st.session_state.api_key
            weak_topic_names = get_weak_topic_list(weak_topics)
            
            if st.session_state.revision_plan is None:
                if st.button("📚 Generate Revision Plan", type="primary"):
                    revision_plan = generate_revision_plan(weak_topic_names, api_key)
                    if revision_plan:
                        st.session_state.revision_plan = revision_plan
                        st.rerun()
            else:
                display_revision_plan(st.session_state.revision_plan)
    else:
        st.success("🎉 Perfect Score! You got all questions correct!")
        st.balloons()
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Take Another Quiz", use_container_width=True):
            st.session_state.quiz_questions = None
            st.session_state.user_answers = []
            st.session_state.current_question = 0
            st.session_state.quiz_submitted = False
            st.session_state.revision_plan = None
            st.session_state.page = 'quiz_setup'
            st.rerun()
    
    with col2:
        if st.button("🔄 Start New Session", type="primary", use_container_width=True):
            # Clear all session state except API key and authentication details
            api_key = st.session_state.api_key
            user = st.session_state.get('user')
            authenticated = st.session_state.get('authenticated')
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.api_key = api_key
            st.session_state.authenticated = authenticated
            st.session_state.user = user
            st.session_state.page = 'upload'
            st.rerun()


def history_page():
    """History Page to view past summaries, topics and quiz scores"""
    
    st.markdown("## 📜 Your Study History")
    st.markdown("---")
    
    if not st.session_state.user:
        st.warning("Please log in to view your history.")
        return
        
    user_id = st.session_state.user['id']
    
    # Detail view
    if st.session_state.get('history_view_id') is not None:
        records = get_user_history(user_id)
        record = next((r for r in records if r['id'] == st.session_state.history_view_id), None)
        
        if not record:
            st.error("Session history not found.")
            st.session_state.history_view_id = None
            st.rerun()
            
        if st.button("← Back to History List", key="back_to_hist_list"):
            st.session_state.history_view_id = None
            st.rerun()
            
        st.markdown(f"### 📖 {record['title']}")
        try:
            date_obj = datetime.fromisoformat(record['created_at'])
            formatted_date = date_obj.strftime("%d %B %Y, %I:%M %p")
        except:
            formatted_date = record['created_at']
        st.caption(f"Created on: **{formatted_date}**")
        st.markdown("---")
        
        col1, col2 = st.columns([1.2, 0.8])
        with col1:
            with st.container():
                st.markdown("#### 📄 Content Summary")
                st.markdown("---")
                st.markdown(record['summary'])
        with col2:
            with st.container():
                st.markdown("#### 📌 Important Topics")
                st.markdown("---")
                for idx, topic in enumerate(record['topics'], 1):
                    st.markdown(f"**{idx}.** {topic}")
                    
        if record['quiz_questions']:
            st.markdown("---")
            st.markdown("### 🏆 Quiz Results")
            display_score_report(
                record['score_percentage'], 
                record['total_questions'], 
                record['correct_count'], 
                record['total_questions'] - record['correct_count']
            )
            
            with st.expander("📝 Review Questions & Explanations", expanded=False):
                for idx, q in enumerate(record['quiz_questions']):
                    user_ans = record['user_answers'][idx] if record['user_answers'] else "Not answered"
                    correct_ans = q['correct']
                    is_correct = (user_ans == correct_ans)
                    
                    st.markdown(f"**Question {idx+1}: {q['question']}**")
                    st.markdown(f"- **Your Answer**: {user_ans} {'✅' if is_correct else '❌'}")
                    if not is_correct:
                        st.markdown(f"- **Correct Answer**: {correct_ans}")
                    st.info(f"💡 **Explanation**: {q['explanation']}")
                    st.markdown("---")
        return
        
    # List view
    history_records = get_user_history(user_id)
    
    if not history_records:
        st.info("📜 No history found. Upload a document to start your study journey!")
        return
        
    for record in history_records:
        try:
            date_obj = datetime.fromisoformat(record['created_at'])
            formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_date = record['created_at']
            
        with st.container():
            col_text, col_quiz, col_actions = st.columns([2, 1.5, 1])
            
            with col_text:
                st.markdown(f"##### 📄 {record['title']}")
                st.caption(f"Created: {formatted_date}")
                
            with col_quiz:
                if record['quiz_questions']:
                    st.markdown(f"🏆 **Quiz Taken**")
                    st.markdown(f"Score: **{record['score_percentage']:.1f}%** ({record['correct_count']}/{record['total_questions']})")
                else:
                    st.caption("Quiz not taken yet")
                    
            with col_actions:
                if st.button("📖 View", key=f"view_hist_{record['id']}", use_container_width=True):
                    st.session_state.history_view_id = record['id']
                    st.rerun()
                if st.button("🗑️ Delete", key=f"del_hist_{record['id']}", type="secondary", use_container_width=True):
                    if delete_history_record(record['id'], user_id):
                        st.success("Session deleted successfully!")
                        st.rerun()


def sidebar_navigation():
    """Sidebar with navigation and info"""
    
    with st.sidebar:
        st.markdown("## 📚 AcademicAnalyser")
        if st.session_state.get('user'):
            st.caption(f"Signed in as **{st.session_state.user['name']}**")
        st.markdown("---")
        
        st.markdown("### 🔍 Navigation")
        if st.button("📜 View Study History", key="side_nav_history", use_container_width=True):
            if st.session_state.page != 'history' or st.session_state.get('history_view_id') is not None:
                st.session_state.page = 'history'
                st.session_state.history_view_id = None
                st.rerun()
            
        if st.button("➕ New Study Session", key="side_nav_new_session", use_container_width=True):
            if st.session_state.page != 'upload' or st.session_state.cleaned_text is not None or st.session_state.pdf_text is not None:
                # Reset current active session details
                st.session_state.pdf_text = None
                st.session_state.cleaned_text = None
                st.session_state.summary = None
                st.session_state.topics = None
                st.session_state.quiz_questions = None
                st.session_state.user_answers = []
                st.session_state.current_question = 0
                st.session_state.quiz_submitted = False
                st.session_state.revision_plan = None
                st.session_state.filename = None
                st.session_state.history_id = None
                st.session_state.uploader_key += 1
                st.session_state.generating_insights = False
                st.session_state.insight_results = {}
                st.session_state.page = 'upload'
                st.rerun()
            
        st.markdown("---")
        
        # Show progress if we are in an active session
        if st.session_state.page in ['upload', 'study', 'quiz_setup', 'quiz', 'results']:
            st.markdown("### 🎯 Current Progress")
            
            # Progress indicators
            pages = ['upload', 'study', 'quiz_setup', 'quiz', 'results']
            page_names = ['Upload Document', 'Study Insights', 'Quiz Setup', 'Take Quiz', 'Results']
            page_icons = ['📄', '🎓', '⚙️', '✍️', '📊']
            
            current_page = st.session_state.page
            
            for page, name, icon in zip(pages, page_names, page_icons):
                if page == current_page:
                    st.markdown(f"**→ {icon} {name}** ✅")
                elif pages.index(page) < pages.index(current_page):
                    st.markdown(f"✓ {icon} {name}")
                else:
                    st.markdown(f"○ {icon} {name}")
            st.markdown("---")
        
        st.markdown("### ℹ️ About")
        st.info("""
        **AcademicAnalyser** helps you:
        - 📄 Summarize study materials
        - 🎯 Identify key topics
        - 📝 Generate custom quizzes
        - 📊 Analyze your performance
        - 📚 Get personalized revision plans
        """)
        
        st.markdown("---")
        
        # Show stats if available
        if st.session_state.page != 'history':
            if st.session_state.cleaned_text:
                stats = get_text_stats(st.session_state.cleaned_text)
                st.markdown("### 📈 Document Stats")
                st.metric("Words", f"{stats['words']:,}")
                st.metric("Characters", f"{stats['characters']:,}")
            
            if st.session_state.quiz_questions:
                st.markdown("### 🎯 Quiz Stats")
                st.metric("Total Questions", len(st.session_state.quiz_questions))
                if st.session_state.quiz_submitted:
                    answered = sum(1 for ans in st.session_state.user_answers if ans is not None)
                    st.metric("Answered", f"{answered}/{len(st.session_state.quiz_questions)}")
            st.markdown("---")
        
        st.markdown("### 🔑 API Status")
        if st.session_state.api_key:
            st.success(f"✅ Connected")
        else:
            st.error("❌ Not Connected")
            
        st.markdown("---")
        if st.button("Logout", type="secondary"):
            logout_user()
            st.rerun()


def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Handle Google OAuth callback
    handle_google_oauth_callback()
    
    # Require authentication
    if not st.session_state.authenticated:
        render_auth_page()
        return
        
    # Display header
    display_header()
    
    # Sidebar
    sidebar_navigation()
    
    # Route to appropriate page
    page = st.session_state.page
    
    if page == 'upload':
        upload_page()
    elif page == 'study':
        study_page()
    elif page == 'quiz_setup':
        quiz_setup_page()
    elif page == 'quiz':
        quiz_page()
    elif page == 'results':
        results_page()
    elif page == 'history':
        history_page()


if __name__ == "__main__":
    main()
