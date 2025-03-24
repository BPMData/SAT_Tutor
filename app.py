"""
SAT Reading & Writing Chatbot Tutor - Streamlit Frontend
This module implements the frontend UI using Streamlit, providing an interactive
interface for the SAT Reading & Writing Chatbot Tutor.
"""

import os
import json
import time
import datetime
import streamlit as st
from chatbot_core import SATTutorChatbot

# Create data directories if they don't exist
os.makedirs("data/sessions", exist_ok=True)
os.makedirs("data/performance", exist_ok=True)
os.makedirs("data/preferences", exist_ok=True)
os.makedirs("data/vocabulary", exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="SAT Reading & Writing Tutor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #F1F8E9;
        border-left: 5px solid #8BC34A;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex-grow: 1;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        color: white;
        background-color: #4CAF50;
        margin-right: 0.5rem;
    }
    .badge.streak {
        background-color: #FF9800;
    }
    .badge.points {
        background-color: #2196F3;
    }
    .badge.achievement {
        background-color: #9C27B0;
    }
    .progress-container {
        margin-bottom: 1rem;
    }
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.25rem;
    }
    .progress-bar {
        height: 0.5rem;
        border-radius: 0.25rem;
        background-color: #E0E0E0;
    }
    .progress-bar .fill {
        height: 100%;
        border-radius: 0.25rem;
        background-color: #4CAF50;
    }
    .option-button {
        display: block;
        width: 100%;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border: 1px solid #E0E0E0;
        border-radius: 0.25rem;
        background-color: white;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .option-button:hover {
        background-color: #F5F5F5;
        border-color: #BDBDBD;
    }
    .option-button.selected {
        background-color: #E3F2FD;
        border-color: #2196F3;
    }
    .option-button.correct {
        background-color: #F1F8E9;
        border-color: #8BC34A;
    }
    .option-button.incorrect {
        background-color: #FFEBEE;
        border-color: #F44336;
    }
    .countdown {
        text-align: center;
        padding: 1rem;
        background-color: #E8EAF6;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .countdown .days {
        font-size: 2rem;
        font-weight: 700;
        color: #3F51B5;
    }
    .countdown .label {
        font-size: 1rem;
        color: #5C6BC0;
    }
    .sidebar-content {
        padding: 1rem;
    }
    .achievement-card {
        padding: 1rem;
        background-color: #F3E5F5;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 5px solid #9C27B0;
    }
    .achievement-card .title {
        font-weight: 700;
        color: #9C27B0;
    }
    .achievement-card .description {
        font-size: 0.875rem;
        color: #6A1B9A;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'test_date' not in st.session_state:
    st.session_state.test_date = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None
if 'question_result' not in st.session_state:
    st.session_state.question_result = None
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'progress' not in st.session_state:
    st.session_state.progress = {
        'prefixes': 0,
        'roots': 0,
        'suffixes': 0
    }
if 'days_until_test' not in st.session_state:
    st.session_state.days_until_test = 14

# Sidebar
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    
    # User profile section
    st.markdown("<h2 class='sub-header'>Your Profile</h2>", unsafe_allow_html=True)
    
    # User name input
    if st.session_state.user_name is None:
        user_name = st.text_input("Enter your name:", key="name_input")
        if st.button("Save Name"):
            if user_name:
                st.session_state.user_name = user_name
                # Initialize chatbot with user name
                st.session_state.chatbot = SATTutorChatbot(user_name=user_name, test_date=st.session_state.test_date)
                # Start session
                session_info = st.session_state.chatbot.start_session()
                # Update session state
                st.session_state.days_until_test = session_info.get('days_until_test', 14)
                # Add greeting to conversation
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": f"{session_info['greeting']}\n\n{session_info['progress_info']}\n\n{session_info['suggestion']}\n\nWhat would you like to do today?"
                })
                st.experimental_rerun()
    else:
        st.markdown(f"<h3>Hello, {st.session_state.user_name}! 👋</h3>", unsafe_allow_html=True)
        
        # Test date input
        st.markdown("<h3>SAT Test Date</h3>", unsafe_allow_html=True)
        new_test_date = st.date_input(
            "When is your SAT?",
            value=datetime.datetime.strptime(st.session_state.test_date, "%Y-%m-%d"),
            min_value=datetime.datetime.now()
        )
        if new_test_date:
            new_test_date_str = new_test_date.strftime("%Y-%m-%d")
            if new_test_date_str != st.session_state.test_date:
                st.session_state.test_date = new_test_date_str
                if st.session_state.chatbot:
                    result = st.session_state.chatbot.set_test_date(new_test_date_str)
                    if result.get('status') == 'success':
                        st.success("Test date updated!")
                        # Update days until test
                        days_until_test = (new_test_date - datetime.datetime.now().date()).days
                        st.session_state.days_until_test = max(0, days_until_test)
        
        # Countdown to test
        st.markdown("<div class='countdown'>", unsafe_allow_html=True)
        st.markdown(f"<div class='days'>{st.session_state.days_until_test}</div>", unsafe_allow_html=True)
        st.markdown("<div class='label'>days until your SAT</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Progress section
        st.markdown("<h3>Your Progress</h3>", unsafe_allow_html=True)
        
        # Prefixes progress
        st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
        st.markdown("<div class='progress-label'>", unsafe_allow_html=True)
        st.markdown("<span>Prefixes</span>", unsafe_allow_html=True)
        st.markdown(f"<span>{st.session_state.progress.get('prefixes', 0):.0f}%</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='progress-bar'>", unsafe_allow_html=True)
        st.markdown(f"<div class='fill' style='width: {st.session_state.progress.get('prefixes', 0)}%;'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Roots progress
        st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
        st.markdown("<div class='progress-label'>", unsafe_allow_html=True)
        st.markdown("<span>Roots</span>", unsafe_allow_html=True)
        st.markdown(f"<span>{st.session_state.progress.get('roots', 0):.0f}%</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='progress-bar'>", unsafe_allow_html=True)
        st.markdown(f"<div class='fill' style='width: {st.session_state.progress.get('roots', 0)}%;'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Suffixes progress
        st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
        st.markdown("<div class='progress-label'>", unsafe_allow_html=True)
        st.markdown("<span>Suffixes</span>", unsafe_allow_html=True)
        st.markdown(f"<span>{st.session_state.progress.get('suffixes', 0):.0f}%</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='progress-bar'>", unsafe_allow_html=True)
        st.markdown(f"<div class='fill' style='width: {st.session_state.progress.get('suffixes', 0)}%;'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Gamification elements
        st.markdown("<h3>Your Stats</h3>", unsafe_allow_html=True)
        
        # Points and streak
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='badge points'>🏆 {st.session_state.points} Points</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='badge streak'>🔥 {st.session_state.streak} Streak</div>", unsafe_allow_html=True)
        
        # Achievements
        if st.session_state.achievements:
            st.markdown("<h3>Achievements</h3>", unsafe_allow_html=True)
            for achievement in st.session_state.achievements:
                st.markdown("<div class='achievement-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='title'>🏆 {achievement['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='description'>{achievement['description']}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Reading level adjustment
        st.markdown("<h3>Settings</h3>", unsafe_allow_html=True)
        reading_level = st.select_slider(
            "Explanation Reading Level",
            options=[8, 9, 10, 11, 12],
            value=10,
            format_func=lambda x: f"Grade {x}"
        )
        if st.button("Update Reading Level"):
            if st.session_state.chatbot:
                st.session_state.chatbot.adaptation_engine.adjust_reading_level(reading_level)
                st.success(f"Reading level updated to Grade {reading_level}!")
        
        # End session button
        if st.button("End Session"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.end_session()
                if 'summary' in result:
                    # Add summary to conversation
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": result['response']
                    })
                    # Reset current question
                    st.session_state.current_question = None
                    st.session_state.selected_option = None
                    st.session_state.question_result = None
                    st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main content
st.markdown("<h1 class='main-header'>📚 SAT Reading & Writing Tutor</h1>", unsafe_allow_html=True)

# Welcome message for new users
if st.session_state.user_name is None:
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h2>Welcome to the SAT Reading & Writing Tutor!</h2>
        <p>This interactive tutor will help you master prefixes, roots, and suffixes to boost your SAT Reading & Writing score.</p>
        <p>Please enter your name in the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Chat interface
    chat_container = st.container()
    
    # Display conversation history
    with chat_container:
        for message in st.session_state.conversation:
            role = message["role"]
            content = message["content"]
            
            st.markdown(f"<div class='chat-message {role}'>", unsafe_allow_html=True)
            st.markdown("<div class='content'>", unsafe_allow_html=True)
            
            if role == "user":
                st.markdown(f"<img src='https://api.dicebear.com/6.x/initials/svg?seed={st.session_state.user_name}' class='avatar' />", unsafe_allow_html=True)
            else:
                st.markdown("<img src='https://api.dicebear.com/6.x/bottts/svg?seed=SAT' class='avatar' />", unsafe_allow_html=True)
            
            st.markdown(f"<div class='message'>{content}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Question interface
    if st.session_state.current_question:
        question = st.session_state.current_question
        
        st.markdown("<div style='padding: 1rem; background-color: #F5F5F5; border-radius: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        st.markdown(f"<h3>{question['question']}</h3>", unsafe_allow_html=True)
        
        # Display options as buttons
        for option in question['options']:
            option_letter = option[0]  # Extract A, B, C, D
            option_text = option[3:]  # Remove "A) " prefix
            
            # Determine button class based on state
            button_class = "option-button"
            if st.session_state.selected_option == option_letter:
                button_class += " selected"
                if st.session_state.question_result:
                    if st.session_state.question_result.get('correct', False):
                        button_class += " correct"
                    else:
                        button_class += " incorrect"
            elif st.session_state.question_result and option_letter == st.session_state.question_result.get('correct_answer'):
                button_class += " correct"
            
            # Create button
            if st.button(option, key=f"option_{option_letter}", disabled=st.session_state.selected_option is not None):
                st.session_state.selected_option = option_letter
                
                # Process answer
                if st.session_state.chatbot:
                    result = st.session_state.chatbot.process_message(option_letter)
                    
                    # Update conversation
                    if 'response' in result:
                        st.session_state.conversation.append({
                            "role": "user",
                            "content": option
                        })
                        st.session_state.conversation.append({
                            "role": "assistant",
                            "content": result['response']
                        })
                    
                    # Update question result
                    if 'result' in result:
                        st.session_state.question_result = result['result']
                        
                        # Update points and streak
                        if 'points' in result:
                            st.session_state.points = result['points']
                        if 'streak' in result:
                            st.session_state.streak = result['streak']
                        
                        # Update achievements
                        if 'achievements' in result:
                            st.session_state.achievements = result['achievements']
                    
                    st.experimental_rerun()
        
        # "Why?" button for explanations
        if st.session_state.selected_option and st.button("Why?", key="why_button"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_message("Why?")
                
                # Update conversation
                if 'response' in result:
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": "Why?"
                    })
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": result['response']
                    })
                    st.experimental_rerun()
        
        # Next question button
        if st.session_state.selected_option and st.button("Next Question", key="next_button"):
            # Reset question state
            st.session_state.current_question = None
            st.session_state.selected_option = None
            st.session_state.question_result = None
            
            # Request new question
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_message("Next question")
                
                # Update conversation
                if 'response' in result:
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": "Next question"
                    })
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": result['response']
                    })
                
                # Update current question
                if 'question' in result:
                    st.session_state.current_question = result['question']
                
                st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # User input
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_input("Type your message:", key="user_message")
        submit_button = st.form_submit_button("Send")
    
    if submit_button and user_input:
        # Add user message to conversation
        st.session_state.conversation.append({
            "role": "user",
            "content": user_input
        })
        
        # Process message with chatbot
        if st.session_state.chatbot:
            result = st.session_state.chatbot.process_message(user_input)
            
            # Update conversation
            if 'response' in result:
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": result['response']
                })
            
            # Update current question if provided
            if 'question' in result:
                st.session_state.current_question = result['question']
                st.session_state.selected_option = None
                st.session_state.question_result = None
            
            # Update progress if provided
            if 'progress' in result:
                st.session_state.progress = result['progress']
            
            st.experimental_rerun()

# Quick action buttons
if st.session_state.user_name:
    st.markdown("<h3>Quick Actions</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Quiz on Prefixes"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_message("Quiz me on prefixes")
                
                # Update conversation
                if 'response' in result:
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": "Quiz me on prefixes"
                    })
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": result['response']
                    })
                
                # Update current question
                if 'question' in result:
                    st.session_state.current_question = result['question']
                    st.session_state.selected_option = None
                    st.session_state.question_result = None
                
                st.experimental_rerun()
    
    with col2:
        if st.button("Quiz on Roots"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_message("Quiz me on roots")
                
                # Update conversation
                if 'response' in result:
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": "Quiz me on roots"
                    })
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": result['response']
                    })
                
                # Update current question
                if 'question' in result:
                    st.session_state.current_question = result['question']
                    st.session_state.selected_option = None
                    st.session_state.question_result = None
                
                st.experimental_rerun()
    
    with col3:
        if st.button("Quiz on Suffixes"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_message("Quiz me on suffixes")
                
                # Update conversation
                if 'response' in result:
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": "Quiz me on suffixes"
                    })
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": result['response']
                    })
                
                # Update current question
                if 'question' in result:
                    st.session_state.current_question = result['question']
                    st.session_state.selected_option = None
                    st.session_state.question_result = None
                
                st.experimental_rerun()
    
    with col4:
        if st.button("Sentence Completion"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_message("Practice sentence completion")
                
                # Update conversation
                if 'response' in result:
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": "Practice sentence completion"
                    })
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": result['response']
                    })
                
                # Update current question
                if 'question' in result:
                    st.session_state.current_question = result['question']
                    st.session_state.selected_option = None
                    st.session_state.question_result = None
                
                st.experimental_rerun()

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 2rem; padding: 1rem; background-color: #F5F5F5; border-radius: 0.5rem;'>
    <p>SAT Reading & Writing Tutor | Helping you master prefixes, roots, and suffixes</p>
    <p style='font-size: 0.8rem;'>Created for high school students preparing for the SAT</p>
</div>
""", unsafe_allow_html=True)

