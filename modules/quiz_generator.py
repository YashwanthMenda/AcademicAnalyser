"""
Quiz Generation Module
Generates multiple choice questions using Gemini AI
"""

import google.generativeai as genai
import streamlit as st
import json
import re


def generate_quiz(cleaned_text, num_questions, api_key):
    """
    Generate quiz questions from content
    
    Args:
        cleaned_text (str): Preprocessed text
        num_questions (int): Number of questions to generate
        api_key (str): Google Gemini API key
        
    Returns:
        list: List of question dictionaries
    """
    try:
        from .gemini_config import generate_content_with_fallback
        
        prompt = get_quiz_prompt(cleaned_text, num_questions)
        
        with st.spinner(f"🎯 Generating {num_questions} quiz questions..."):
            response = generate_content_with_fallback(api_key, prompt)
        
        quiz_text = response.text
        questions = parse_quiz_json(quiz_text)
        
        if questions and len(questions) > 0:
            st.success(f"✅ Generated {len(questions)} questions successfully")
            return questions
        else:
            st.error("❌ Failed to generate quiz questions")
            return None
            
    except Exception as e:
        st.error(f"❌ Quiz generation error: {str(e)}")
        
        if "429" in str(e) or "quota" in str(e).lower():
            st.warning("⚠️ API rate limit reached. Please wait 60 seconds and try again.")
            
        return None


def get_quiz_prompt(text, num_questions):
    """
    Create quiz generation prompt
    
    Args:
        text (str): Content to create quiz from
        num_questions (int): Number of questions
        
    Returns:
        str: Formatted prompt
    """
    
    # Truncate if too long
    max_length = 30000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    prompt = f"""You are an expert quiz creator for academic assessments.

Generate exactly {num_questions} multiple choice questions from the following study material.

**Requirements for each question:**
1. Create clear, specific questions
2. Provide exactly 4 options (A, B, C, D)
3. Clearly mark the correct answer
4. Assign a topic/category
5. Provide a detailed explanation

**IMPORTANT: Return ONLY valid JSON, no other text.**

**JSON Format:**
[
  {{
    "question": "What is the primary function of X?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": "Option A",
    "topic": "Topic Name",
    "explanation": "Detailed explanation of why Option A is correct."
  }}
]

**Study Material:**
{text}

**Generate exactly {num_questions} questions in valid JSON format:**"""
    
    return prompt


def parse_quiz_json(quiz_text):
    """
    Parse quiz questions from JSON response
    
    Args:
        quiz_text (str): Raw JSON response
        
    Returns:
        list: Parsed questions
    """
    
    try:
        # Remove markdown code blocks if present
        json_match = re.search(r'```json\s*(.*?)\s*```', quiz_text, re.DOTALL)
        if json_match:
            quiz_text = json_match.group(1)
        else:
            # Try to find JSON array directly
            json_match = re.search(r'\[.*\]', quiz_text, re.DOTALL)
            if json_match:
                quiz_text = json_match.group(0)
        
        # Parse JSON
        questions = json.loads(quiz_text)
        
        # Validate and clean questions
        validated_questions = []
        for q in questions:
            if validate_question(q):
                validated_questions.append(q)
        
        return validated_questions
        
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {str(e)}")
        st.error("Failed to parse quiz questions. Please try again.")
        return None
    except Exception as e:
        st.error(f"Quiz parsing error: {str(e)}")
        return None


def validate_question(question):
    """
    Validate question structure
    
    Args:
        question (dict): Question dictionary
        
    Returns:
        bool: True if valid
    """
    
    required_fields = ['question', 'options', 'correct', 'topic', 'explanation']
    
    # Check all required fields exist
    if not all(field in question for field in required_fields):
        return False
    
    # Check options is a list of 4 items
    if not isinstance(question['options'], list) or len(question['options']) != 4:
        return False
    
    # Check correct answer is in options
    if question['correct'] not in question['options']:
        return False
    
    return True


def display_question(question, question_num, total_questions, default_answer=None):
    """
    Display a single question
    
    Args:
        question (dict): Question data
        question_num (int): Current question number
        total_questions (int): Total number of questions
        default_answer (str, optional): Previously selected answer
        
    Returns:
        str: Selected answer
    """
    
    # Progress bar
    progress = question_num / total_questions
    st.progress(progress)
    
    st.markdown(f"### Question {question_num} of {total_questions}")
    st.markdown("---")
    
    # Question text
    st.markdown(f"**{question['question']}**")
    st.markdown("")
    
    # Determine default index
    default_idx = None
    if default_answer and default_answer in question['options']:
        default_idx = question['options'].index(default_answer)
    
    # Answer options
    selected = st.radio(
        "Select your answer:",
        question['options'],
        key=f"q_{question_num}",
        index=default_idx
    )
    
    return selected
