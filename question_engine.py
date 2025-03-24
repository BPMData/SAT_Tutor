"""
Enhanced Question Generation for SAT Reading & Writing Chatbot Tutor

This module implements the enhanced question generation system for the SAT tutor,
providing a comprehensive QuestionEngine class that leverages the OpenAI integration
to generate high-quality SAT-style questions following the detailed guidelines.
"""

import os
import json
import time
import random
from typing import List, Dict, Any, Optional, Union
from openai_integration import OpenAIIntegration

class QuestionEngine:
    """
    Enhanced question generation engine for the SAT tutor.
    """
    
    def __init__(self, openai_integration: Optional[OpenAIIntegration] = None):
        """
        Initialize the question engine.
        
        Args:
            openai_integration: Optional OpenAIIntegration instance
        """
        self.openai_integration = openai_integration or OpenAIIntegration()
        self.question_history = {}
        self.vocabulary_db = self._load_vocabulary_db()
    
    def _load_vocabulary_db(self) -> Dict[str, Any]:
        """
        Load vocabulary database from file or create a default one.
        
        Returns:
            Dictionary containing vocabulary data
        """
        db_path = "data/vocabulary/default_vocabulary.json"
        
        # Check if file exists
        if os.path.exists(db_path):
            try:
                with open(db_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading vocabulary database: {e}")
        
        # Create default vocabulary database
        return {
            "prefixes": {
                "anti-": {"meaning": "against", "examples": ["antibiotic", "antisocial"]},
                "co-": {"meaning": "with, together", "examples": ["cooperate", "coexist"]},
                "de-": {"meaning": "down, away from", "examples": ["devalue", "decrease"]},
                "dis-": {"meaning": "not, opposite of", "examples": ["disagree", "dislike"]},
                "in-": {"meaning": "not, into", "examples": ["invisible", "insert"]},
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
    
    def generate_question(
        self, 
        question_type: Optional[str] = None, 
        difficulty: int = 3, 
        category: Optional[str] = None, 
        word_part: Optional[str] = None,
        text_segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an SAT-style question based on the specified parameters.
        
        Args:
            question_type: Type of question to generate (word_part_identification, 
                          sentence_completion, context_clue_analysis, or a specific SAT domain)
            difficulty: Difficulty level (1-5)
            category: Category of word parts (prefixes, roots, suffixes)
            word_part: Specific word part to focus on
            text_segment: Optional text segment to generate a question from
            
        Returns:
            Dictionary containing the generated question data
        """
        # Map internal question types to SAT domains
        question_type_mapping = {
            "word_part_identification": "Information and Ideas",
            "sentence_completion": "Expression of Ideas",
            "context_clue_analysis": "Craft and Structure",
            "grammar": "Standard English Conventions"
        }
        
        # If text_segment is provided, use OpenAI to generate a question
        if text_segment:
            # Map internal question type to SAT domain if needed
            sat_domain = question_type
            if question_type in question_type_mapping:
                sat_domain = question_type_mapping[question_type]
            
            # Generate question using OpenAI
            question_data = self.openai_integration.generate_sat_question(text_segment, sat_domain)
            
            # Add to question history
            question_id = str(time.time())
            self.question_history[question_id] = question_data
            
            # Add ID to question data
            question_data["id"] = question_id
            
            return question_data
        
        # If no text_segment, generate a question based on vocabulary
        # This is a fallback for when we don't have a text segment
        
        # Determine category if not specified
        if not category:
            category = random.choice(["prefixes", "roots", "suffixes"])
        
        # Determine word part if not specified
        if not word_part:
            if category in self.vocabulary_db and self.vocabulary_db[category]:
                word_part = random.choice(list(self.vocabulary_db[category].keys()))
            else:
                # Default word parts if category not found
                default_word_parts = {
                    "prefixes": "un-",
                    "roots": "dict",
                    "suffixes": "-able"
                }
                word_part = default_word_parts.get(category, "un-")
        
        # Get word part data
        part_data = {}
        if category in self.vocabulary_db and word_part in self.vocabulary_db[category]:
            part_data = self.vocabulary_db[category][word_part]
        
        # Extract meaning and examples
        meaning = part_data.get("meaning", "")
        examples = part_data.get("examples", [])
        
        # Determine question type if not specified
        if not question_type:
            question_type = random.choice(["word_part_identification", "sentence_completion"])
        
        # Generate question based on type
        if question_type == "word_part_identification":
            # Create a text segment about the word part
            text_segment = self._create_word_part_text_segment(category, word_part, meaning, examples)
            
            # Generate question using OpenAI
            question_data = self.openai_integration.generate_sat_question(
                text_segment, 
                "Information and Ideas"
            )
            
        elif question_type == "sentence_completion":
            # Create a text segment with sentences using the word part
            text_segment = self._create_sentence_completion_text_segment(category, word_part, meaning, examples)
            
            # Generate question using OpenAI
            question_data = self.openai_integration.generate_sat_question(
                text_segment, 
                "Expression of Ideas"
            )
            
        else:
            # Default to word_part_identification
            text_segment = self._create_word_part_text_segment(category, word_part, meaning, examples)
            
            # Generate question using OpenAI
            question_data = self.openai_integration.generate_sat_question(
                text_segment, 
                "Information and Ideas"
            )
        
        # Add metadata
        question_data["category"] = category
        question_data["word_part"] = word_part
        question_data["difficulty"] = difficulty
        question_data["internal_type"] = question_type
        
        # Add to question history
        question_id = str(time.time())
        self.question_history[question_id] = question_data
        
        # Add ID to question data
        question_data["id"] = question_id
        
        return question_data
    
    def _create_word_part_text_segment(
        self, 
        category: str, 
        word_part: str, 
        meaning: str, 
        examples: List[str]
    ) -> str:
        """
        Create a text segment about a word part for generating questions.
        
        Args:
            category: Category of word part (prefixes, roots, suffixes)
            word_part: The specific word part
            meaning: The meaning of the word part
            examples: Example words using the word part
            
        Returns:
            A text segment about the word part
        """
        category_singular = category[:-1] if category.endswith("s") else category
        
        examples_str = ", ".join(examples)
        if examples:
            examples_str = f"Examples include {examples_str}."
        
        return f"""
        Understanding {category} is essential for vocabulary development on the SAT.
        
        The {category_singular} '{word_part}' means '{meaning}'. When added to words, it changes or enhances their meaning in specific ways. {examples_str}
        
        By recognizing this {category_singular} in unfamiliar words, students can make educated guesses about their meanings, which is a valuable skill for the SAT Reading & Writing section.
        """
    
    def _create_sentence_completion_text_segment(
        self, 
        category: str, 
        word_part: str, 
        meaning: str, 
        examples: List[str]
    ) -> str:
        """
        Create a text segment with sentences using a word part for generating questions.
        
        Args:
            category: Category of word part (prefixes, roots, suffixes)
            word_part: The specific word part
            meaning: The meaning of the word part
            examples: Example words using the word part
            
        Returns:
            A text segment with sentences using the word part
        """
        category_singular = category[:-1] if category.endswith("s") else category
        
        # Create sentences using examples
        sentences = []
        for example in examples[:3]:  # Use up to 3 examples
            sentences.append(f"The word '{example}' uses the {category_singular} '{word_part}' to indicate {meaning}.")
        
        sentences_str = " ".join(sentences)
        
        return f"""
        Effective writing requires precise word choice, which often involves understanding word parts like {category}.
        
        {sentences_str}
        
        When completing sentences on the SAT, recognizing {category} can help students select the most appropriate words to convey specific meanings and maintain clarity.
        """
    
    def check_answer(self, question_id: str, user_answer: str) -> Dict[str, Any]:
        """
        Check if the user's answer is correct.
        
        Args:
            question_id: ID of the question
            user_answer: User's answer (A, B, C, or D)
            
        Returns:
            Dictionary with results of the check
        """
        if question_id not in self.question_history:
            return {
                "correct": False,
                "explanation": "Question not found in history."
            }
        
        question_data = self.question_history[question_id]
        
        # Get correct answer
        correct_answer = question_data.get("correct_answer")
        
        # Normalize user answer (convert to uppercase letter if needed)
        if user_answer.upper() in ["A", "B", "C", "D"]:
            user_answer = user_answer.upper()
        
        # Check if the answer is correct
        is_correct = user_answer == correct_answer
        
        # Get explanation
        explanation = question_data.get("explanation", "")
        
        return {
            "correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "question_type": question_data.get("question_type"),
            "category": question_data.get("category"),
            "word_part": question_data.get("word_part")
        }
    
    def get_explanation(self, question_id: str, reading_level: int = 10) -> str:
        """
        Get an explanation for a question at the specified reading level.
        
        Args:
            question_id: ID of the question
            reading_level: Reading level (8-12)
            
        Returns:
            Explanation text
        """
        if question_id not in self.question_history:
            return "Question not found in history."
        
        question_data = self.question_history[question_id]
        base_explanation = question_data.get("explanation", "")
        
        # If reading level is the default (10), return the base explanation
        if reading_level == 10:
            return base_explanation
        
        # Otherwise, generate a new explanation at the specified reading level
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Please rewrite the following explanation at a grade {reading_level} reading level:
            
            {base_explanation}
            
            {"Make it simpler and more straightforward." if reading_level < 10 else "Use more advanced vocabulary and complex sentence structures."}
            """
            
            # Generate the explanation
            response = self.openai_integration.client.chat.completions.create(
                model=self.openai_integration.model_name,
                messages=[
                    {"role": "system", "content": f"You are an educational assistant that explains SAT questions at a grade {reading_level} reading level."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and return the explanation
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating explanation at reading level {reading_level}: {e}")
            return base_explanation
    
    def generate_practice_set(
        self, 
        num_questions: int = 5, 
        category: Optional[str] = None,
        difficulty: int = 3,
        text_passage: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a set of practice questions.
        
        Args:
            num_questions: Number of questions to generate
            category: Optional category to focus on (prefixes, roots, suffixes)
            difficulty: Difficulty level (1-5)
            text_passage: Optional text passage to generate questions from
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        # If text_passage is provided, split it into segments
        if text_passage:
            # Split the passage into paragraphs
            paragraphs = [p.strip() for p in text_passage.split("\n\n") if p.strip()]
            
            # Create segments of 1-3 paragraphs
            segments = []
            for i in range(len(paragraphs)):
                # Single paragraph
                segments.append(paragraphs[i])
                
                # Two paragraphs (if available)
                if i < len(paragraphs) - 1:
                    segments.append(paragraphs[i] + "\n\n" + paragraphs[i+1])
                
                # Three paragraphs (if available)
                if i < len(paragraphs) - 2:
                    segments.append(paragraphs[i] + "\n\n" + paragraphs[i+1] + "\n\n" + paragraphs[i+2])
            
            # Shuffle segments and select up to num_questions
            random.shuffle(segments)
            segments = segments[:num_questions]
            
            # Generate a question for each segment
            for segment in segments:
                # Determine question type (ensure distribution across domains)
                domain_options = [
                    "Information and Ideas",
                    "Craft and Structure",
                    "Expression of Ideas",
                    "Standard English Conventions"
                ]
                
                # Select domain based on position in the list to ensure distribution
                domain = domain_options[len(questions) % len(domain_options)]
                
                # Generate question
                question = self.generate_question(
                    question_type=domain,
                    difficulty=difficulty,
                    text_segment=segment
                )
                
                questions.append(question)
        
        # If no text_passage or not enough segments, generate vocabulary-based questions
        while len(questions) < num_questions:
            # Determine question type
            question_type = random.choice(["word_part_identification", "sentence_completion"])
            
            # Generate question
            question = self.generate_question(
                question_type=question_type,
                difficulty=difficulty,
                category=category
            )
            
            questions.append(question)
        
        return questions


# Example usage
if __name__ == "__main__":
    try:
        # Initialize question engine
        question_engine = QuestionEngine()
        
        # Example text segment
        text_segment = """
        The study of prefixes, roots, and suffixes is an essential component of vocabulary development. 
        By understanding these word parts, students can decode the meaning of unfamiliar words they 
        encounter in their reading. For instance, when a student knows that the prefix "un-" means "not" 
        and the suffix "-able" means "capable of being," they can deduce that "uncomfortable" means 
        "not capable of being comfortable." This analytical approach to vocabulary not only enhances 
        reading comprehension but also improves writing skills as students learn to use words more 
        precisely and effectively.
        """
        
        # Generate a question
        question = question_engine.generate_question(text_segment=text_segment)
        
        # Print the generated question
        print("Generated Question:")
        print(json.dumps(question, indent=2))
        
    except Exception as e:
        print(f"Error in example: {e}")
