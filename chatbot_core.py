"""
SAT Reading & Writing Chatbot Tutor - Core Functionality
This module implements the core chatbot functionality, integrating the adaptation engine
and practice question engine into a cohesive system.
"""

import os
import json
import time
import random
import uuid
from datetime import datetime, timedelta

class SATTutorChatbot:
    def __init__(self, user_name=None, test_date=None):
        """Initialize the SAT Tutor Chatbot with user information"""
        self.user_name = user_name
        self.test_date = test_date if test_date else (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        self.user_id = str(uuid.uuid4()) if not user_name else user_name.lower().replace(" ", "_")
        
        # Create necessary directories
        os.makedirs("data/sessions", exist_ok=True)
        os.makedirs("data/performance", exist_ok=True)
        os.makedirs("data/preferences", exist_ok=True)
        
        # Initialize components
        self.adaptation_engine = self._initialize_adaptation_engine()
        self.question_engine = self._initialize_question_engine()
        
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
    
    def _initialize_adaptation_engine(self):
        """Initialize the adaptation engine"""
        # In a real implementation, this would import the actual AdaptationEngine class
        # For this prototype, we'll create a simplified version
        
        class AdaptationEngine:
            def __init__(self, user_id):
                self.user_id = user_id
                self.performance_metrics = self._load_performance_metrics()
                self.user_preferences = self._load_user_preferences()
                self.content_difficulty = {
                    "prefixes": 3,
                    "roots": 3,
                    "suffixes": 3,
                    "questions": 3
                }
            
            def _load_performance_metrics(self):
                """Load or initialize performance metrics"""
                try:
                    with open(f"data/performance/{self.user_id}.json", "r") as f:
                        return json.load(f)
                except FileNotFoundError:
                    return {
                        "prefixes": {"mastery": {}, "accuracy": 0.0, "avg_time": 0.0},
                        "roots": {"mastery": {}, "accuracy": 0.0, "avg_time": 0.0},
                        "suffixes": {"mastery": {}, "accuracy": 0.0, "avg_time": 0.0}
                    }
            
            def _load_user_preferences(self):
                """Load or initialize user preferences"""
                try:
                    with open(f"data/preferences/{self.user_id}.json", "r") as f:
                        return json.load(f)
                except FileNotFoundError:
                    return {
                        "reading_level": 10,
                        "learning_style": "balanced",
                        "session_history": [],
                        "test_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                    }
            
            def update_performance(self, category, word_part, correct, response_time):
                """Update performance metrics based on user response"""
                if category not in self.performance_metrics:
                    self.performance_metrics[category] = {"mastery": {}, "accuracy": 0.0, "avg_time": 0.0}
                
                if word_part not in self.performance_metrics[category]["mastery"]:
                    self.performance_metrics[category]["mastery"][word_part] = {
                        "correct": 0,
                        "attempts": 0,
                        "last_seen": None,
                        "mastery_level": 0
                    }
                
                mastery_data = self.performance_metrics[category]["mastery"][word_part]
                mastery_data["attempts"] += 1
                if correct:
                    mastery_data["correct"] += 1
                mastery_data["last_seen"] = time.time()
                
                # Calculate mastery level (0-5 scale)
                accuracy = mastery_data["correct"] / mastery_data["attempts"]
                consistency = min(mastery_data["attempts"] / 5, 1.0)
                mastery_data["mastery_level"] = min(round(accuracy * 5 * consistency), 5)
                
                # Update category-level metrics
                total_correct = sum(item["correct"] for item in self.performance_metrics[category]["mastery"].values())
                total_attempts = sum(item["attempts"] for item in self.performance_metrics[category]["mastery"].values())
                self.performance_metrics[category]["accuracy"] = total_correct / total_attempts if total_attempts > 0 else 0.0
                
                # Save updated metrics
                self._save_performance_metrics()
                
                # Adjust difficulty based on new performance
                self._adjust_difficulty(category)
                
                return mastery_data["mastery_level"]
            
            def _adjust_difficulty(self, category):
                """Adjust difficulty level based on performance"""
                accuracy = self.performance_metrics[category]["accuracy"]
                
                if accuracy > 0.85:
                    self.content_difficulty[category] = min(self.content_difficulty[category] + 1, 5)
                elif accuracy < 0.60:
                    self.content_difficulty[category] = max(self.content_difficulty[category] - 1, 1)
            
            def _save_performance_metrics(self):
                """Save performance metrics to file"""
                with open(f"data/performance/{self.user_id}.json", "w") as f:
                    json.dump(self.performance_metrics, f)
            
            def _save_user_preferences(self):
                """Save user preferences to file"""
                with open(f"data/preferences/{self.user_id}.json", "w") as f:
                    json.dump(self.user_preferences, f)
            
            def get_next_word_part(self, category):
                """Determine the next word part to present to the user"""
                if category not in self.performance_metrics:
                    return self._get_beginner_word_part(category)
                
                word_parts = list(self.performance_metrics[category]["mastery"].keys())
                
                if not word_parts:
                    return self._get_beginner_word_part(category)
                
                # For simplicity, we'll just return a random word part
                # In a real implementation, this would use the algorithm from adaptation_engine_logic.md
                return random.choice(word_parts)
            
            def _get_beginner_word_part(self, category):
                """Get a beginner-level word part for the category"""
                beginner_word_parts = {
                    "prefixes": "un-",
                    "roots": "dict",
                    "suffixes": "-able"
                }
                return beginner_word_parts.get(category, "")
            
            def get_question_difficulty(self):
                """Get the current question difficulty level"""
                return self.content_difficulty["questions"]
            
            def adjust_reading_level(self, requested_level=None):
                """Adjust the reading level for explanations"""
                if requested_level is not None:
                    self.user_preferences["reading_level"] = max(8, min(12, requested_level))
                    self._save_user_preferences()
                return self.user_preferences["reading_level"]
            
            def get_reading_level(self):
                """Get the current reading level for explanations"""
                return self.user_preferences["reading_level"]
            
            def get_weak_areas(self):
                """Identify weak areas that need more focus"""
                weak_areas = []
                
                for category in ["prefixes", "roots", "suffixes"]:
                    if category in self.performance_metrics:
                        for word_part, data in self.performance_metrics[category]["mastery"].items():
                            if data["attempts"] >= 2 and data["mastery_level"] <= 2:
                                weak_areas.append({
                                    "category": category,
                                    "word_part": word_part,
                                    "mastery_level": data["mastery_level"],
                                    "accuracy": data["correct"] / data["attempts"] if data["attempts"] > 0 else 0
                                })
                
                # Sort by mastery level (ascending) and then by accuracy (ascending)
                weak_areas.sort(key=lambda x: (x["mastery_level"], x["accuracy"]))
                return weak_areas
            
            def calculate_category_progress(self, category):
                """Calculate progress percentage for a category"""
                if category not in self.performance_metrics:
                    return 0
                
                mastery_data = self.performance_metrics[category]["mastery"]
                if not mastery_data:
                    return 0
                
                # Count word parts with mastery level 3 or higher
                mastered_count = sum(1 for data in mastery_data.values() if data["mastery_level"] >= 3)
                total_count = len(mastery_data)
                
                return (mastered_count / total_count) * 100 if total_count > 0 else 0
            
            def get_days_until_test(self):
                """Calculate days until the SAT test"""
                test_date_str = self.user_preferences.get("test_date")
                if not test_date_str:
                    return 14  # Default to 14 days
                
                try:
                    test_date = datetime.strptime(test_date_str, "%Y-%m-%d")
                    days_remaining = (test_date - datetime.now()).days
                    return max(0, days_remaining)
                except ValueError:
                    return 14  # Default to 14 days if date format is invalid
            
            def set_test_date(self, date_str):
                """Set the SAT test date"""
                try:
                    # Validate date format
                    datetime.strptime(date_str, "%Y-%m-%d")
                    self.user_preferences["test_date"] = date_str
                    self._save_user_preferences()
                    return True
                except ValueError:
                    return False
        
        return AdaptationEngine(self.user_id)
    
    def _initialize_question_engine(self):
        """Initialize the question engine"""
        # In a real implementation, this would import the actual QuestionEngine class
        # For this prototype, we'll create a simplified version
        
        class QuestionEngine:
            def __init__(self):
                self.vocabulary_db = self._load_vocabulary_db()
                self.question_history = {}
            
            def _load_vocabulary_db(self):
                """Load vocabulary database"""
                # For simplicity, we'll use a small hardcoded database
                # In a real implementation, this would load from a JSON file
                return {
                    "prefixes": {
                        "anti-": {"meaning": "against", "examples": ["antibiotic", "antisocial"]},
                        "co-": {"meaning": "with, together", "examples": ["cooperate", "coexist"]},
                        "de-": {"meaning": "down, away from", "examples": ["devalue", "decrease"]},
                        "dis-": {"meaning": "not, opposite of", "examples": ["disagree", "dislike"]},
                        "un-": {"meaning": "not", "examples": ["unhappy", "unable"]}
                    },
                    "roots": {
                        "dict": {"meaning": "to say", "examples": ["dictate", "predict"]},
                        "bio": {"meaning": "life", "examples": ["biology", "biography"]},
                        "scrib": {"meaning": "to write", "examples": ["describe", "manuscript"]}
                    },
                    "suffixes": {
                        "-able": {"meaning": "capable of being", "examples": ["readable", "flexible"]},
                        "-ment": {"meaning": "action or process", "examples": ["development", "statement"]},
                        "-ful": {"meaning": "full of", "examples": ["beautiful", "helpful"]}
                    }
                }
            
            def generate_question(self, question_type, difficulty=3, category=None, word_part=None):
                """Generate a question based on specified parameters"""
                if category is None:
                    category = random.choice(["prefixes", "roots", "suffixes"])
                
                if word_part is None:
                    if category == "prefixes":
                        word_part = random.choice(list(self.vocabulary_db["prefixes"].keys()))
                    elif category == "roots":
                        word_part = random.choice(list(self.vocabulary_db["roots"].keys()))
                    elif category == "suffixes":
                        word_part = random.choice(list(self.vocabulary_db["suffixes"].keys()))
                
                # Get word part data
                if category == "prefixes" and word_part in self.vocabulary_db["prefixes"]:
                    part_data = self.vocabulary_db["prefixes"][word_part]
                elif category == "roots" and word_part in self.vocabulary_db["roots"]:
                    part_data = self.vocabulary_db["roots"][word_part]
                elif category == "suffixes" and word_part in self.vocabulary_db["suffixes"]:
                    part_data = self.vocabulary_db["suffixes"][word_part]
                else:
                    # Default to a prefix if not found
                    category = "prefixes"
                    word_part = list(self.vocabulary_db["prefixes"].keys())[0]
                    part_data = self.vocabulary_db["prefixes"][word_part]
                
                meaning = part_data.get("meaning", "")
                examples = part_data.get("examples", [])
                
                # Generate question based on type
                if question_type == "word_part_identification":
                    question_text = f"What does the {category[:-1]} '{word_part}' mean?"
                    options = [
                        f"A) {meaning}",  # Correct answer
                        f"B) opposite of {meaning}",
                        f"C) related to {meaning}",
                        f"D) similar to {meaning} but stronger"
                    ]
                    correct_answer = "A"
                    explanation = f"The {category[:-1]} '{word_part}' means '{meaning}'. Examples include: {', '.join(examples)}."
                
                elif question_type == "sentence_completion":
                    if category == "prefixes":
                        question_text = f"The scientist's theory was so ____________ that even his colleagues couldn't understand it."
                        options = [
                            "A) incomprehensible",  # Correct answer
                            "B) interchangeable",
                            "C) international",
                            "D) introverted"
                        ]
                        correct_answer = "A"
                        explanation = f"'Incomprehensible' is the right answer. The prefix 'in-' means 'not', and 'comprehensible' means 'able to be understood'. So 'incomprehensible' means 'not able to be understood', which fits the context."
                    
                    elif category == "roots":
                        question_text = f"The ____________ of the ancient manuscript revealed information about early civilizations."
                        options = [
                            "A) description",  # Correct answer
                            "B) prescription",
                            "C) subscription",
                            "D) conscription"
                        ]
                        correct_answer = "A"
                        explanation = f"'Description' is the right answer. It contains the root 'script' which means 'to write'. A description is a written account of something."
                    
                    else:  # suffixes
                        question_text = f"The student found the assignment ____________; it required very little effort."
                        options = [
                            "A) manageable",  # Correct answer
                            "B) management",
                            "C) manager",
                            "D) managed"
                        ]
                        correct_answer = "A"
                        explanation = f"'Manageable' is the right answer. The suffix '-able' means 'capable of being', so 'manageable' means 'capable of being managed', which fits the context of something requiring little effort."
                
                else:  # Default to word_part_identification
                    question_text = f"What does the {category[:-1]} '{word_part}' mean?"
                    options = [
                        f"A) {meaning}",  # Correct answer
                        f"B) opposite of {meaning}",
                        f"C) related to {meaning}",
                        f"D) similar to {meaning} but stronger"
                    ]
                    correct_answer = "A"
                    explanation = f"The {category[:-1]} '{word_part}' means '{meaning}'. Examples include: {', '.join(examples)}."
                
                # Create question ID and store in history
                question_id = str(uuid.uuid4())
                self.question_history[question_id] = {
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": explanation,
                    "category": category,
                    "word_part": word_part,
                    "difficulty": difficulty,
                    "type": question_type,
                    "timestamp": time.time()
                }
                
                return {
                    "id": question_id,
                    "question": question_text,
                    "options": options,
                    "category": category,
                    "word_part": word_part,
                    "difficulty": difficulty,
                    "type": question_type
                }
            
            def check_answer(self, question_id, user_answer):
                """Check if the user's answer is correct"""
                if question_id not in self.question_history:
                    return {
                        "correct": False,
                        "explanation": "Question not found in history."
                    }
                
                question_data = self.question_history[question_id]
                correct_answer = question_data["correct_answer"]
                
                # Normalize user answer (convert to uppercase letter if needed)
                if user_answer.upper() in ["A", "B", "C", "D"]:
                    user_answer = user_answer.upper()
                
                # Check if the answer is correct
                is_correct = user_answer == correct_answer
                
                return {
                    "correct": is_correct,
                    "correct_answer": correct_answer,
                    "explanation": question_data["explanation"],
                    "category": question_data["category"],
                    "word_part": question_data["word_part"]
                }
            
            def get_explanation(self, question_id, reading_level=10):
                """Get an explanation for a question at the specified reading level"""
                if question_id not in self.question_history:
                    return "Question not found in history."
                
                question_data = self.question_history[question_id]
                base_explanation = question_data["explanation"]
                
                # Adjust explanation based on reading level
                if reading_level <= 8:
                    # Simplify for 8th grade level
                    return f"Simple explanation: {base_explanation}"
                elif reading_level >= 12:
                    # Enhance for 12th grade level
                    return f"Advanced explanation: {base_explanation} This word part has important applications in academic and professional contexts."
                else:
                    # Default to original explanation (10th grade level)
                    return base_explanation
        
        return QuestionEngine()
    
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
        
        # Generate greeting message
        days_until_test = self.adaptation_engine.get_days_until_test()
        greeting = f"Hi, {self.user_name}! 👋 Welcome back to your SAT Reading & Writing prep session. You have {days_until_test} days until test day!"
        
        # Get progress information
        prefix_progress = self.adaptation_engine.calculate_category_progress("prefixes")
        root_progress = self.adaptation_engine.calculate_category_progress("roots")
        suffix_progress = self.adaptation_engine.calculate_category_progress("suffixes")
        
        # Add progress information to greeting
        progress_info = f"Your current progress:\n- Prefixes: {prefix_progress:.0f}% mastered\n- Roots: {root_progress:.0f}% mastered\n- Suffixes: {suffix_progress:.0f}% mastered"
        
        # Suggest focus area
        weak_areas = self.adaptation_engine.get_weak_areas()
        if weak_areas:
            weakest = weak_areas[0]
            suggestion = f"I suggest we focus on {weakest['category']} today, especially '{weakest['word_part']}'."
        else:
            lowest_progress = min([
                ("prefixes", prefix_progress),
                ("roots", root_progress),
                ("suffixes", suffix_progress)
            ], key=lambda x: x[1])
            suggestion = f"I suggest we focus on {lowest_progress[0]} today to build your foundation."
        
        # Add to conversation history
        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": f"{greeting}\n\n{progress_info}\n\n{suggestion}\n\nWhat would you like to do today?"
        })
        
        return {
            "greeting": greeting,
            "progress_info": progress_info,
            "suggestion": suggestion,
            "days_until_test": days_until_test
        }
    
    def process_message(self, message):
        """Process a user message and generate a response"""
        # Add user message to conversation history
        self.session_state["conversation_history"].append({
            "role": "user",
            "content": message
        })
        
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
                                break
                
                if not self.user_name:
                    response = "I'd be happy to help you prepare for the SAT Reading & Writing section! Could you tell me your name so I can personalize your experience?"
                    self.session_state["conversation_history"].append({
                        "role": "assistant",
                        "content": response
                    })
                    return {"response": response}
            
            # Start session with user name
            session_info = self.start_session()
            response = f"{session_info['greeting']}\n\n{session_info['progress_info']}\n\n{session_info['suggestion']}\n\nWhat would you like to do today?"
            return {"response": response}
        
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
            
            # Switch to quiz mode and generate first question
            self.session_state["current_mode"] = "quiz"
            self.session_state["current_category"] = category
            
            # Generate question
            question_type = "word_part_identification"
            if "sentence" in message_lower or "complete" in message_lower:
                question_type = "sentence_completion"
            
            difficulty = self.adaptation_engine.get_question_difficulty()
            
            if category:
                # Get a specific word part if needed
                word_part = None
                if self.adaptation_engine.get_weak_areas():
                    for area in self.adaptation_engine.get_weak_areas():
                        if area["category"] == category:
                            word_part = area["word_part"]
                            break
                
                question = self.question_engine.generate_question(
                    question_type=question_type,
                    difficulty=difficulty,
                    category=category,
                    word_part=word_part
                )
            else:
                question = self.question_engine.generate_question(
                    question_type=question_type,
                    difficulty=difficulty
                )
            
            self.session_state["current_question"] = question
            
            # Format response
            response = f"Great! Let's practice with some questions about {question['category']}.\n\n"
            response += f"Question: {question['question']}\n\n"
            for option in question['options']:
                response += f"{option}\n"
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {
                "response": response,
                "question": question
            }
        
        # Check for reading level adjustment
        elif any(term in message_lower for term in ["reading level", "simpler", "easier to understand", "more advanced"]):
            new_level = None
            if any(term in message_lower for term in ["simpler", "easier", "basic", "elementary"]):
                new_level = 8
            elif any(term in message_lower for term in ["advanced", "harder", "complex", "college"]):
                new_level = 12
            
            if new_level:
                self.adaptation_engine.adjust_reading_level(new_level)
                response = f"I've adjusted the reading level to make explanations {'simpler' if new_level == 8 else 'more advanced'} for you."
            else:
                current_level = self.adaptation_engine.get_reading_level()
                response = f"Your current reading level is set to grade {current_level}. Would you like me to make explanations simpler or more advanced?"
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {"response": response}
        
        # Check for test date adjustment
        elif any(term in message_lower for term in ["test date", "exam date", "sat date"]):
            # Try to extract date from message
            import re
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
                r'(\w+ \d{1,2},? \d{4})'  # Month DD, YYYY
            ]
            
            extracted_date = None
            for pattern in date_patterns:
                match = re.search(pattern, message)
                if match:
                    date_str = match.group(1)
                    try:
                        if '/' in date_str:
                            # Convert MM/DD/YYYY to YYYY-MM-DD
                            parts = date_str.split('/')
                            extracted_date = f"{parts[2]}-{parts[0]}-{parts[1]}"
                        elif ',' in date_str or ' ' in date_str:
                            # Convert Month DD, YYYY to YYYY-MM-DD
                            parsed_date = datetime.strptime(date_str, "%B %d, %Y" if ',' in date_str else "%B %d %Y")
                            extracted_date = parsed_date.strftime("%Y-%m-%d")
                        else:
                            # Already in YYYY-MM-DD format
                            extracted_date = date_str
                        break
                    except ValueError:
                        continue
            
            if extracted_date and self.adaptation_engine.set_test_date(extracted_date):
                days_until_test = self.adaptation_engine.get_days_until_test()
                response = f"I've updated your SAT test date. You now have {days_until_test} days until the test!"
            else:
                response = f"I couldn't identify a valid date in your message. Please provide your SAT test date in YYYY-MM-DD format (e.g., 2025-05-15)."
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {"response": response}
        
        # Check for progress request
        elif any(term in message_lower for term in ["progress", "how am i doing", "my status", "my performance"]):
            prefix_progress = self.adaptation_engine.calculate_category_progress("prefixes")
            root_progress = self.adaptation_engine.calculate_category_progress("roots")
            suffix_progress = self.adaptation_engine.calculate_category_progress("suffixes")
            
            response = f"Here's your current progress:\n\n"
            response += f"📊 Progress Report:\n"
            response += f"- Prefixes: {prefix_progress:.0f}% mastered\n"
            response += f"- Roots: {root_progress:.0f}% mastered\n"
            response += f"- Suffixes: {suffix_progress:.0f}% mastered\n\n"
            
            # Add weak areas if any
            weak_areas = self.adaptation_engine.get_weak_areas()
            if weak_areas:
                response += f"Areas that need more focus:\n"
                for i, area in enumerate(weak_areas[:3]):  # Show top 3 weak areas
                    response += f"- {area['category'].capitalize()}: '{area['word_part']}'\n"
                response += "\n"
            
            # Add days until test
            days_until_test = self.adaptation_engine.get_days_until_test()
            response += f"⏰ Days until your SAT: {days_until_test}\n\n"
            
            response += f"Would you like to practice with some questions to improve your mastery?"
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {"response": response}
        
        # Check for help request
        elif any(term in message_lower for term in ["help", "what can you do", "how does this work", "instructions"]):
            response = f"I'm your SAT Reading & Writing tutor, focused on helping you master prefixes, roots, and suffixes. Here's what I can do:\n\n"
            response += f"1. Quiz you on word parts (prefixes, roots, suffixes)\n"
            response += f"2. Provide practice with SAT-style sentence completion questions\n"
            response += f"3. Explain answers at different reading levels (grades 8-12)\n"
            response += f"4. Track your progress and identify areas that need more focus\n"
            response += f"5. Adjust to your performance and prioritize what you need to learn\n\n"
            
            response += f"To get started, you can say things like:\n"
            response += f"- \"Quiz me on prefixes\"\n"
            response += f"- \"I want to practice sentence completion\"\n"
            response += f"- \"Show me my progress\"\n"
            response += f"- \"Make explanations simpler\"\n\n"
            
            response += f"What would you like to do today?"
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {"response": response}
        
        # Default response for greeting mode
        else:
            response = f"I'm here to help you prepare for the SAT Reading & Writing section! Would you like to:\n\n"
            response += f"1. Practice with prefix questions\n"
            response += f"2. Practice with root questions\n"
            response += f"3. Practice with suffix questions\n"
            response += f"4. Try sentence completion questions\n"
            response += f"5. Check your progress\n\n"
            
            response += f"Just let me know what you'd like to do!"
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {"response": response}
    
    def _process_quiz_mode(self, message):
        """Process message in quiz mode"""
        message_lower = message.lower()
        
        # Check if user wants to exit quiz mode
        if any(term in message_lower for term in ["exit", "quit", "stop", "end quiz", "back"]):
            self.session_state["current_mode"] = "greeting"
            
            response = f"Quiz mode ended. What would you like to do next?"
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {"response": response}
        
        # Check if user is asking why
        if message_lower in ["why", "why?"]:
            if self.session_state["current_question"]:
                question_id = self.session_state["current_question"]["id"]
                reading_level = self.adaptation_engine.get_reading_level()
                explanation = self.question_engine.get_explanation(question_id, reading_level)
                
                response = f"Let me explain why:\n\n{explanation}"
                
                # Add to conversation history
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response
                })
                
                return {"response": response}
            else:
                response = f"I don't have a current question to explain. Would you like to start a new quiz?"
                
                # Add to conversation history
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response
                })
                
                return {"response": response}
        
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
                start_time = self.session_state.get("question_start_time", time.time() - 10)  # Default to 10 seconds if not set
                response_time = time.time() - start_time
                
                result = self.question_engine.check_answer(question_id, answer)
                
                # Update adaptation engine with result
                category = result["category"]
                word_part = result["word_part"]
                mastery_level = self.adaptation_engine.update_performance(
                    category=category,
                    word_part=word_part,
                    correct=result["correct"],
                    response_time=response_time
                )
                
                # Update session state
                if result["correct"]:
                    self.session_state["streak"] += 1
                    self.session_state["points"] += 10
                    
                    # Bonus points for streak
                    streak = self.session_state["streak"]
                    if streak >= 3:
                        self.session_state["points"] += min(streak, 10)  # Bonus capped at 10
                    
                    # Check for achievements
                    if streak == 3:
                        self.session_state["achievements"].append({
                            "title": "Streak Starter",
                            "description": "Answer 3 questions correctly in a row"
                        })
                    elif streak == 5:
                        self.session_state["achievements"].append({
                            "title": "On Fire",
                            "description": "Answer 5 questions correctly in a row"
                        })
                else:
                    self.session_state["streak"] = 0
                
                # Generate response
                if result["correct"]:
                    response = f"✅ Correct! {result['explanation']}\n\n"
                    response += f"Your {category[:-1]} mastery: {'⭐' * mastery_level} ({mastery_level}/5)\n"
                    response += f"Points: +10 (Total: {self.session_state['points']})\n"
                    
                    # Add streak information
                    if self.session_state["streak"] > 1:
                        response += f"🔥 Streak: {self.session_state['streak']} questions\n"
                    
                    # Add achievement if earned
                    for achievement in self.session_state["achievements"]:
                        if "shown" not in achievement:
                            response += f"🏆 Achievement unlocked: {achievement['title']} ({achievement['description']})\n"
                            achievement["shown"] = True
                else:
                    response = f"❌ That's not correct. The right answer is {result['correct_answer']}.\n\n"
                    response += f"{result['explanation']}\n\n"
                    response += f"Your streak has been reset. Keep trying!\n"
                
                # Ask if user wants another question
                response += f"\nWould you like another question?"
                
                # Add to conversation history
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response
                })
                
                return {
                    "response": response,
                    "result": result,
                    "mastery_level": mastery_level,
                    "points": self.session_state["points"],
                    "streak": self.session_state["streak"]
                }
            
            # If no answer detected, ask for clarification
            else:
                response = f"I didn't recognize your answer. Please respond with A, B, C, or D."
                
                # Add to conversation history
                self.session_state["conversation_history"].append({
                    "role": "assistant",
                    "content": response
                })
                
                return {"response": response}
        
        # If no current question, generate one
        else:
            # Determine category
            category = self.session_state.get("current_category")
            
            # Generate question
            difficulty = self.adaptation_engine.get_question_difficulty()
            question = self.question_engine.generate_question(
                question_type="word_part_identification",
                difficulty=difficulty,
                category=category
            )
            
            self.session_state["current_question"] = question
            self.session_state["question_start_time"] = time.time()
            
            # Format response
            response = f"Here's your question:\n\n"
            response += f"Question: {question['question']}\n\n"
            for option in question['options']:
                response += f"{option}\n"
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {
                "response": response,
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
                new_level = None
                if any(term in message_lower for term in ["simpler", "easier", "more basic"]):
                    new_level = 8
                elif any(term in message_lower for term in ["more advanced", "harder", "more complex"]):
                    new_level = 12
                
                if new_level:
                    self.adaptation_engine.adjust_reading_level(new_level)
                    question_id = self.session_state["last_explanation_question_id"]
                    explanation = self.question_engine.get_explanation(question_id, new_level)
                    
                    response = f"Here's the {'simpler' if new_level == 8 else 'more advanced'} explanation:\n\n{explanation}"
                    
                    # Add to conversation history
                    self.session_state["conversation_history"].append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    return {"response": response}
            
            # If no last explanation, return to quiz mode
            self.session_state["current_mode"] = "quiz"
            return self._process_quiz_mode("new question")
        
        # Default: return to quiz mode
        self.session_state["current_mode"] = "quiz"
        return self._process_quiz_mode("new question")
    
    def _process_review_mode(self, message):
        """Process message in review mode"""
        message_lower = message.lower()
        
        # Check if user wants to exit review mode
        if any(term in message_lower for term in ["exit", "quit", "stop", "end review", "back"]):
            self.session_state["current_mode"] = "greeting"
            
            response = f"Review mode ended. What would you like to do next?"
            
            # Add to conversation history
            self.session_state["conversation_history"].append({
                "role": "assistant",
                "content": response
            })
            
            return {"response": response}
        
        # Default: show progress and return to greeting mode
        prefix_progress = self.adaptation_engine.calculate_category_progress("prefixes")
        root_progress = self.adaptation_engine.calculate_category_progress("roots")
        suffix_progress = self.adaptation_engine.calculate_category_progress("suffixes")
        
        response = f"Here's your current progress:\n\n"
        response += f"📊 Progress Report:\n"
        response += f"- Prefixes: {prefix_progress:.0f}% mastered\n"
        response += f"- Roots: {root_progress:.0f}% mastered\n"
        response += f"- Suffixes: {suffix_progress:.0f}% mastered\n\n"
        
        # Add weak areas if any
        weak_areas = self.adaptation_engine.get_weak_areas()
        if weak_areas:
            response += f"Areas that need more focus:\n"
            for i, area in enumerate(weak_areas[:3]):  # Show top 3 weak areas
                response += f"- {area['category'].capitalize()}: '{area['word_part']}'\n"
            response += "\n"
        
        # Add session stats
        response += f"📊 Session Stats:\n"
        response += f"- Points earned: {self.session_state['points']}\n"
        response += f"- Max streak: {self.session_state['streak']}\n"
        
        # Add achievements
        if self.session_state["achievements"]:
            response += f"\n🏆 Achievements:\n"
            for achievement in self.session_state["achievements"]:
                response += f"- {achievement['title']}: {achievement['description']}\n"
        
        # Add days until test
        days_until_test = self.adaptation_engine.get_days_until_test()
        response += f"\n⏰ Days until your SAT: {days_until_test}\n\n"
        
        response += f"What would you like to do next?"
        
        # Switch back to greeting mode
        self.session_state["current_mode"] = "greeting"
        
        # Add to conversation history
        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": response
        })
        
        return {"response": response}
    
    def end_session(self):
        """End the current session and generate a summary"""
        if not self.session_state["active"]:
            return {"error": "No active session to end"}
        
        # Calculate session duration
        start_time = self.session_state.get("start_time", time.time())
        duration = time.time() - start_time
        duration_minutes = int(duration / 60)
        
        # Get progress information
        prefix_progress = self.adaptation_engine.calculate_category_progress("prefixes")
        root_progress = self.adaptation_engine.calculate_category_progress("roots")
        suffix_progress = self.adaptation_engine.calculate_category_progress("suffixes")
        
        # Count questions answered
        questions_answered = 0
        correct_answers = 0
        for message in self.session_state["conversation_history"]:
            if message["role"] == "assistant" and "✅ Correct!" in message["content"]:
                questions_answered += 1
                correct_answers += 1
            elif message["role"] == "assistant" and "❌ That's not correct" in message["content"]:
                questions_answered += 1
        
        # Generate summary
        summary = {
            "user_name": self.user_name,
            "duration_minutes": duration_minutes,
            "questions_answered": questions_answered,
            "correct_answers": correct_answers,
            "accuracy": (correct_answers / questions_answered * 100) if questions_answered > 0 else 0,
            "points": self.session_state["points"],
            "max_streak": self.session_state["streak"],
            "achievements": self.session_state["achievements"],
            "progress": {
                "prefixes": prefix_progress,
                "roots": root_progress,
                "suffixes": suffix_progress
            },
            "days_until_test": self.adaptation_engine.get_days_until_test()
        }
        
        # Generate response message
        response = f"Great job today, {self.user_name}! Here's a summary of your session:\n\n"
        response += f"📊 Session Stats:\n"
        response += f"- Questions answered: {questions_answered}\n"
        response += f"- Correct answers: {correct_answers} ({summary['accuracy']:.0f}%)\n"
        response += f"- Points earned: {summary['points']}\n"
        response += f"- Streak: {summary['max_streak']} questions\n"
        response += f"- Time spent: {duration_minutes} minutes\n\n"
        
        # Add achievements
        if summary["achievements"]:
            response += f"🏆 Achievements:\n"
            for achievement in summary["achievements"]:
                response += f"- {achievement['title']}: {achievement['description']}\n"
            response += "\n"
        
        # Add progress
        response += f"📈 Progress:\n"
        response += f"- Prefixes: {prefix_progress:.0f}% mastered\n"
        response += f"- Roots: {root_progress:.0f}% mastered\n"
        response += f"- Suffixes: {suffix_progress:.0f}% mastered\n\n"
        
        # Add recommended focus
        weak_areas = self.adaptation_engine.get_weak_areas()
        if weak_areas:
            response += f"📝 Recommended focus for next time:\n"
            for i, area in enumerate(weak_areas[:2]):  # Show top 2 weak areas
                response += f"- {area['category'].capitalize()} related to '{area['word_part']}'\n"
            response += "\n"
        
        # Add days until test
        response += f"⏰ Remember: {summary['days_until_test']} days until your SAT!\n\n"
        
        response += f"Session ended. I'll see you next time for more SAT prep. Remember, consistent practice is key to success! 💪"
        
        # Add to conversation history
        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": response
        })
        
        # Reset session state
        self.session_state["active"] = False
        
        return {
            "response": response,
            "summary": summary
        }
    
    def get_conversation_history(self):
        """Get the conversation history"""
        return self.session_state["conversation_history"]
    
    def set_user_name(self, name):
        """Set the user's name"""
        self.user_name = name
        self.user_id = name.lower().replace(" ", "_")
        return {"status": "success", "user_name": name}
    
    def set_test_date(self, date_str):
        """Set the SAT test date"""
        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
            self.test_date = date_str
            self.adaptation_engine.set_test_date(date_str)
            return {"status": "success", "test_date": date_str}
        except ValueError:
            return {"status": "error", "message": "Invalid date format. Please use YYYY-MM-DD format."}
