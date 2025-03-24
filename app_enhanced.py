"""
Streamlit application for the enhanced SAT Reading & Writing Chatbot Tutor

This script implements the Streamlit UI for the enhanced chatbot tutor,
integrating all components and providing a user-friendly interface.
"""

import os
import json
import time
import datetime
import streamlit as st
from datetime import datetime, timedelta

# Import components
from memory_manager import MemoryManager
from openai_integration import OpenAIIntegration
from question_engine import QuestionEngine
from enhanced_chatbot_core import SATTutorChatbot

# Page configuration
st.set_page_config(
    page_title="SAT Reading & Writing Tutor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #1890ff;
    }
    .chat-message.assistant {
        background-color: #f6ffed;
        border-left: 5px solid #52c41a;
    }
    .chat-message .content {
        margin-top: 0.5rem;
    }
    .achievement {
        background-color: #fffbe6;
        border-left: 5px solid #faad14;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .correct {
        color: #52c41a;
        font-weight: bold;
    }
    .incorrect {
        color: #f5222d;
        font-weight: bold;
    }
    .countdown {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1890ff;
        text-align: center;
        margin-bottom: 1rem;
    }
    .points {
        font-size: 1.2rem;
        font-weight: bold;
        color: #722ed1;
        text-align: center;
        margin-bottom: 1rem;
    }
    .streak {
        font-size: 1.2rem;
        font-weight: bold;
        color: #fa8c16;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "points" not in st.session_state:
    st.session_state.points = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "achievements" not in st.session_state:
    st.session_state.achievements = []

def initialize_chatbot():
    """Initialize the chatbot with user information"""
    user_name = st.session_state.user_name if "user_name" in st.session_state else None
    test_date = st.session_state.test_date if "test_date" in st.session_state else None
    
    # Create chatbot
    st.session_state.chatbot = SATTutorChatbot(user_name=user_name, test_date=test_date)
    
    # Start session if user name is provided
    if user_name:
        session_info = st.session_state.chatbot.start_session()
        
        # Add greeting to messages
        st.session_state.messages.append({"role": "assistant", "content": session_info["greeting"]})

def format_message(message):
    """Format a message for display"""
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        st.markdown(f'<div class="chat-message user"><div class="content">{content}</div></div>', unsafe_allow_html=True)
    else:
        # Check for special formatting
        if "✅ Correct!" in content:
            content = content.replace("✅ Correct!", '<span class="correct">✅ Correct!</span>')
        elif "❌ That's not correct" in content:
            content = content.replace("❌ That's not correct", '<span class="incorrect">❌ That's not correct</span>')
        
        # Check for achievements
        if "🏆 Achievement unlocked:" in content:
            achievement_lines = []
            non_achievement_lines = []
            
            for line in content.split("\n"):
                if "🏆 Achievement unlocked:" in line:
                    achievement_lines.append(line)
                else:
                    non_achievement_lines.append(line)
            
            # Format achievements
            achievement_html = ""
            for line in achievement_lines:
                achievement_html += f'<div class="achievement">{line}</div>'
            
            # Combine content
            content = "\n".join(non_achievement_lines)
            content = f'{achievement_html}<div class="content">{content}</div>'
        else:
            content = f'<div class="content">{content}</div>'
        
        st.markdown(f'<div class="chat-message assistant">{content}</div>', unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with user information and stats"""
    with st.sidebar:
        st.title("SAT Reading & Writing Tutor")
        st.markdown("---")
        
        # User information form
        with st.form("user_info_form"):
            user_name = st.text_input("Your Name", value=st.session_state.user_name if "user_name" in st.session_state else "")
            
            # Test date (default to 14 days from now)
            default_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            test_date = st.date_input(
                "Test Date",
                value=datetime.strptime(st.session_state.test_date, "%Y-%m-%d") if "test_date" in st.session_state else datetime.strptime(default_date, "%Y-%m-%d")
            )
            
            submit_button = st.form_submit_button("Start/Update Session")
            
            if submit_button:
                st.session_state.user_name = user_name
                st.session_state.test_date = test_date.strftime("%Y-%m-%d")
                
                # Initialize or update chatbot
                if st.session_state.chatbot is None:
                    initialize_chatbot()
                else:
                    st.session_state.chatbot.set_user_name(user_name)
                    st.session_state.chatbot.set_test_date(test_date.strftime("%Y-%m-%d"))
        
        st.markdown("---")
        
        # Display countdown if test date is set
        if "test_date" in st.session_state:
            try:
                test_date = datetime.strptime(st.session_state.test_date, "%Y-%m-%d")
                days_remaining = (test_date - datetime.now()).days
                
                if days_remaining > 0:
                    st.markdown(f'<div class="countdown">📅 {days_remaining} days until your SAT test</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="countdown">📅 Test day is here! Good luck!</div>', unsafe_allow_html=True)
            except:
                pass
        
        # Display points and streak
        if "points" in st.session_state and st.session_state.points > 0:
            st.markdown(f'<div class="points">🎯 Points: {st.session_state.points}</div>', unsafe_allow_html=True)
        
        if "streak" in st.session_state and st.session_state.streak > 0:
            st.markdown(f'<div class="streak">🔥 Streak: {st.session_state.streak}</div>', unsafe_allow_html=True)
        
        # Display achievements
        if "achievements" in st.session_state and st.session_state.achievements:
            st.markdown("### 🏆 Achievements")
            for achievement in st.session_state.achievements:
                st.markdown(f"**{achievement['title']}**: {achievement['description']}")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        if st.button("Quiz me on Prefixes"):
            process_message("Quiz me on prefixes")
        
        if st.button("Quiz me on Roots"):
            process_message("Quiz me on roots")
        
        if st.button("Quiz me on Suffixes"):
            process_message("Quiz me on suffixes")
        
        if st.button("End Session"):
            if st.session_state.chatbot and st.session_state.chatbot.session_state["active"]:
                summary = st.session_state.chatbot.end_session()
                st.session_state.messages.append({"role": "assistant", "content": summary["response"]})
                st.rerun()

def process_message(message_text):
    """Process a user message and update the UI"""
    if not message_text.strip():
        return
    
    # Initialize chatbot if not already initialized
    if st.session_state.chatbot is None:
        initialize_chatbot()
    
    # Add user message to messages
    st.session_state.messages.append({"role": "user", "content": message_text})
    
    # Process message
    response = st.session_state.chatbot.process_message(message_text)
    
    # Add assistant response to messages
    st.session_state.messages.append({"role": "assistant", "content": response["response"]})
    
    # Update current question if provided
    if "question" in response:
        st.session_state.current_question = response["question"]
    
    # Update points and streak if provided
    if "points" in response:
        st.session_state.points = response["points"]
    
    if "streak" in response:
        st.session_state.streak = response["streak"]
    
    # Update achievements
    if st.session_state.chatbot and "achievements" in st.session_state.chatbot.session_state:
        st.session_state.achievements = st.session_state.chatbot.session_state["achievements"]

def main():
    """Main function to run the Streamlit app"""
    # Display sidebar
    display_sidebar()
    
    # Main content area
    st.title("SAT Reading & Writing Tutor")
    
    # Display personalized greeting if user name is set
    if "user_name" in st.session_state and st.session_state.user_name:
        st.markdown(f"### Hi, {st.session_state.user_name}! Ready to crush your SAT prep today?")
    
    # Display messages
    for message in st.session_state.messages:
        format_message(message)
    
    # Message input
    with st.form("message_form", clear_on_submit=True):
        user_input = st.text_input("Type your message:", key="user_message")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            process_message(user_input)
            st.rerun()
    
    # Multiple choice buttons if in quiz mode
    if (st.session_state.chatbot and 
        st.session_state.chatbot.session_state["current_mode"] == "quiz" and
        st.session_state.current_question):
        
        st.markdown("### Quick Answer:")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("A"):
                process_message("A")
                st.rerun()
        
        with col2:
            if st.button("B"):
                process_message("B")
                st.rerun()
        
        with col3:
            if st.button("C"):
                process_message("C")
                st.rerun()
        
        with col4:
            if st.button("D"):
                process_message("D")
                st.rerun()
        
        # Why button
        if st.button("Why?"):
            process_message("Why?")
            st.rerun()

if __name__ == "__main__":
    main()
