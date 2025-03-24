"""
Test script for the enhanced SAT Reading & Writing Chatbot Tutor

This script tests the integration of all components of the enhanced chatbot tutor:
- Memory Manager
- OpenAI Integration
- Question Engine
- Enhanced Chatbot Core
"""

import os
import json
import time
import unittest
from unittest.mock import patch, MagicMock

# Import components
from memory_manager import MemoryManager, TokenCounter, VectorDatabase
from openai_integration import OpenAIIntegration
from question_engine import QuestionEngine
from enhanced_chatbot_core import SATTutorChatbot

class MockOpenAIResponse:
    """Mock class for OpenAI API responses"""
    
    def __init__(self, content, usage=None):
        self.choices = [MagicMock(message=MagicMock(content=content))]
        self.usage = usage or MagicMock(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )

class MockEmbeddingResponse:
    """Mock class for OpenAI embedding responses"""
    
    def __init__(self, embedding):
        self.data = [MagicMock(embedding=embedding)]

class TestMemoryManager(unittest.TestCase):
    """Test the MemoryManager component"""
    
    def setUp(self):
        """Set up test environment"""
        self.memory_manager = MemoryManager(
            max_tokens=1000,
            model_name="gpt-4o",
            db_path="test_data/test_memory.db",
            embedding_dimension=4  # Small dimension for testing
        )
    
    def test_add_message(self):
        """Test adding messages to short-term memory"""
        # Clear existing messages
        self.memory_manager.short_term_memory = []
        
        # Add a message
        self.memory_manager.add_message("user", "Test message")
        
        # Check if message was added
        self.assertEqual(len(self.memory_manager.short_term_memory), 1)
        self.assertEqual(self.memory_manager.short_term_memory[0]["role"], "user")
        self.assertEqual(self.memory_manager.short_term_memory[0]["content"], "Test message")
    
    def test_get_context_for_prompt(self):
        """Test getting context for prompt"""
        # Clear existing messages
        self.memory_manager.short_term_memory = []
        
        # Add messages
        self.memory_manager.add_message("system", "System message")
        self.memory_manager.add_message("user", "User message")
        
        # Get context
        context = self.memory_manager.get_context_for_prompt()
        
        # Check context
        self.assertIn("system_instructions", context)
        self.assertIn("short_term_memory", context)
        self.assertIn("relevant_chunks", context)
        self.assertIn("user_query", context)
        
        # Check messages in context
        self.assertEqual(len(context["short_term_memory"]), 2)
        self.assertEqual(context["short_term_memory"][0]["role"], "system")
        self.assertEqual(context["short_term_memory"][1]["role"], "user")
    
    def test_prune_short_term_memory(self):
        """Test pruning short-term memory"""
        # Mock token counter to always return a large number
        self.memory_manager.token_counter.count_message_tokens = MagicMock(return_value=2000)
        
        # Add messages
        self.memory_manager.short_term_memory = []
        self.memory_manager.add_message("system", "System message")
        self.memory_manager.add_message("user", "User message 1")
        self.memory_manager.add_message("assistant", "Assistant message 1")
        self.memory_manager.add_message("user", "User message 2")
        
        # Initial count
        initial_count = len(self.memory_manager.short_term_memory)
        
        # Prune memory
        self.memory_manager.prune_short_term_memory()
        
        # Check if memory was pruned
        self.assertLess(len(self.memory_manager.short_term_memory), initial_count)


class TestOpenAIIntegration(unittest.TestCase):
    """Test the OpenAIIntegration component"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a mock OpenAI client
        mock_client = MagicMock()
        
        # Mock the chat.completions.create method
        mock_client.chat.completions.create.return_value = MockOpenAIResponse(
            content='{"response_type": "text", "content": "Test response"}'
        )
        
        # Mock the embeddings.create method
        mock_client.embeddings.create.return_value = MockEmbeddingResponse(
            embedding=[0.1, 0.2, 0.3, 0.4]
        )
        
        # Create OpenAIIntegration with mock client
        self.openai_integration = OpenAIIntegration()
        self.openai_integration.client = mock_client
    
    def test_create_embedding(self):
        """Test creating embeddings"""
        embedding = self.openai_integration.create_embedding("Test text")
        
        # Check if embedding was created
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding), 4)
    
    def test_generate_response(self):
        """Test generating responses"""
        context = {
            "system_instructions": "System instructions",
            "short_term_memory": [
                {"role": "user", "content": "User message"}
            ],
            "relevant_chunks": [],
            "user_query": "User query"
        }
        
        response = self.openai_integration.generate_response(context)
        
        # Check response
        self.assertIn("content", response)
        self.assertIn("response_type", response)
        self.assertIn("raw_response", response)
        self.assertIn("usage", response)
    
    def test_generate_sat_question(self):
        """Test generating SAT questions"""
        # Mock the response for question generation
        self.openai_integration.client.chat.completions.create.return_value = MockOpenAIResponse(
            content=json.dumps({
                "question_type": "Information and Ideas",
                "question": "Test question",
                "passage": "Test passage",
                "options": {
                    "A": "Option A",
                    "B": "Option B",
                    "C": "Option C",
                    "D": "Option D"
                },
                "correct_answer": "A",
                "explanation": "Test explanation"
            })
        )
        
        question = self.openai_integration.generate_sat_question("Test text segment")
        
        # Check question
        self.assertIn("question_type", question)
        self.assertIn("question", question)
        self.assertIn("options", question)
        self.assertIn("correct_answer", question)
        self.assertIn("explanation", question)


class TestQuestionEngine(unittest.TestCase):
    """Test the QuestionEngine component"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a mock OpenAIIntegration
        self.mock_openai = MagicMock()
        
        # Mock generate_sat_question method
        self.mock_openai.generate_sat_question.return_value = {
            "id": "test_id",
            "question_type": "Information and Ideas",
            "question": "Test question",
            "passage": "Test passage",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "A",
            "explanation": "Test explanation"
        }
        
        # Create QuestionEngine with mock OpenAIIntegration
        self.question_engine = QuestionEngine(self.mock_openai)
    
    def test_generate_question(self):
        """Test generating questions"""
        question = self.question_engine.generate_question(
            question_type="word_part_identification",
            category="prefixes",
            word_part="un-"
        )
        
        # Check question
        self.assertIn("question", question)
        self.assertIn("options", question)
        self.assertIn("correct_answer", question)
        self.assertIn("explanation", question)
    
    def test_check_answer(self):
        """Test checking answers"""
        # Add a question to history
        self.question_engine.question_history["test_id"] = {
            "question": "Test question",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "A",
            "explanation": "Test explanation"
        }
        
        # Check correct answer
        result = self.question_engine.check_answer("test_id", "A")
        self.assertTrue(result["correct"])
        
        # Check incorrect answer
        result = self.question_engine.check_answer("test_id", "B")
        self.assertFalse(result["correct"])
    
    def test_get_explanation(self):
        """Test getting explanations"""
        # Add a question to history
        self.question_engine.question_history["test_id"] = {
            "question": "Test question",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "A",
            "explanation": "Test explanation"
        }
        
        # Get explanation
        explanation = self.question_engine.get_explanation("test_id")
        self.assertEqual(explanation, "Test explanation")


class TestEnhancedChatbotCore(unittest.TestCase):
    """Test the EnhancedChatbotCore component"""
    
    def setUp(self):
        """Set up test environment"""
        # Create mock components
        self.mock_memory_manager = MagicMock()
        self.mock_openai_integration = MagicMock()
        self.mock_question_engine = MagicMock()
        
        # Mock response generation
        self.mock_openai_integration.generate_response.return_value = {
            "content": "Test response",
            "response_type": "text",
            "raw_response": "Test response",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        
        # Mock question generation
        self.mock_question_engine.generate_question.return_value = {
            "id": "test_id",
            "question_type": "Information and Ideas",
            "question": "Test question",
            "passage": "Test passage",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "A",
            "explanation": "Test explanation",
            "category": "prefixes"
        }
        
        # Create chatbot
        self.chatbot = SATTutorChatbot(user_name="Test User")
        
        # Replace components with mocks
        self.chatbot.memory_manager = self.mock_memory_manager
        self.chatbot.openai_integration = self.mock_openai_integration
        self.chatbot.question_engine = self.mock_question_engine
    
    def test_start_session(self):
        """Test starting a session"""
        # Start session
        result = self.chatbot.start_session()
        
        # Check result
        self.assertIn("greeting", result)
        self.assertIn("days_until_test", result)
        self.assertTrue(self.chatbot.session_state["active"])
    
    def test_process_message_greeting_mode(self):
        """Test processing messages in greeting mode"""
        # Set up session state
        self.chatbot.session_state["active"] = True
        self.chatbot.session_state["current_mode"] = "greeting"
        
        # Process message
        result = self.chatbot.process_message("Hello")
        
        # Check result
        self.assertIn("response", result)
    
    def test_process_message_quiz_mode(self):
        """Test processing messages in quiz mode"""
        # Set up session state
        self.chatbot.session_state["active"] = True
        self.chatbot.session_state["current_mode"] = "quiz"
        self.chatbot.session_state["current_question"] = {
            "id": "test_id",
            "question": "Test question",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "A"
        }
        
        # Mock check_answer
        self.mock_question_engine.check_answer.return_value = {
            "correct": True,
            "correct_answer": "A",
            "explanation": "Test explanation"
        }
        
        # Process answer
        result = self.chatbot.process_message("A")
        
        # Check result
        self.assertIn("response", result)
        self.assertIn("result", result)
        self.assertIn("points", result)
        self.assertIn("streak", result)
    
    def test_end_session(self):
        """Test ending a session"""
        # Set up session state
        self.chatbot.session_state["active"] = True
        self.chatbot.session_state["start_time"] = time.time() - 300  # 5 minutes ago
        self.chatbot.session_state["points"] = 50
        self.chatbot.session_state["streak"] = 3
        self.chatbot.session_state["conversation_history"] = [
            {"role": "assistant", "content": "✅ Correct! Test explanation"},
            {"role": "assistant", "content": "❌ That's not correct. The right answer is A."}
        ]
        
        # End session
        result = self.chatbot.end_session()
        
        # Check result
        self.assertIn("response", result)
        self.assertIn("summary", result)
        self.assertFalse(self.chatbot.session_state["active"])


def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestMemoryManager))
    suite.addTest(unittest.makeSuite(TestOpenAIIntegration))
    suite.addTest(unittest.makeSuite(TestQuestionEngine))
    suite.addTest(unittest.makeSuite(TestEnhancedChatbotCore))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    # Create test directory
    os.makedirs("test_data", exist_ok=True)
    
    # Run tests
    result = run_tests()
    
    # Print summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    
    # Exit with appropriate code
    if result.wasSuccessful():
        print("\nAll tests passed!")
        exit(0)
    else:
        print("\nTests failed!")
        exit(1)
