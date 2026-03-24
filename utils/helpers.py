from datetime import datetime
import streamlit as st


def format_date(timestamp):
    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp)
        except Exception:
            return timestamp
    else:
        dt = timestamp
    return dt.strftime("%b %d, %Y at %I:%M %p")


def truncate_text(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length].strip() + "..."


def validate_note_input(title, subject, content):
    errors = []
    if not title or title.strip() == "":
        errors.append("Title is required")
    if not subject or subject.strip() == "":
        errors.append("Subject is required")
    if not content or content.strip() == "":
        errors.append("Content is required")
    return errors


def calculate_percentage(score, total):
    if total == 0:
        return 0
    return round((score / total) * 100, 1)


def get_performance_emoji(percentage):
    if percentage >= 90:
        return "🏆"
    elif percentage >= 80:
        return "🌟"
    elif percentage >= 70:
        return "✅"
    elif percentage >= 60:
        return "👍"
    else:
        return "📚"


def get_grade(percentage):
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"


def get_subject_color(index):
    colors = ["#415A77", "#778DA9", "#5A7D8C", "#6B8E99", "#4A6F82"]
    return colors[index % len(colors)]


# ────────────────────────────────────────────────────────────
# Login guard — call at top of every page
# ────────────────────────────────────────────────────────────

def require_login():
    """Redirect to app.py if not logged in. Call at top of every page."""
    if not st.session_state.get("logged_in"):
        st.switch_page("app.py")


# ────────────────────────────────────────────────────────────
# Sound effects
# ────────────────────────────────────────────────────────────

# Short beep sounds encoded as base64 WAV files
# "Ding" — 880Hz sine wave, 0.15s
_DING_B64 = (
    "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="
)

# "Buzz" — 220Hz square-ish wave, 0.15s
_BUZZ_B64 = (
    "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="
)


def play_correct_sound():
    """Play a short 'ding' sound if sound effects are enabled."""
    try:
        from utils.database import get_setting
        if get_setting("sound_effects"):
            st.markdown(
                f'<audio autoplay><source src="data:audio/wav;base64,{_DING_B64}"></audio>',
                unsafe_allow_html=True,
            )
    except Exception:
        pass


def play_wrong_sound():
    """Play a short 'buzz' sound if sound effects are enabled."""
    try:
        from utils.database import get_setting
        if get_setting("sound_effects"):
            st.markdown(
                f'<audio autoplay><source src="data:audio/wav;base64,{_BUZZ_B64}"></audio>',
                unsafe_allow_html=True,
            )
    except Exception:
        pass


# ────────────────────────────────────────────────────────────
# CSS injection
# ────────────────────────────────────────────────────────────

def inject_custom_css():
    from utils.database import get_setting, THEMES, FONTS

    theme_name = get_setting("theme") or "Midnight"
    c = THEMES.get(theme_name, THEMES["Midnight"])
    font_name = get_setting("font") or "Inter"
    font_family = FONTS.get(font_name, "Inter, sans-serif")

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Merriweather:wght@400;700&display=swap');

    .stApp, .stApp * {{ font-family: {font_family} !important; }}
    .stApp code, .stApp pre {{ font-family: 'JetBrains Mono', monospace !important; }}
    .stApp {{ background-color: {c['background']}; }}
    section[data-testid="stSidebar"] {{ background-color: {c['cards']}; }}

    [data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavLink"], ul[data-testid="stSidebarNavItems"] {{
        display: none !important;
    }}

    .stApp h1 {{ font-size: 32px !important; font-weight: 700 !important; color: {c['primary_text']} !important; }}
    .stApp h2 {{ font-size: 24px !important; font-weight: 600 !important; color: {c['primary_text']} !important; }}
    .stApp h3 {{ font-size: 20px !important; font-weight: 500 !important; color: {c['secondary_text']} !important; }}
    .stApp .stMarkdown p {{ color: {c['primary_text']} !important; line-height: 1.6 !important; }}

    .note-card, .flashcard, .score-card, .quiz-question, .suggestion-card,
    .stat-card, .credit-card, .quiz-card, .about-box, .quote-card, .streak-card {{
        background-color: {c['cards']} !important;
        border: 1px solid {c['accent']}4D !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        transition: all 0.2s ease !important;
    }}
    .note-card:hover, .stat-card:hover, .credit-card:hover, .suggestion-card:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }}

    .stButton > button {{
        background-color: {c['accent']} !important;
        color: {c['primary_text']} !important;
        border: 1px solid {c['accent']} !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{ filter: brightness(0.85) !important; }}

    .subject-tag {{ background-color: {c['accent']} !important; color: {c['primary_text']} !important; }}
    .note-title, .stat-number, .grade-big {{ color: {c['primary_text']} !important; }}
    .note-content, .note-date, .stat-label {{ color: {c['secondary_text']} !important; }}
    .progress-bar {{ background-color: {c['cards']} !important; }}
    .progress-fill {{ background-color: {c['accent']} !important; }}
    .stAlert {{ border-radius: 8px !important; }}

    section[data-testid="stSidebar"] .stPageLink {{ border-radius: 8px !important; }}
    section[data-testid="stSidebar"] .stPageLink[data-is-current="true"] a {{
        background-color: {c['accent']} !important; color: {c['primary_text']} !important; font-weight: 600 !important;
    }}

    .empty-state {{ text-align: center; padding: 3rem; color: {c['secondary_text']}; font-size: 1.2rem; }}
    .save-status {{ font-size: 0.8rem; color: {c['secondary_text']}; margin-top: 0.25rem; }}
    .toolbar-hint {{ font-size: 0.75rem; color: {c['secondary_text']}; margin-bottom: 0.25rem; }}
    .diff-bar {{ height: 28px; border-radius: 6px; display: flex; align-items: center; padding: 0 12px; color: #fff; font-size: 0.85rem; font-weight: 600; margin: 4px 0; }}
    .tech-bar {{ height: 36px; border-radius: 8px; display: flex; align-items: center; padding: 0 14px; background-color: {c['accent']}; color: #fff; font-weight: 600; font-size: 0.9rem; margin-bottom: 8px; }}
    .avatar {{ font-size: 4rem; margin-bottom: 0.5rem; }}
    .tech-table {{ width: 100%; border-collapse: collapse; }}
    .tech-table td {{ padding: 0.75rem 1rem; border-bottom: 1px solid {c['accent']}33; color: {c['primary_text']}; }}
    .tech-table td:first-child {{ font-weight: 600; width: 35%; }}
    .version-text {{ color: {c['secondary_text']}; font-size: 0.9rem; }}
    </style>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────

def render_sidebar():
    from utils.database import get_stats, get_setting

    if not st.session_state.get("logged_in"):
        return

    username = st.session_state.get("username", "")
    display_name = st.session_state.get("display_name", "")
    avatar = get_setting(f"avatar_{username}") or "🧑‍🎓"
    stats = get_stats(username)
    theme_name = get_setting("theme") or "Midnight"
    font_name = get_setting("font") or "Inter"

    with st.sidebar:
        st.markdown(f"## {avatar} BrainDump")
        st.caption(f"Logged in as **{display_name}**")
        st.markdown("---")

        st.page_link("app.py", label="🏠 Home")
        st.page_link("pages/1_📝_Notes.py", label="📝 Notes")
        st.page_link("pages/2_💬_Chat.py", label="💬 Chat")
        st.page_link("pages/3_🧠_Flashcards.py", label="🧠 Flashcards")
        st.page_link("pages/4_📝_Quiz.py", label="📝 Quiz")
        st.page_link("pages/5_📖_Study.py", label="📖 Study")
        st.page_link("pages/6_📊_Progress.py", label="📊 Progress")
        st.page_link("pages/7_⚙️_Settings.py", label="⚙️ Settings")
        st.page_link("pages/8_🏆_Credits.py", label="🏆 Credits")
        st.page_link("pages/9_👤_Profile.py", label="👤 Profile")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📝 Notes", stats["total_notes"])
        with col2:
            st.metric("🧠 Cards", stats["total_flashcards"])
        st.metric("📊 Quizzes", stats["total_quizzes"])

        st.markdown("---")
        st.caption(f"🎨 {theme_name} · 🔤 {font_name}")

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.display_name = ""
            st.rerun()


# ── Note Templates ───────────────────────────────────────────

NOTE_TEMPLATES = {
    "📝 Lecture Notes": """# Lecture Notes
## Date:
## Topic:
## Key Points
-
-
-
## Detailed Notes

## Summary

## Questions to Review
""",
    "📖 Chapter Summary": """# Chapter Summary
## Chapter:
## Main Ideas
-
-
## Key Vocabulary
| Term | Definition |
|------|-----------|
|      |           |
## Important Details

## Summary
""",
    "🔬 Lab Report": """# Lab Report
## Experiment:
## Date:
## Objective

## Materials

## Method
1.
2.
3.
## Results

## Conclusion
""",
    "📊 Formula Sheet": """# Formula Sheet
## Subject:
## Formulas
| Formula | Description | Example |
|---------|------------|---------|
|         |            |         |
## Key Concepts

## Practice Problems
""",
    "📋 Blank Notes": """# Title

## Notes
""",
}

# ── Motivational Quotes ──────────────────────────────────────

MOTIVATIONAL_QUOTES = [
    "All good things take time. Keep going. 🌱",
    "Small progress is still progress. 📈",
    "The expert in anything was once a beginner. 🎯",
    "Study hard now, celebrate later. 🏆",
    "Your future self will thank you. ⭐",
    "Dream big, start small, act now. 🚀",
    "Mistakes are proof that you are trying. 💪",
    "Learning is a treasure that follows its owner. 💎",
]
