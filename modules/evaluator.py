"""
Quiz Evaluation and Score Calculator Module
Evaluates student answers and calculates scores
"""

import streamlit as st


def evaluate_quiz(quiz_questions, user_answers):
    """
    Evaluate quiz responses
    
    Args:
        quiz_questions (list): List of question dictionaries
        user_answers (list): List of user's selected answers
        
    Returns:
        tuple: (score, total, mistakes, correct_count)
    """
    
    total_questions = len(quiz_questions)
    correct_count = 0
    mistakes = []
    
    for i in range(total_questions):
        question = quiz_questions[i]
        correct_answer = question['correct']
        user_answer = user_answers[i]
        
        if user_answer == correct_answer:
            correct_count += 1
        else:
            mistakes.append({
                'question_num': i + 1,
                'question': question['question'],
                'user_answer': user_answer if user_answer else "Not answered",
                'correct_answer': correct_answer,
                'explanation': question['explanation'],
                'topic': question['topic']
            })
    
    score_percentage = (correct_count / total_questions) * 100
    
    return score_percentage, total_questions, mistakes, correct_count


def display_score_report(score_percentage, total_questions, correct_count, wrong_count):
    """
    Display score report
    
    Args:
        score_percentage (float): Score percentage
        total_questions (int): Total questions
        correct_count (int): Number of correct answers
        wrong_count (int): Number of wrong answers
    """
    
    st.markdown("---")
    st.markdown("## 📊 YOUR SCORE REPORT")
    st.markdown("---")
    
    # Create columns for score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Questions", total_questions)
    
    with col2:
        st.metric("Correct ✅", correct_count)
    
    with col3:
        st.metric("Wrong ❌", wrong_count)
    
    st.markdown("---")
    
    # Score percentage with color coding
    st.markdown(f"### Final Score: {score_percentage:.1f}%")
    
    # Progress bar
    st.progress(score_percentage / 100)
    
    # Grade
    grade = get_grade(score_percentage)
    grade_color = get_grade_color(score_percentage)
    
    st.markdown(f"### Grade: :{grade_color}[{grade}]")
    st.markdown("---")


def get_grade(score_percentage):
    """
    Get letter grade based on score
    
    Args:
        score_percentage (float): Score percentage
        
    Returns:
        str: Letter grade
    """
    
    if score_percentage >= 90:
        return "Excellent! 🌟"
    elif score_percentage >= 75:
        return "Good! 👍"
    elif score_percentage >= 50:
        return "Average 📚"
    else:
        return "Needs Improvement 📖"


def get_grade_color(score_percentage):
    """
    Get color for grade display
    
    Args:
        score_percentage (float): Score percentage
        
    Returns:
        str: Color name
    """
    
    if score_percentage >= 90:
        return "green"
    elif score_percentage >= 75:
        return "blue"
    elif score_percentage >= 50:
        return "orange"
    else:
        return "red"


def calculate_statistics(mistakes):
    """
    Calculate additional statistics
    
    Args:
        mistakes (list): List of mistakes
        
    Returns:
        dict: Statistics dictionary
    """
    
    if not mistakes:
        return {
            'total_mistakes': 0,
            'unanswered': 0,
            'incorrect': 0
        }
    
    unanswered = sum(1 for m in mistakes if m['user_answer'] == "Not answered")
    incorrect = len(mistakes) - unanswered
    
    return {
        'total_mistakes': len(mistakes),
        'unanswered': unanswered,
        'incorrect': incorrect
    }
