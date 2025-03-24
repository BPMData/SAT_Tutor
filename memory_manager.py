"""
Memory Manager for SAT Reading & Writing Chatbot Tutor

This module implements the hybrid memory system for the SAT tutor, combining
short-term memory for immediate context and a vector database for long-term
storage and retrieval of relevant conversation history.
"""

import os
import json
import time
import sqlite3
import datetime
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import tiktoken
import streamlit as st

class TokenCounter:
    """
    Utility class for counting tokens in text and messages using tiktoken.
    """
    
    def __init__(self, model_name: str = "gpt-4o"):
        """
        Initialize the token counter with the specified model.
        
        Args:
            model_name: The name of the OpenAI model to use for token counting
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base encoding if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The number of tokens in the text
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count the number of tokens in a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            The total number of tokens in all messages
        """
        if not messages:
            return 0
        
        # OpenAI's token counting approach for chat messages
        # See: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        
        # Base tokens for message formatting
        tokens_per_message = 3
        tokens_per_name = 1
        
        # Count tokens
        total_tokens = 0
        for message in messages:
            total_tokens += tokens_per_message
            for key, value in message.items():
                if key == "timestamp":
                    continue  # Skip timestamp for token counting
                total_tokens += self.count_tokens(str(value))
                if key == "role":
                    total_tokens += tokens_per_name
        
        # Every reply is primed with <|start|>assistant<|message|>
        total_tokens += 3
        
        return total_tokens


class VectorDatabase:
    """
    SQLite-based vector database for storing and retrieving text chunks and their embeddings.
    """
    
    def __init__(self, db_path: str = "data/memory.db", embedding_dimension: int = 1536):
        """
        Initialize the vector database.
        
        Args:
            db_path: Path to the SQLite database file
            embedding_dimension: Dimension of the embedding vectors
        """
        self.db_path = db_path
        self.embedding_dimension = embedding_dimension
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.initialize_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the SQLite database.
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_db(self) -> None:
        """
        Initialize the database schema if it doesn't exist.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create chunks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create index on timestamp
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_chunks_timestamp ON chunks(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_chunk(self, text: str, embedding: List[float]) -> int:
        """
        Insert a text chunk and its embedding into the database.
        
        Args:
            text: The text chunk to store
            embedding: The embedding vector for the text
            
        Returns:
            The ID of the inserted chunk
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert embedding to binary blob
        embedding_blob = self._embedding_to_blob(embedding)
        
        # Insert chunk
        cursor.execute(
            "INSERT INTO chunks (text, embedding, timestamp) VALUES (?, ?, ?)",
            (text, embedding_blob, datetime.datetime.now())
        )
        
        # Get the ID of the inserted chunk
        chunk_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return chunk_id
    
    def search_similar(self, embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for chunks with embeddings similar to the given embedding.
        
        Args:
            embedding: The query embedding vector
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing chunk_id, text, similarity, and timestamp
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all chunks
        cursor.execute("SELECT chunk_id, text, embedding, timestamp FROM chunks")
        chunks = cursor.fetchall()
        
        # Calculate similarity for each chunk
        results = []
        for chunk in chunks:
            chunk_embedding = self._blob_to_embedding(chunk["embedding"])
            similarity = self.calculate_similarity(embedding, chunk_embedding)
            
            results.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "similarity": similarity,
                "timestamp": chunk["timestamp"]
            })
        
        # Sort by similarity (descending) and limit results
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:limit]
        
        conn.close()
        
        return results
    
    def delete_chunk(self, chunk_id: int) -> bool:
        """
        Delete a chunk from the database.
        
        Args:
            chunk_id: The ID of the chunk to delete
            
        Returns:
            True if the chunk was deleted, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chunks WHERE chunk_id = ?", (chunk_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def calculate_similarity(self, v1: List[float], v2: List[float]) -> float:
        """
        Calculate the cosine similarity between two vectors.
        
        Args:
            v1: First vector
            v2: Second vector
            
        Returns:
            Cosine similarity (between -1 and 1, higher is more similar)
        """
        # Convert to numpy arrays
        v1_array = np.array(v1)
        v2_array = np.array(v2)
        
        # Normalize vectors
        v1_norm = v1_array / np.linalg.norm(v1_array)
        v2_norm = v2_array / np.linalg.norm(v2_array)
        
        # Calculate cosine similarity
        return np.dot(v1_norm, v2_norm)
    
    def _embedding_to_blob(self, embedding: List[float]) -> bytes:
        """
        Convert an embedding vector to a binary blob for storage.
        
        Args:
            embedding: The embedding vector
            
        Returns:
            Binary blob representation of the embedding
        """
        return np.array(embedding, dtype=np.float32).tobytes()
    
    def _blob_to_embedding(self, blob: bytes) -> List[float]:
        """
        Convert a binary blob back to an embedding vector.
        
        Args:
            blob: Binary blob from the database
            
        Returns:
            The embedding vector as a list of floats
        """
        array = np.frombuffer(blob, dtype=np.float32)
        return array.tolist()


class MemoryManager:
    """
    Manages the hybrid memory system for the SAT tutor, combining short-term
    memory and a vector database for long-term storage and retrieval.
    """
    
    def __init__(
        self,
        max_tokens: int = 40000,
        model_name: str = "gpt-4o",
        db_path: str = "data/memory.db",
        embedding_dimension: int = 1536
    ):
        """
        Initialize the memory manager.
        
        Args:
            max_tokens: Maximum number of tokens in short-term memory
            model_name: The name of the OpenAI model to use
            db_path: Path to the SQLite database file
            embedding_dimension: Dimension of the embedding vectors
        """
        self.short_term_memory = []
        self.max_tokens = max_tokens
        self.model_name = model_name
        
        # Initialize token counter
        self.token_counter = TokenCounter(model_name)
        
        # Initialize vector database
        self.vector_db = self._get_or_create_vector_db(db_path, embedding_dimension)
    
    def _get_or_create_vector_db(self, db_path: str, embedding_dimension: int) -> VectorDatabase:
        """
        Get or create a vector database instance using Streamlit's caching.
        
        Args:
            db_path: Path to the SQLite database file
            embedding_dimension: Dimension of the embedding vectors
            
        Returns:
            VectorDatabase instance
        """
        # Use Streamlit's cache_resource if available
        if 'st' in globals():
            @st.cache_resource
            def get_vector_db(path, dim):
                return VectorDatabase(path, dim)
            
            return get_vector_db(db_path, embedding_dimension)
        else:
            # Fallback for non-Streamlit environments
            return VectorDatabase(db_path, embedding_dimension)
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to short-term memory.
        
        Args:
            role: The role of the message sender ("user", "assistant", or "system")
            content: The content of the message
        """
        # Create message object
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add to short-term memory
        self.short_term_memory.append(message)
        
        # Check if we need to prune
        self.prune_short_term_memory()
        
        # Store in long-term memory if it's a user or assistant message
        if role in ["user", "assistant"]:
            self.store_in_long_term(message)
    
    def get_context_for_prompt(self, query: str = None, max_relevant_chunks: int = 3) -> Dict[str, Any]:
        """
        Get the context to be used in the LLM prompt.
        
        Args:
            query: The query to use for retrieving relevant chunks (defaults to last user message)
            max_relevant_chunks: Maximum number of relevant chunks to include
            
        Returns:
            Dictionary with system_instructions, short_term_memory, relevant_chunks, and user_query
        """
        # If no query is provided, use the last user message
        if query is None and self.short_term_memory:
            for message in reversed(self.short_term_memory):
                if message["role"] == "user":
                    query = message["content"]
                    break
        
        # If still no query, use an empty string
        if query is None:
            query = ""
        
        # Get relevant chunks from long-term memory
        relevant_chunks = []
        if query:
            # Get embedding for query
            query_embedding = self.create_embedding(query)
            if query_embedding:
                # Search for similar chunks
                results = self.vector_db.search_similar(query_embedding, limit=max_relevant_chunks)
                relevant_chunks = [result["text"] for result in results]
        
        # Create context dictionary
        context = {
            "system_instructions": self._get_system_instructions(),
            "short_term_memory": self.short_term_memory,
            "relevant_chunks": relevant_chunks,
            "user_query": query
        }
        
        return context
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for the given text using OpenAI's API.
        
        Args:
            text: The text to create an embedding for
            
        Returns:
            The embedding vector or None if there was an error
        """
        # This is a placeholder - in the actual implementation, this would call the OpenAI API
        # For now, we'll return a random embedding for testing purposes
        # This will be replaced when we integrate the OpenAI API
        
        # Placeholder: Return random embedding of the correct dimension
        import random
        return [random.uniform(-1, 1) for _ in range(1536)]
    
    def store_in_long_term(self, message: Dict[str, str]) -> None:
        """
        Store a message in long-term memory.
        
        Args:
            message: The message to store
        """
        # Create text representation of the message
        text = f"{message['role'].upper()}: {message['content']}"
        
        # Create embedding
        embedding = self.create_embedding(text)
        
        # Store in vector database if embedding was created successfully
        if embedding:
            self.vector_db.insert_chunk(text, embedding)
    
    def retrieve_relevant(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from long-term memory.
        
        Args:
            query: The query to use for retrieval
            limit: Maximum number of chunks to retrieve
            
        Returns:
            List of relevant chunks with their similarity scores
        """
        # Create embedding for query
        query_embedding = self.create_embedding(query)
        
        # Return empty list if embedding creation failed
        if not query_embedding:
            return []
        
        # Search for similar chunks
        return self.vector_db.search_similar(query_embedding, limit=limit)
    
    def create_summary(self, messages: List[Dict[str, str]] = None) -> str:
        """
        Create a summary of the given messages or the current short-term memory.
        
        Args:
            messages: The messages to summarize (defaults to short-term memory)
            
        Returns:
            A summary of the messages
        """
        # Use short-term memory if no messages are provided
        if messages is None:
            messages = self.short_term_memory
        
        # If there are no messages, return empty string
        if not messages:
            return ""
        
        # This is a placeholder - in the actual implementation, this would call the OpenAI API
        # For now, we'll return a simple concatenation of the messages
        # This will be replaced when we integrate the OpenAI API
        
        summary_parts = []
        for message in messages:
            summary_parts.append(f"{message['role'].upper()}: {message['content'][:50]}...")
        
        return "SUMMARY: " + " ".join(summary_parts)
    
    def prune_short_term_memory(self) -> None:
        """
        Prune short-term memory if it exceeds the token limit.
        """
        # Count tokens in short-term memory
        total_tokens = self.token_counter.count_message_tokens(self.short_term_memory)
        
        # If we're under the limit, no need to prune
        if total_tokens <= self.max_tokens:
            return
        
        # Strategy 1: Remove oldest messages first
        while (
            self.short_term_memory and 
            self.token_counter.count_message_tokens(self.short_term_memory) > self.max_tokens
        ):
            # Keep system messages if possible
            if len(self.short_term_memory) > 1 and self.short_term_memory[0]["role"] == "system":
                # Remove the second oldest message
                self.short_term_memory.pop(1)
            else:
                # Remove the oldest message
                self.short_term_memory.pop(0)
        
        # Alternative Strategy 2 (commented out): Summarize older messages
        # This would be implemented when we integrate the OpenAI API
        """
        # Find a cutoff point where we can summarize older messages
        cutoff = len(self.short_term_memory) // 2
        
        # Summarize the older half of messages
        older_messages = self.short_term_memory[:cutoff]
        summary = self.create_summary(older_messages)
        
        # Replace older messages with summary
        summary_message = {
            "role": "system",
            "content": summary,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.short_term_memory = [summary_message] + self.short_term_memory[cutoff:]
        """
    
    def get_token_count(self, text: str) -> int:
        """
        Get the token count for a text string.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The number of tokens in the text
        """
        return self.token_counter.count_tokens(text)
    
    def _get_system_instructions(self) -> str:
        """
        Get the system instructions for the SAT tutor.
        
        Returns:
            The system instructions as a string
        """
        return """
        You are an expert SAT Reading & Writing tutor designed to help high school students prepare for the test.
        Your goal is to provide personalized assistance, focusing on prefixes, roots, and suffixes.
        
        You should:
        1. Respond in a friendly, motivating, non-condescending tone
        2. Provide explanations at the appropriate reading level for the student
        3. Track the student's progress and focus on areas that need improvement
        4. Generate SAT-style questions that test the student's knowledge
        5. Provide detailed explanations for answers
        
        Remember to maintain context from previous interactions and adapt to the student's needs.
        """


# Example usage
if __name__ == "__main__":
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Add some messages
    memory_manager.add_message("system", "You are an SAT tutor.")
    memory_manager.add_message("user", "Can you help me understand prefixes?")
    memory_manager.add_message("assistant", "Of course! Prefixes are word parts added to the beginning of a word to change its meaning.")
    
    # Get context for prompt
    context = memory_manager.get_context_for_prompt()
    
    # Print context
    print("Context for prompt:")
    print(f"System instructions: {context['system_instructions']}")
    print(f"Short-term memory: {len(context['short_term_memory'])} messages")
    print(f"Relevant chunks: {context['relevant_chunks']}")
    print(f"User query: {context['user_query']}")
