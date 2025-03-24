# SAT Reading & Writing Chatbot Tutor - Deployment Instructions

This document provides comprehensive instructions for deploying the SAT Reading & Writing Chatbot Tutor using different methods. The application is designed to be easily deployed with minimal dependencies, making it accessible for educational environments.

## Prerequisites

Before deploying the application, ensure you have the following:

- Python 3.7 or higher installed
- pip (Python package installer)
- Internet connection for initial setup
- Basic familiarity with command line operations

## Option 1: Local Deployment

### Step 1: Clone or Download the Project

First, download the project files to your local machine. If you received the files as a ZIP archive, extract them to a folder of your choice.

### Step 2: Set Up a Virtual Environment (Recommended)

It's best practice to create a virtual environment to avoid conflicts with other Python projects:

```bash
# Navigate to the project directory
cd path/to/sat_tutor

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should contain:

```
streamlit>=1.22.0
```

### Step 4: Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application should open automatically in your default web browser. If not, you can access it at `http://localhost:8501`.

## Option 2: Deployment on Replit

[Replit](https://replit.com/) is a browser-based IDE that makes it easy to deploy Python applications without any local setup.

### Step 1: Create a Replit Account

If you don't already have one, sign up for a free account at [replit.com](https://replit.com/).

### Step 2: Create a New Repl

1. Click the "+ Create Repl" button
2. Select "Python" as the language
3. Give your project a name (e.g., "SAT-Tutor")
4. Click "Create Repl"

### Step 3: Upload Project Files

1. In the Replit file explorer, upload all the project files:
   - `app.py`
   - `chatbot_core.py`
   - Any other Python modules or data files

2. Create a new file named `requirements.txt` with the following content:
   ```
   streamlit>=1.22.0
   ```

3. Create a new file named `.replit` with the following content:
   ```
   language = "python3"
   run = "streamlit run app.py"
   ```

### Step 4: Run the Application

Click the "Run" button at the top of the Replit interface. Replit will install the dependencies and start the Streamlit application.

### Step 5: Access the Application

Replit will provide a URL where your application is hosted. You can share this URL with others to let them use the SAT Tutor.

## Option 3: Deployment on Streamlit Cloud

[Streamlit Cloud](https://streamlit.io/cloud) is a platform specifically designed for hosting Streamlit applications.

### Step 1: Create a GitHub Repository

1. Create a new repository on GitHub
2. Upload all project files to the repository:
   - `app.py`
   - `chatbot_core.py`
   - `requirements.txt` (with `streamlit>=1.22.0`)
   - Any other Python modules or data files

### Step 2: Sign Up for Streamlit Cloud

Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.

### Step 3: Deploy Your App

1. Click "New app"
2. Select your GitHub repository, branch, and the main file (`app.py`)
3. Click "Deploy"

Streamlit Cloud will automatically deploy your application and provide a public URL.

## Option 4: Deployment on Flask (Alternative Method)

If you prefer to use Flask instead of Streamlit, you can convert the application to a Flask web application.

### Step 1: Create a Flask Version

Create a new file named `flask_app.py` with the following content:

```python
from flask import Flask, render_template, request, jsonify
from chatbot_core import SATTutorChatbot
import os
import json

app = Flask(__name__)

# Create data directories
os.makedirs("data/sessions", exist_ok=True)
os.makedirs("data/performance", exist_ok=True)
os.makedirs("data/preferences", exist_ok=True)

# Store chatbot instances
chatbots = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_session', methods=['POST'])
def start_session():
    data = request.json
    user_name = data.get('user_name')
    test_date = data.get('test_date')
    
    if not user_name:
        return jsonify({"error": "User name is required"}), 400
    
    # Create or get chatbot instance
    user_id = user_name.lower().replace(" ", "_")
    if user_id not in chatbots:
        chatbots[user_id] = SATTutorChatbot(user_name=user_name, test_date=test_date)
    
    # Start session
    session_info = chatbots[user_id].start_session()
    return jsonify(session_info)

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({"error": "User ID and message are required"}), 400
    
    if user_id not in chatbots:
        return jsonify({"error": "Session not found"}), 404
    
    # Process message
    result = chatbots[user_id].process_message(message)
    return jsonify(result)

@app.route('/api/end_session', methods=['POST'])
def end_session():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    if user_id not in chatbots:
        return jsonify({"error": "Session not found"}), 404
    
    # End session
    result = chatbots[user_id].end_session()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

### Step 2: Create HTML Templates

Create a `templates` folder and add an `index.html` file with your frontend code. You'll need to convert the Streamlit UI to HTML/CSS/JavaScript.

### Step 3: Install Dependencies

```bash
pip install flask
```

### Step 4: Run the Flask Application

```bash
python flask_app.py
```

The application will be available at `http://localhost:5000`.

## Data Storage Considerations

By default, the application stores data in JSON files in the following directories:

- `data/sessions/`: User session data
- `data/performance/`: User performance metrics
- `data/preferences/`: User preferences
- `data/vocabulary/`: Vocabulary database

For a production environment, you might want to consider:

1. **Database Integration**: Replace the file-based storage with a database like SQLite, PostgreSQL, or MongoDB
2. **Cloud Storage**: Store data in cloud storage services if deploying to platforms with ephemeral filesystems
3. **Backup Strategy**: Implement regular backups of user data

## Security Considerations

For educational applications handling student data, consider these security measures:

1. **User Authentication**: Add proper user authentication if deploying beyond personal use
2. **Data Encryption**: Encrypt sensitive user data
3. **HTTPS**: Ensure your deployment uses HTTPS, especially if collecting any personal information
4. **Privacy Policy**: Create a clear privacy policy explaining how user data is used and stored

## Troubleshooting

### Common Issues and Solutions

1. **Streamlit Port Already in Use**
   - Error: `Address already in use`
   - Solution: Kill the process using the port or specify a different port: `streamlit run app.py --server.port 8502`

2. **Missing Dependencies**
   - Error: `ModuleNotFoundError: No module named 'streamlit'`
   - Solution: Ensure you've installed all dependencies: `pip install -r requirements.txt`

3. **File Permission Issues**
   - Error: `Permission denied` when writing to data files
   - Solution: Check folder permissions and ensure the application has write access to the data directory

4. **Browser Compatibility**
   - Issue: UI elements not displaying correctly
   - Solution: Use a modern browser like Chrome, Firefox, or Edge

### Getting Help

If you encounter issues not covered here:

1. Check the Streamlit documentation: [docs.streamlit.io](https://docs.streamlit.io/)
2. Search for similar issues on Stack Overflow
3. Contact the developer for support

## Customization

### Modifying the Vocabulary Database

To customize the vocabulary content:

1. Create a JSON file with your vocabulary data following the structure in `chatbot_core.py`
2. Update the `_load_vocabulary_db` method in `QuestionEngine` to load your custom file

### Changing the UI Theme

To customize the Streamlit theme:

1. Create a file named `.streamlit/config.toml` with the following content:
   ```toml
   [theme]
   primaryColor = "#1E3A8A"
   backgroundColor = "#FFFFFF"
   secondaryBackgroundColor = "#F0F2F6"
   textColor = "#262730"
   font = "sans serif"
   ```

2. Adjust the colors and font to match your preferences

### Adding New Question Types

To add new question types:

1. Update the `QuestionEngine` class in `chatbot_core.py`
2. Add new templates and generation logic for your question type
3. Update the UI in `app.py` to handle the new question type

## Conclusion

The SAT Reading & Writing Chatbot Tutor is designed to be easily deployed in various environments. Choose the deployment method that best suits your needs and technical comfort level.

For personal use or testing, the local deployment or Replit options are recommended. For sharing with a wider audience, consider Streamlit Cloud or a more robust Flask deployment.

Remember to regularly back up user data and consider security implications when deploying to production environments.
