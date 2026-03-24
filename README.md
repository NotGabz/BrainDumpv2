# 🧠 BrainDump - AI-Powered Study Helper

BrainDump is a complete study companion that helps you take notes, create flashcards, generate quizzes, and track your learning progress using AI.

## Features

- **📝 Smart Note Taking**: Create and organize notes by subject
- **🧠 AI-Generated Flashcards**: Automatically create flashcards from your notes
- **📊 AI-Generated Quizzes**: Test your knowledge with custom quizzes
- **💡 Concept Explanations**: Get simple explanations of confusing concepts
- **💬 Chat with Your Notes**: Ask questions about your notes and get AI-powered answers
- **📈 Progress Tracking**: View statistics and identify areas for improvement
- **✨ Beautiful UI**: Clean, modern interface with dark theme

## Installation

### 1. Clone or Download the Project

```bash
git clone <your-repo-url>
cd braindump
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Your OpenRouter API Key

1. Get a free API key from [OpenRouter.ai](https://openrouter.ai/)
2. Open `.streamlit/secrets.toml`
3. Replace `your-api-key-here` with your actual API key:

```toml
OPENROUTER_API_KEY = "sk-or-v1-xxxxxxxxxxxxx"
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage Guide

### Creating Notes

1. Navigate to the **Notes** page
2. Click **Create New Note**
3. Enter a title, subject, and your note content
4. Click **Save**

### Studying with Flashcards

1. Go to the **Study** page
2. Select a note from the dropdown
3. Click **Flashcards** tab
4. Generate flashcards (if not already created)
5. Study by revealing answers and marking them as correct/incorrect

### Taking Quizzes

1. Go to the **Study** page
2. Select a note from the dropdown
3. Click **Quiz** tab
4. Generate a quiz (if not already created)
5. Answer the multiple-choice questions
6. Review your results and explanations

### AI Features

From any note, you can:

- **Summarize**: Get a concise bullet-point summary
- **Generate Flashcards**: Create 5-20 flashcards automatically
- **Generate Quiz**: Create 3-10 quiz questions
- **Explain Concepts**: Paste confusing text for a simple explanation
- **Chat**: Ask questions about your notes

### Tracking Progress

Visit the **Progress** page to see:

- Overall statistics (notes, flashcards, quizzes, average score)
- Quiz scores over time (line chart)
- Performance by subject (bar chart)
- Recent quiz history
- Personalized study suggestions

## Project Structure

```
braindump/
├── app.py                    # Home dashboard
├── pages/
│   ├── 1_📝_Notes.py        # Note taking and AI features
│   ├── 2_🧠_Study.py        # Flashcards and quizzes
│   └── 3_📊_Progress.py     # Statistics and tracking
├── utils/
│   ├── database.py           # Database functions (SQLite)
│   ├── ai.py                 # AI functions (OpenRouter)
│   └── helpers.py            # Helper utilities
├── .streamlit/
│   ├── config.toml           # Theme configuration
│   └── secrets.toml          # API keys (DO NOT COMMIT)
├── requirements.txt
└── README.md
```

## Deploying to Streamlit Cloud

1. Push your code to GitHub (make sure `.streamlit/secrets.toml` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. In the deployment settings, add your secrets:
   - Key: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key
5. Deploy!

## Tips for Best Results

- Write detailed notes for better AI-generated content
- Review flashcards regularly for better retention
- Take quizzes multiple times to reinforce learning
- Use the chat feature to clarify confusing concepts
- Check the Progress page to identify weak subjects

## Technologies Used

- **Streamlit**: Web framework
- **SQLite**: Database
- **OpenRouter**: AI API (using Qwen Coder model)
- **OpenAI Python Client**: API client library
- **Pandas**: Data analysis for progress tracking

## Troubleshooting

**AI features not working?**
- Make sure your OpenRouter API key is correctly set in `.streamlit/secrets.toml`
- Check that you have an active internet connection

**Database issues?**
- The SQLite database (`braindump.db`) is created automatically
- If you encounter issues, delete `braindump.db` and restart the app

**Import errors?**
- Make sure all dependencies are installed: `pip install -r requirements.txt`

## License

This project is open source and available for educational purposes.

## Credits

Built with ❤️ for learners everywhere.

Powered by:
- Streamlit
- OpenRouter AI
- Qwen Coder AI Model
