"""
OpenAI API Integration for SAT Reading & Writing Chatbot Tutor

This module implements the integration with OpenAI's GPT-4o API for the SAT tutor,
providing functions for generating embeddings, creating responses, and generating
SAT-style questions.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Union
import streamlit as st
from openai import OpenAI

class OpenAIIntegration:
    """
    Handles integration with OpenAI's API for the SAT tutor.
    """
    
    def __init__(self, model_name: str = "gpt-4o"):
        """
        Initialize the OpenAI integration.
        
        Args:
            model_name: The name of the OpenAI model to use
        """
        self.model_name = model_name
        self.client = self._get_openai_client()
    
    def _get_openai_client(self) -> OpenAI:
        """
        Get an OpenAI client instance using the API key from Streamlit secrets.
        
        Returns:
            OpenAI client instance
        """
        # Get API key from Streamlit secrets if available
        api_key = None
        if 'st' in globals():
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
            except Exception as e:
                st.error(f"Error accessing OpenAI API key from Streamlit secrets: {e}")
                st.error("Please set the OPENAI_API_KEY in your Streamlit secrets.")
        
        # Fallback to environment variable if not in Streamlit
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                    "or add it to your Streamlit secrets."
                )
        
        # Create and return client
        return OpenAI(api_key=api_key)
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for the given text using OpenAI's API.
        
        Args:
            text: The text to create an embedding for
            
        Returns:
            The embedding vector or None if there was an error
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # Using the appropriate embedding model
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None
    
    def generate_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response using the OpenAI API based on the provided context.
        
        Args:
            context: Dictionary containing system_instructions, short_term_memory,
                    relevant_chunks, and user_query
            
        Returns:
            Dictionary with the generated response and metadata
        """
        try:
            # Prepare messages for the API
            messages = []
            
            # Add system message with instructions
            system_content = context["system_instructions"].strip()
            if context["relevant_chunks"]:
                system_content += "\n\nRelevant context from previous conversations:\n"
                for i, chunk in enumerate(context["relevant_chunks"]):
                    system_content += f"\n{i+1}. {chunk}\n"
            
            messages.append({"role": "system", "content": system_content})
            
            # Add short-term memory messages
            for message in context["short_term_memory"]:
                # Skip system messages as they're included in the system content
                if message["role"] == "system":
                    continue
                
                # Add user and assistant messages
                messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract and return the response
            content = response.choices[0].message.content
            
            # Try to parse as JSON if it looks like JSON
            try:
                if content.strip().startswith("{") and content.strip().endswith("}"):
                    parsed_content = json.loads(content)
                    return {
                        "content": parsed_content.get("content", content),
                        "response_type": parsed_content.get("response_type", "text"),
                        "raw_response": content,
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        }
                    }
            except json.JSONDecodeError:
                pass
            
            # Return as plain text if not JSON
            return {
                "content": content,
                "response_type": "text",
                "raw_response": content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "content": f"I'm sorry, I encountered an error: {str(e)}",
                "response_type": "error",
                "error": str(e)
            }
    
    def create_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Create a summary of the given messages using the OpenAI API.
        
        Args:
            messages: The messages to summarize
            
        Returns:
            A summary of the messages
        """
        try:
            # Prepare the prompt
            prompt = "Please summarize the following conversation concisely while preserving key information:\n\n"
            
            for message in messages:
                role = message["role"].upper()
                content = message["content"]
                prompt += f"{role}: {content}\n\n"
            
            # Generate summary
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract and return the summary
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error creating summary: {e}")
            return f"Error creating summary: {str(e)}"
    
    def generate_sat_question(self, text_segment: str, question_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an SAT-style question based on the provided text segment.
        
        Args:
            text_segment: The text segment to generate a question for
            question_type: Optional specific question type to generate
                          (Information and Ideas, Craft and Structure, 
                           Expression of Ideas, Standard English Conventions)
            
        Returns:
            Dictionary containing the generated question data
        """
        try:
            # Prepare system instructions
            system_instructions = """
# System Instructions for SAT-Style Question Generator for Longer Articles

## Core Purpose

Generate SAT-style Reading and Writing questions that test specific sections (1-3 paragraphs) within longer articles. These questions should mirror the cognitive demands and format of the digital SAT while being interspersed throughout a lengthier text.

## Question Generation Approach

*   **Segment Analysis:** When provided with a longer article, identify coherent segments (1-3 paragraphs) that can stand as self-contained mini-passages for question development. *Look for segments that present a complete idea, argument, or piece of evidence.*
*   **Question Placement:** Create questions that could logically appear *after* specific paragraphs, testing comprehension and analysis of *just that section*, not the entire article.
*   **Self-Contained Questions:** Ensure each question can be answered *completely* using only the immediate context (the preceding 1-3 paragraphs), without requiring information from elsewhere in the article.
*   **Domain Distribution:** Generate questions across all four SAT content domains, appropriately matched to the content of each selected segment:
    *   Information and Ideas (≈26%)
    *   Craft and Structure (≈28%)
    *   Expression of Ideas (≈20%)
    *   Standard English Conventions (≈26%)

## Domain-Specific Question Design Guidelines

### Information and Ideas

*   **For Informational Segments:** Questions about main ideas, supporting details, inferences, or logical conclusions.
*   **For Argumentative Segments:** Questions about claims, evidence, logical reasoning, or conclusions.
*   **Question Stems:**
    *   "Based on the preceding paragraphs, which statement best captures the main idea?"
    *   "Which finding would most directly support the author's claim in paragraph X?"
    *   "What can reasonably be inferred from the author's description of..."

### Craft and Structure

*   **For Segments with Notable Language:** Questions about word meaning in context.
*   **For Segments with Distinct Structure:** Questions about function of sentences, paragraphs, or rhetorical elements.
*   **Question Stems:**
    *   "As used in paragraph X, the word '___' most nearly means..."
    *   "The primary function of the [third] paragraph is to..."
    *   "The author includes the example of [X] primarily to..."

### Expression of Ideas

*   **For Segments with Complex Organization:** Questions about sentence placement, transitions, or combinations.
*   **For Segments with Supporting Information:** Questions about effective use of information. *In rare cases, you may be provided with supplementary notes to be used in the question.*
*   **Question Stems:**
    *   "Which transition would most effectively connect paragraphs X and Y?"
    *   "Where would the following sentence best be placed in paragraph X?"
    *   "Which revision most improves the clarity of the author's point in paragraph X?"

### Standard English Conventions

*   **For Any Segment:** Identify a location where a grammatical question could be asked.
*   **Process:** Create a version that tests *one* specific grammatical convention *without* modifying the original text.
*   **Question Stem:** "Which choice best conforms to Standard English conventions?"

## Answer Choice Construction

*   **Structure:** Four options (A-D) with one unambiguously correct answer.
*   **Domain-Specific Distractor Design:** Create plausible but incorrect options based on common student errors.
*   **Quality Requirements:**
    *   Similar length and complexity across options.
    *   Parallel grammatical structure (unless testing grammar).
    *   All distractors must be definitively incorrect, but plausible enough to require careful reading.
    *   Ensure all options directly relate to the selected segment (1-3 paragraphs).

## Required format

Return a JSON object with the following format:
```json
{
"question_type": "<One of: Information and Ideas, Craft and Structure, Expression of Ideas, Standard English Conventions>",
"question": "<The question stem>",
"passage": "<The 1-3 paragraph segment the question is based on>",
"options": {
    "A": "<Option A>",
    "B": "<Option B>",
    "C": "<Option C>",
    "D": "<Option D>"
},
"correct_answer": "<A, B, C, or D>",
"explanation": "<A detailed explanation of why the correct answer is correct, and why the other options are incorrect.>"
}
```
            """
            
            # Prepare user prompt
            user_prompt = f"Generate an SAT-style question based on the following text segment:\n\n{text_segment}"
            
            # Add specific question type if provided
            if question_type:
                user_prompt += f"\n\nPlease generate a question of type: {question_type}"
            
            # Generate question
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                response_format={"type": "json_object"}
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content
            
            try:
                question_data = json.loads(content)
                
                # Validate required fields
                required_fields = ["question_type", "question", "passage", "options", "correct_answer", "explanation"]
                for field in required_fields:
                    if field not in question_data:
                        raise ValueError(f"Missing required field: {field}")
                
                # Add metadata
                question_data["generated_at"] = time.time()
                question_data["model"] = self.model_name
                
                return question_data
                
            except json.JSONDecodeError as e:
                print(f"Error parsing question JSON: {e}")
                print(f"Raw content: {content}")
                return {
                    "error": "Failed to parse question data",
                    "raw_content": content
                }
            
        except Exception as e:
            print(f"Error generating SAT question: {e}")
            return {
                "error": f"Error generating SAT question: {str(e)}"
            }


# Example usage
if __name__ == "__main__":
    # This will only work if you have set the OPENAI_API_KEY environment variable
    try:
        # Initialize OpenAI integration
        openai_integration = OpenAIIntegration()
        
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
        
        # Generate an SAT question
        question = openai_integration.generate_sat_question(text_segment)
        
        # Print the generated question
        print("Generated SAT Question:")
        print(json.dumps(question, indent=2))
        
    except Exception as e:
        print(f"Error in example: {e}")
