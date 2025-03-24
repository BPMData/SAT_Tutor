"""
Enhanced SAT Reading & Writing Chatbot Tutor with Memory and LLM Integration

This module implements the enhanced chatbot core that integrates the memory system,
OpenAI GPT-4o API, and enhanced question generation capabilities.
"""

import os
import json
import time
import datetime
import uuid
from typing import List, Dict, Any, Optional, Union

from memory_manager import MemoryManager
from openai_integration import OpenAIIntegration
from question_engine import QuestionEngine

class SATTutorChatbot:
    """
    Enhanced SAT Reading & Writing Chatbot Tutor with memory and LLM integration.
    """
    
    def __init__(self, user_name=None, test_date=None):
        """Initialize the SAT Tutor Chatbot with user information"""
        self.user_name = user_name
        self.test_date = test_date if test_date else (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        self.user_id = str(uuid.uuid4()) if not user_name else user_name.lower().replace(" ", "_")
        
        # Create necessary directories
        os.makedirs("data/sessions", exist_ok=True)
        os.makedirs("data/performance", exist_ok=True)
        os.makedirs("data/preferences", exist_ok=True)
        os.makedirs("data/vocabulary", exist_ok=True)
        
        # Initialize components
        self.openai_integration = OpenAIIntegration()
        self.memory_manager = MemoryManager()
        self.question_engine = QuestionEngine(self.openai_integration)
        
        # Initialize session state
        self.session_state = {
            "active": False,
            "current_mode": None,
            "current_question": None,
            "conversation_history": [],
            "streak": 0,
            "points": 0,
            "achievements": []
        }
        
        # Add system message to memory
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize the memory with system instructions"""
        system_instructions = self._get_system_instructions()
        self.memory_manager.add_message("system", system_instructions)
    
    def _get_system_instructions(self):
        """Get the system instructions for the SAT tutor"""
        return f"""
        You are an expert SAT Reading & Writing tutor designed to help high school students prepare for the test.
        Your name is SAT Tutor and you're helping {self.user_name if self.user_name else "a student"} prepare for their SAT test on {self.test_date}.
        
        Your goal is to provide personalized assistance, focusing on prefixes, roots, and suffixes.
        
        You should:
        1. Respond in a friendly, motivating, non-condescending tone
        2. Provide explanations at the appropriate reading level for the student
        3. Track the student's progress and focus on areas that need improvement
        4. Generate SAT-style questions that test the student's knowledge
        5. Provide detailed explanations for answers
        
        Remember to maintain context from previous interactions and adapt to the student's needs.
        """
    
    def start_session(self):
        """Start a new learning session"""
        if not self.user_name:
            return {"error": "User name is required to start a session"}
        
        self.session_state["active"] = True
        self.session_state["start_time"] = time.time()
        self.session_state["current_mode"] = "greeting"
        self.session_state["streak"] = 0
        self.session_state["points"] = 0
        self.session_state["achievements"] = []
        
        # Generate greeting message using LLM
        greeting_prompt = f"""
        Generate a friendly greeting for {self.user_name} who is preparing for the SAT Reading & Writing section.
        The test is on {self.test_date}, which is {self._days_until_test()} days away.
        Focus on encouraging them to work on prefixes, roots, and suffixes.
        Keep it concise and motivating.
        """
        
        # Add greeting prompt to memory
        self.memory_manager.add_message("user", greeting_prompt)
        
        # Generate greeting using LLM
        context = self.memory_manager.get_context_for_prompt()
        response = self.openai_integration.generate_response(context)
        
        # Extract greeting content
        greeting = response["content"]
        
        # Add greeting to memory
        self.memory_manager.add_message("assistant", greeting)
        
        # Add to conversation history
        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": greeting
        })
        
        return {
            "greeting": greeting,
            "days_until_test": self._days_until_test()
        }
    
    def _days_until_test(self):
        """Calculate days until the SAT test"""
        try:
            test_date = datetime.datetime.strptime(self.test_date, "%Y-%m-%d")
            days_remaining = (test_date - datetime.datetime.now()).days
            return max(0, days_remaining)
        except ValueError:
            return 14  # Default to 14 days if date format is invalid
    
    def process_message(self, message):
        """Process a user message and generate a response"""
        # Add user message to conversation history
        self.session_state["conversation_history"].append({
            "role": "user",
            "content": message
        })
        
        # Add message to memory
        self.memory_manager.add_message("user", message)
        
        # If session is not active, start a new one
        if not self.session_state["active"]:
            if not self.user_name:
                # Extract name from message if possible
                name_indicators = ["my name is", "i am", "i'm", "call me"]
                for indicator in name_indicators:
                    if indicator in message.lower():
                        parts = message.lower().split(indicator, 1)
                        if len(parts) > 1:
                            potential_name = parts[1].strip().split()[0].capitalize()
                            if len(potential_name) > 1:  # Ensure it's a valid name
                                self.user_name = potential_name
                                self._initialize_memory()  # Reinitialize with user name
                                break
                
                if not self.user_name:
                    response_text = "I'd be happy to help you prepare for the SAT Reading & Writing section! Could you tell me your name so I can personalize your experience?"
                    
                    # Add response to memory and conversation history
                    self.memory_manager.add_message("assistant", response_text)
                    self.session_state["conversation_history"].append({
                        "role": "assistant",
                        "content": response_text
                    })
                    
                    return {"response": response_text}
            
            # Start session with user name
            session_info = self.start_session()
            return {"response": session_info["greeting"]}
        
        # Process message based on current mode
        if self.session_state["current_mode"] == "greeting":
            return self._process_greeting_mode(message)
        elif self.session_state["current_mode"] == "quiz":
            return self._process_quiz_mode(message)
        elif self.session_state["current_mode"] == "explanation":
            return self._process_explanation_mode(message)
        elif self.session_state["current_mode"] == "review":
            return self._process_review_mode(message)
        else:
            # Default to greeting mode
            self.session_state["current_mode"] = "greeting"
            return self._process_greeting_mode(message)
    
    def _process_greeting_mode(self, message):
        """Process message in greeting mode"""
        message_lower = message.lower()
        
        # Check for quiz request
        if any(term in message_lower for term in ["quiz", "test", "question", "practice"]):
            # Determine category based on message
            category = None
            if "prefix" in message_lower:
                category = "prefixes"
            elif "root" in message_lower:
                category = "roots"
            elif "suffix" in message_lower:
                category = "suffixes"
            
            # Switch to quiz mode
            self.session_state["current_mode"] = "quiz"
            self.session_state["current_category"] = category
            
            # Determine question type
            question_type = "word_part_identification"
            if "sentence" in message_lower or "complete" in message_lower:
                question_type = "sentence_completion"
            
            # Generate question
            question = self.question_engine.generate_question(
                question_type=question_type,
                category=category
            )
            
            self.session_state["current_question"] = question
            
            # Format response
            response_text = f"Great! Let's practice with some questions about {question['category'] if 'category' in question else 'vocabulary'}.\n\n"
            response_text += f"Question: {question['question']}\n\n"
            
            # Add options
            if 'options' in question:
                for option_letter, option_text in question['options'].items():
                    response_text += f"{option_letter}) {option_text}\n"
            
            # Add response to memory and conversation history
            self.memory_manager.add_message("assistant", response_text)
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response_text
            })
            
            return {
                "response": response_text,
                "question": question
            }
        
        # For other types of messages, use the LLM to generate a response
        context = self.memory_manager.get_context_for_prompt()
        response = self.openai_integration.generate_response(context)
        
        # Extract response content
        response_text = response["content"]
        
        # Add response to memory and conversation history
        self.memory_manager.add_message("assistant", response_text)
        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": response_text
        })
        
        return {"response": response_text}
    
    def _process_quiz_mode(self, message):
        """Process message in quiz mode"""
        message_lower = message.lower()
        
        # Check if user wants to exit quiz mode
        if any(term in message_lower for term in ["exit", "quit", "stop", "end quiz", "back"]):
            self.session_state["current_mode"] = "greeting"
            
            response_text = "Quiz mode ended. What would you like to do next?"
            
            # Add response to memory and conversation history
            self.memory_manager.add_message("assistant", response_text)
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response_text
            })
            
            return {"response": response_text}
        
        # Check if user is asking why
        if message_lower in ["why", "why?"]:
            if self.session_state["current_question"]:
                question_id = self.session_state["current_question"]["id"]
                explanation = self.question_engine.get_explanation(question_id)
                
                response_text = f"Let me explain why:\n\n{explanation}"
                
                # Add response to memory and conversation history
                self.memory_manager.add_message("assistant", response_text)
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response_text
                })
                
                return {"response": response_text}
            else:
                response_text = "I don't have a current question to explain. Would you like to start a new quiz?"
                
                # Add response to memory and conversation history
                self.memory_manager.add_message("assistant", response_text)
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response_text
                })
                
                return {"response": response_text}
        
        # Process answer to current question
        if self.session_state["current_question"]:
            question_id = self.session_state["current_question"]["id"]
            
            # Check if message contains an answer (A, B, C, D)
            answer = None
            if message.upper() in ["A", "B", "C", "D"]:
                answer = message.upper()
            else:
                # Try to extract answer from message
                for option in ["A", "B", "C", "D"]:
                    if f"option {option}" in message_lower or f"answer {option}" in message_lower or f"{option})" in message:
                        answer = option
                        break
            
            if answer:
                # Check answer
                result = self.question_engine.check_answer(question_id, answer)
                
                # Update session state
                if result["correct"]:
                    self.session_state["streak"] += 1
                    self.session_state["points"] += 10
                    
                    # Bonus points for streak
                    streak = self.session_state["streak"]
                    if streak >= 3:
                        self.session_state["points"] += min(streak, 10)  # Bonus capped at 10
                    
                    # Check for achievements
                    if streak == 3 and not any(a.get("title") == "Streak Starter" for a in self.session_state["achievements"]):
                        self.session_state["achievements"].append({
                            "title": "Streak Starter",
                            "description": "Answer 3 questions correctly in a row"
                        })
                    elif streak == 5 and not any(a.get("title") == "On Fire" for a in self.session_state["achievements"]):
                        self.session_state["achievements"].append({
                            "title": "On Fire",
                            "description": "Answer 5 questions correctly in a row"
                        })
                else:
                    self.session_state["streak"] = 0
                
                # Generate response
                if result["correct"]:
                    response_text = f"✅ Correct! {result['explanation']}\n\n"
                    
                    # Add points and streak information
                    response_text += f"Points: +10 (Total: {self.session_state['points']})\n"
                    
                    # Add streak information
                    if self.session_state["streak"] > 1:
                        response_text += f"🔥 Streak: {self.session_state['streak']} questions\n"
                    
                    # Add achievement if earned
                    for achievement in self.session_state["achievements"]:
                        if "shown" not in achievement:
                            response_text += f"🏆 Achievement unlocked: {achievement['title']} ({achievement['description']})\n"
                            achievement["shown"] = True
                else:
                    response_text = f"❌ That's not correct. The right answer is {result['correct_answer']}.\n\n"
                    response_text += f"{result['explanation']}\n\n"
                    response_text += f"Your streak has been reset. Keep trying!\n"
                
                # Ask if user wants another question
                response_text += f"\nWould you like another question?"
                
                # Add response to memory and conversation history
                self.memory_manager.add_message("assistant", response_text)
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response_text
                })
                
                return {
                    "response": response_text,
                    "result": result,
                    "points": self.session_state["points"],
                    "streak": self.session_state["streak"]
                }
            
            # If no answer detected, ask for clarification
            else:
                response_text = f"I didn't recognize your answer. Please respond with A, B, C, or D."
                
                # Add response to memory and conversation history
                self.memory_manager.add_message("assistant", response_text)
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response_text
                })
                
                return {"response": response_text}
        
        # If no current question, generate one
        else:
            # Determine category
            category = self.session_state.get("current_category")
            
            # Generate question
            question = self.question_engine.generate_question(
                question_type="word_part_identification",
                category=category
            )
            
            self.session_state["current_question"] = question
            
            # Format response
            response_text = f"Here's your question:\n\n"
            response_text += f"Question: {question['question']}\n\n"
            
            # Add options
            if 'options' in question:
                for option_letter, option_text in question['options'].items():
                    response_text += f"{option_letter}) {option_text}\n"
            
            # Add response to memory and conversation history
            self.memory_manager.add_message("assistant", response_text)
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response_text
            })
            
            return {
                "response": response_text,
                "question": question
            }
    
    def _process_explanation_mode(self, message):
        """Process message in explanation mode"""
        message_lower = message.lower()
        
        # Check if user wants to exit explanation mode
        if any(term in message_lower for term in ["exit", "quit", "stop", "back", "continue"]):
            # Return to quiz mode
            self.session_state["current_mode"] = "quiz"
            
            # Generate a new question
            return self._process_quiz_mode("new question")
        
        # Check if user wants a different reading level
        if any(term in message_lower for term in ["simpler", "easier", "more basic", "more advanced", "harder", "more complex"]):
            if self.session_state.get("last_explanation_question_id"):
                reading_level = 8 if any(term in message_lower for term in ["simpler", "easier", "more basic"]) else 12
                
                question_id = self.session_state["last_explanation_question_id"]
                explanation = self.question_engine.get_explanation(question_id, reading_level)
                
                response_text = f"Here's the {'simpler' if reading_level == 8 else 'more advanced'} explanation:\n\n{explanation}"
                
                # Add response to memory and conversation history
                self.memory_manager.add_message("assistant", response_text)
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response_text
                })
                
                return {"response": response_text}
        
        # For other messages, use the LLM to generate a response
        context = self.memory_manager.get_context_for_prompt()
        response = self.openai_integration.generate_response(context)
        
        # Extract response content
        response_text = response["content"]
        
        # Add response to memory and conversation history
        self.memory_manager.add_message("assistant", response_text)
        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": response_text
        })
        
        return {"response": response_text}
    
    def _process_review_mode(self, message):
        """Process message in review mode"""
        message_lower = message.lower()
        
        # Check if user wants to exit review mode
        if any(term in message_lower for term in ["exit", "quit", "stop", "end review", "back"]):
            self.session_state["current_mode"] = "greeting"
            
            response_text = f"Review mode ended. What would you like to do next?"
            
            # Add response to memory and conversation history
            self.memory_manager.add_message("assistant", response_text)
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response_text
            })
            
            return {"response": response_text}
        
        # For other messages, use the LLM to generate a response
        context = self.memory_manager.get_context_for_prompt()
        response = self.openai_integration.generate_response(context)
        
        # Extract response content
        response_text = response["content"]
        
        # Add response to memory and conversation history
        self.memory_manager.add_message("assistant", response_text)
        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": response_text
        })
        
        return {"response": response_text}
    
    def end_session(self):
        """End the current session and generate a summary"""
        if not self.session_state["active"]:
            return {"error": "No active session to end"}
        
        # Calculate session duration
        start_time = self.session_state.get("start_time", time.time())
        duration = time.time() - start_time
        duration_minutes = int(duration / 60)
        
        # Count questions answered
        questions_answered = 0
        correct_answers = 0
        for message in self.session_state["conversation_history"]:
            if message["role"] == "assistant" and "✅ Correct!" in message["content"]:
                questions_answered += 1
                correct_answers += 1
            elif message["role"] == "assistant" and "❌ That's not correct" in message["content"]:
                questions_answered += 1
        
        # Generate summary prompt
        summary_prompt = f"""
        Generate a summary of the student's session with the following information:
        - Student name: {self.user_name}
        - Session duration: {duration_minutes} minutes
        - Questions answered: {questions_answered}
        - Correct answers: {correct_answers}
        - Accuracy: {(correct_answers / questions_answered * 100) if questions_answered > 0 else 0:.0f}%
        - Points earned: {self.session_state["points"]}
        - Max streak: {self.session_state["streak"]}
        - Days until test: {self._days_until_test()}
        
        Include:
        1. A congratulatory message
        2. A summary of their performance
        3. Suggestions for what to focus on next
        4. An encouraging closing statement
        
        Keep it concise and motivating.
        """
        
        # Add summary prompt to memory
        self.memory_manager.add_message("user", summary_prompt)
        
        # Generate summary using LLM
        context = self.memory_manager.get_context_for_prompt()
        response = self.openai_integration.generate_response(context)
        
        # Extract summary content
        summary_text = response["content"]
        
        # Add summary to memory and conversation history
        self.memory_manager.add_message("assistant", summary_text)
        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": summary_text
        })
        
        # Reset session state
        self.session_state["active"] = False
        
        # Create summary object
        summary = {
            "user_name": self.user_name,
            "duration_minutes": duration_minutes,
            "questions_answered": questions_answered,
            "correct_answers": correct_answers,
            "accuracy": (correct_answers / questions_answered * 100) if questions_answered > 0 else 0,
            "points": self.session_state["points"],
            "max_streak": self.session_state["streak"],
            "achievements": self.session_state["achievements"],
            "days_until_test": self._days_until_test()
        }
        
        return {
            "response": summary_text,
            "summary": summary
        }
    
    def get_conversation_history(self):
        """Get the conversation history"""
        return self.session_state["conversation_history"]
    
    def set_user_name(self, name):
        """Set the user's name"""
        self.user_name = name
        self.user_id = name.lower().replace(" ", "_")
        self._initialize_memory()  # Reinitialize with user name
        return {"status": "success", "user_name": name}
    
    def set_test_date(self, date_str):
        """Set the SAT test date"""
        try:
            # Validate date format
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            self.test_date = date_str
            self._initialize_memory()  # Reinitialize with new test date
            return {"status": "success", "test_date": date_str}
        except ValueError:
            return {"status": "error", "message": "Invalid date format. Please use YYYY-MM-DD format."}


# Example usage
if __name__ == "__main__":
    # Initialize chatbot
    chatbot = SATTutorChatbot(user_name="Bryan")
    
    # Start session
    session_info = chatbot.start_session()
    print(f"Greeting: {session_info['greeting']}")
    
    # Process a message
    response = chatbot.process_message("Can you help me understand prefixes?")
    print(f"Response: {response['response']}")
    
    # Request a quiz
    quiz_response = chatbot.process_message("Quiz me on prefixes")
    print(f"Quiz: {quiz_response['response']}")
    
    # End session
    summary = chatbot.end_session()
    print(f"Summary: {summary['response']}")
