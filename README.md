# README: Enhanced SAT Reading & Writing Chatbot Tutor

## Introduction

Welcome to the Enhanced SAT Reading & Writing Chatbot Tutor! This intelligent tutoring system is designed to help high school students prepare for the SAT Reading & Writing section, with a special focus on prefixes, roots, and suffixes. The enhanced version includes a robust memory system, OpenAI GPT-4o integration, and improved SAT-style question generation capabilities.

## Key Features

- **Conversational Interface**: Friendly, motivating tone with ability to explain concepts at different reading levels (grades 8-12)
- **Hybrid Memory System**: Combines short-term memory and vector database for contextual conversations
- **Gamified Learning**: Points, streaks, and achievements to keep students motivated
- **Smart Adaptation**: Adjusts to student performance and focuses on areas needing improvement
- **SAT-Style Questions**: Generates authentic questions following official SAT guidelines
- **Test Countdown**: Shows days remaining until the test to create urgency
- **Personalization**: Remembers student name and preferences

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- OpenAI API key

### Installation

1. Clone the repository or extract the provided zip file:
   ```
   mkdir sat_tutor
   cd sat_tutor
   # Extract files here
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Create a `.streamlit/secrets.toml` file with the following content:
     ```
     OPENAI_API_KEY = "your-api-key-here"
     ```
   - Alternatively, set the `OPENAI_API_KEY` environment variable

4. Run the setup script to initialize the necessary directories and files:
   ```
   ./setup.sh
   ```

5. Start the application:
   ```
   streamlit run app_enhanced.py
   ```

## Project Structure

```
sat_tutor/
├── app_enhanced.py           # Streamlit application
├── config.py                 # Configuration settings
├── documentation.md          # Comprehensive documentation
├── enhanced_chatbot_core.py  # Main chatbot implementation
├── integration_test.py       # Integration tests
├── memory_manager.py         # Hybrid memory system
├── openai_integration.py     # OpenAI API integration
├── question_engine.py        # SAT question generation
├── requirements.txt          # Dependencies
├── setup.sh                  # Setup script
└── test_integration.py       # Unit tests
```

## Usage

1. Enter your name and test date in the sidebar
2. Start a conversation with the chatbot
3. Ask for help with prefixes, roots, or suffixes
4. Request quizzes on specific word parts
5. Answer questions and receive immediate feedback
6. Ask "Why?" to get detailed explanations
7. Track your progress with points and achievements

## Deployment Options

### Local Deployment

Run locally with:
```
streamlit run app_enhanced.py
```

### Streamlit Cloud

1. Push to GitHub
2. Deploy on Streamlit Cloud
3. Add your OpenAI API key to secrets

### Replit

1. Create a new Replit project
2. Upload the project files
3. Set run command to `streamlit run app_enhanced.py`
4. Add your OpenAI API key to secrets

## Documentation

For detailed documentation, please see [documentation.md](documentation.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the GPT-4o model
- Streamlit for the web application framework
- The SAT College Board for educational guidelines
