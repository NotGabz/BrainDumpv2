# BrainDump Setup Guide

## Quick Start

### Step 1: Install Python
Make sure you have Python 3.8 or higher installed.

```bash
python --version
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Get Your OpenRouter API Key

1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Navigate to the API Keys section
4. Create a new API key
5. Copy your API key (starts with `sk-or-v1-...`)

### Step 4: Add Your API Key

Open the file `.streamlit/secrets.toml` and replace the placeholder:

```toml
OPENROUTER_API_KEY = "your-actual-api-key-here"
```

### Step 5: Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## What's Next?

1. **Create Your First Note**
   - Click on "Notes" in the sidebar
   - Click "Create New Note"
   - Add a title, subject, and content
   - Save it!

2. **Generate AI Content**
   - Open any note
   - Use the AI tools to:
     - Summarize your notes
     - Generate flashcards
     - Create quizzes
     - Explain concepts
     - Chat about your notes

3. **Start Studying**
   - Go to the "Study" page
   - Select a note
   - Study with flashcards or take a quiz

4. **Track Your Progress**
   - Visit the "Progress" page
   - View your statistics
   - See performance charts
   - Get personalized study suggestions

## Troubleshooting

**Problem: "Module not found" errors**
- Solution: Run `pip install -r requirements.txt`

**Problem: AI features not working**
- Solution: Check that your OpenRouter API key is correctly set in `.streamlit/secrets.toml`

**Problem: "Port 8501 is already in use"**
- Solution: Stop any other Streamlit apps or use a different port:
  ```bash
  streamlit run app.py --server.port 8502
  ```

**Problem: Database errors**
- Solution: Delete `braindump.db` and restart the app. It will be recreated automatically.

## Project Structure

```
braindump/
├── app.py                      # Main dashboard page
├── pages/
│   ├── 1_📝_Notes.py          # Note management
│   ├── 2_🧠_Study.py          # Flashcards & quizzes
│   └── 3_📊_Progress.py       # Statistics & tracking
├── utils/
│   ├── __init__.py
│   ├── database.py             # SQLite database functions
│   ├── ai.py                   # OpenRouter AI functions
│   └── helpers.py              # Utility functions
├── .streamlit/
│   ├── config.toml             # Theme settings
│   └── secrets.toml            # API keys (gitignored)
├── requirements.txt
├── README.md
└── SETUP.md                    # This file
```

## Features Overview

### Notes Page
- Create, edit, and delete notes
- Organize by subject
- Search functionality
- AI-powered summaries
- Generate flashcards from notes
- Generate quizzes from notes
- Get explanations of concepts
- Chat with AI about your notes

### Study Page
- **Flashcards Mode**
  - Study one card at a time
  - Reveal answers
  - Track correct/incorrect responses
  - Review missed cards

- **Quiz Mode**
  - Multiple choice questions
  - Instant feedback
  - Explanations for correct answers
  - Score tracking

### Progress Page
- Overall statistics dashboard
- Quiz scores over time (line chart)
- Performance by subject (bar chart)
- Recent quiz history
- Personalized study suggestions

## Tips for Success

1. **Write Detailed Notes**: The more detailed your notes, the better the AI-generated content will be.

2. **Study Regularly**: Use flashcards and quizzes frequently to reinforce learning.

3. **Review Progress**: Check the Progress page weekly to identify areas needing improvement.

4. **Use All AI Features**:
   - Summaries help you review quickly
   - Flashcards improve memorization
   - Quizzes test your understanding
   - Chat helps clarify confusion

5. **Organize by Subject**: Keep your notes organized by subject for better tracking.

## Need Help?

- Check the README.md for more detailed information
- Report issues on GitHub
- Review the code comments for technical details

Happy studying! 🧠
