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
    accent = c["accent"]
    bg = c["background"]
    cards = c["cards"]
    primary = c["primary_text"]
    secondary = c["secondary_text"]

    st.markdown(f"""
    <style>
    /* ══════════════════════════════════════════════════════ */
    /* FONTS                                                */
    /* ══════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Merriweather:wght@400;700&display=swap');

    .stApp, .stApp * {{ font-family: {font_family} !important; }}
    .stApp code, .stApp pre {{ font-family: 'JetBrains Mono', monospace !important; }}

    /* ══════════════════════════════════════════════════════ */
    /* 10. PAGE TRANSITIONS                                  */
    /* ══════════════════════════════════════════════════════ */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .main .block-container {{
        animation: fadeIn 0.4s ease-out;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* BASE APP                                              */
    /* ══════════════════════════════════════════════════════ */
    .stApp {{ background-color: {bg}; }}

    /* Hide Streamlit built-in nav */
    [data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavLink"], ul[data-testid="stSidebarNavItems"] {{
        display: none !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* TYPOGRAPHY                                            */
    /* ══════════════════════════════════════════════════════ */
    .stApp h1 {{ font-size: 32px !important; font-weight: 700 !important; color: {primary} !important; }}
    .stApp h2 {{ font-size: 24px !important; font-weight: 600 !important; color: {primary} !important; }}
    .stApp h3 {{ font-size: 20px !important; font-weight: 500 !important; color: {secondary} !important; }}
    .stApp .stMarkdown p {{ color: {primary} !important; line-height: 1.6 !important; }}
    .stApp label {{ color: {primary} !important; }}

    /* ══════════════════════════════════════════════════════ */
    /* 1. CARDS                                              */
    /* ══════════════════════════════════════════════════════ */
    .note-card, .flashcard, .score-card, .quiz-question,
    .suggestion-card, .stat-card, .credit-card, .quiz-card,
    .about-box, .quote-card, .streak-card {{
        background-color: {cards} !important;
        border: 1px solid {accent}33 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        transition: all 0.3s ease !important;
    }}
    .note-card:hover, .stat-card:hover, .credit-card:hover,
    .suggestion-card:hover, .quiz-card:hover, .quote-card:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25) !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* 2. BUTTONS                                            */
    /* ══════════════════════════════════════════════════════ */
    .stButton > button {{
        background-color: {accent} !important;
        color: {primary} !important;
        border: 1px solid {accent} !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        filter: brightness(1.1) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* 3. INPUTS                                             */
    /* ══════════════════════════════════════════════════════ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-radius: 10px !important;
        border: 1px solid {accent}4D !important;
        background-color: {cards} !important;
        color: {primary} !important;
        transition: border-color 0.2s ease !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 2px {accent}33 !important;
    }}
    .stSelectbox > div > div > div {{
        border-radius: 10px !important;
        border: 1px solid {accent}4D !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* 4. SIDEBAR                                            */
    /* ══════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {cards} 0%, {bg} 100%) !important;
    }}
    section[data-testid="stSidebar"] .stPageLink {{
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }}
    section[data-testid="stSidebar"] .stPageLink a:hover {{
        background-color: {accent}22 !important;
    }}
    section[data-testid="stSidebar"] .stPageLink[data-is-current="true"] {{
        border-left: 3px solid {accent} !important;
    }}
    section[data-testid="stSidebar"] .stPageLink[data-is-current="true"] a {{
        background-color: {accent}33 !important;
        color: {primary} !important;
        font-weight: 600 !important;
        border-radius: 0 10px 10px 0 !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stMetric"] {{
        background-color: {accent}1A !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* 5. FLASHCARD 3D FLIP                                  */
    /* ══════════════════════════════════════════════════════ */
    .flashcard {{
        perspective: 1000px !important;
        min-height: 300px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        font-size: 1.4rem !important;
        cursor: default !important;
    }}
    .flashcard:hover {{
        transform: none !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* 6. QUIZ OPTIONS                                       */
    /* ══════════════════════════════════════════════════════ */
    .quiz-question {{
        border: 2px solid {accent}4D !important;
    }}
    .quiz-correct {{
        border-color: #22c55e !important;
        background-color: rgba(34, 197, 94, 0.1) !important;
    }}
    .quiz-wrong {{
        border-color: #ef4444 !important;
        background-color: rgba(239, 68, 68, 0.1) !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* 7. PROGRESS BARS                                      */
    /* ══════════════════════════════════════════════════════ */
    .progress-bar {{
        background-color: {cards} !important;
        border-radius: 10px !important;
        height: 12px !important;
        overflow: hidden !important;
    }}
    .progress-fill {{
        background: linear-gradient(90deg, {accent}, {primary}33) !important;
        border-radius: 10px !important;
        height: 100% !important;
        transition: width 0.6s ease !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* 8. STREAK CIRCLES                                     */
    /* ══════════════════════════════════════════════════════ */
    .streak-card {{
        text-align: center !important;
    }}
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.15); opacity: 0.8; }}
    }}
    .streak-today {{
        animation: pulse 2s infinite;
        display: inline-block;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* 9. PROFILE AVATAR                                     */
    /* ══════════════════════════════════════════════════════ */
    .profile-avatar {{
        width: 80px !important;
        height: 80px !important;
        border-radius: 50% !important;
        border: 3px solid {accent} !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 2.5rem !important;
        margin: 0 auto 12px auto !important;
        background-color: {cards} !important;
    }}

    /* ══════════════════════════════════════════════════════ */
    /* UTILITY CLASSES                                       */
    /* ══════════════════════════════════════════════════════ */
    .subject-tag {{
        display: inline-block !important;
        background-color: {accent} !important;
        color: {primary} !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 0.85rem !important;
    }}
    .note-title, .stat-number, .grade-big {{ color: {primary} !important; }}
    .note-content, .note-date, .stat-label {{ color: {secondary} !important; }}

    .stAlert {{ border-radius: 12px !important; }}

    .empty-state {{ text-align: center; padding: 3rem; color: {secondary}; font-size: 1.2rem; }}
    .save-status {{ font-size: 0.8rem; color: {secondary}; margin-top: 0.25rem; }}
    .toolbar-hint {{ font-size: 0.75rem; color: {secondary}; margin-bottom: 0.25rem; }}

    .diff-bar {{
        height: 30px; border-radius: 8px; display: flex; align-items: center;
        padding: 0 14px; color: #fff; font-size: 0.85rem; font-weight: 600; margin: 4px 0;
    }}
    .tech-bar {{
        height: 38px; border-radius: 10px; display: flex; align-items: center;
        padding: 0 16px; background-color: {accent}; color: #fff;
        font-weight: 600; font-size: 0.9rem; margin-bottom: 8px;
    }}
    .avatar {{ font-size: 4rem; margin-bottom: 0.5rem; }}
    .tech-table {{ width: 100%; border-collapse: collapse; }}
    .tech-table td {{ padding: 0.75rem 1rem; border-bottom: 1px solid {accent}33; color: {primary}; }}
    .tech-table td:first-child {{ font-weight: 600; width: 35%; }}
    .version-text {{ color: {secondary}; font-size: 0.9rem; }}

    /* ══════════════════════════════════════════════════════ */
    /* MOBILE RESPONSIVE                                     */
    /* ══════════════════════════════════════════════════════ */
    @media (max-width: 768px) {{
        [data-testid="column"] {{ width: 100% !important; flex: 100% !important; min-width: 100% !important; }}
        .note-card, .flashcard, .quiz-card {{ width: 100% !important; margin: 8px 0 !important; }}
        .stButton > button {{ min-height: 48px !important; font-size: 16px !important; padding: 12px 24px !important; }}
        .stTextInput input, .stTextArea textarea {{ font-size: 16px !important; }}
        .main .block-container {{ padding: 1rem !important; }}
        .keyboard-hint {{ display: none !important; }}
        .flashcard {{ min-height: 220px !important; font-size: 1.2rem !important; }}
    }}
    @media (max-width: 480px) {{
        .stApp h1 {{ font-size: 24px !important; }}
        .stApp h2 {{ font-size: 20px !important; }}
        .stApp h3 {{ font-size: 18px !important; }}
        .stButton > button {{ width: 100% !important; }}
        .note-card, .stat-card, .credit-card {{ padding: 16px !important; }}
    }}

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
        st.page_link("pages/10_📋_Quiz_History.py", label="📋 Quiz History")

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


# ────────────────────────────────────────────────────────────
# Confetti celebration
# ────────────────────────────────────────────────────────────

def celebrate_confetti(emoji="🎉", duration=3):
    """Show a confetti animation using streamlit-extras."""
    try:
        from streamlit_extras.let_it_rain import rain
        rain(emoji=emoji, font_size=54, falling_speed=5, animation_length=duration)
    except ImportError:
        pass


# ────────────────────────────────────────────────────────────
# Keyboard shortcuts
# ────────────────────────────────────────────────────────────

def inject_keyboard_shortcuts():
    """Inject JavaScript for keyboard shortcuts."""
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            var btns = document.querySelectorAll('[data-testid="stButton"] button');
            for (var b of btns) {
                if (b.textContent.includes('Save')) { b.click(); break; }
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)
