import random
import streamlit as st
from datetime import date, timedelta
from utils.database import (
    init_db, get_stats, get_all_notes, get_all_quiz_results,
    create_user, authenticate_user, get_streak_data,
)
from utils.helpers import (
    format_date, truncate_text, render_sidebar, inject_custom_css,
    MOTIVATIONAL_QUOTES,
)

init_db()

st.set_page_config(page_title="BrainDump - AI Study Helper", page_icon="🧠", layout="wide")
inject_custom_css()

# ── Login / Sign Up ──────────────────────────────────────────

if not st.session_state.get("logged_in"):
    st.markdown("<h1 style='text-align:center;'>🧠 BrainDump</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#778DA9;'>Your AI-Powered Study Companion</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.radio("", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")

        if auth_mode == "Login":
            st.markdown("### Welcome back! 👋")
            username = st.text_input("Username", key="login_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            if st.button("🔓 Log In", type="primary", use_container_width=True):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user["username"]
                    st.session_state.display_name = user["display_name"]
                    st.toast(f"Welcome back, {user['display_name']}!", icon="✅")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        else:
            st.markdown("### Create an account ✨")
            display_name = st.text_input("Display Name", key="signup_name", placeholder="e.g., Gabriel Ndava")
            new_username = st.text_input("Username", key="signup_user", placeholder="e.g., gabriel")
            new_password = st.text_input("Password", type="password", key="signup_pass", placeholder="Min 6 characters")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Re-enter password")
            if st.button("✨ Sign Up", type="primary", use_container_width=True):
                if not display_name.strip():
                    st.error("Display name is required")
                elif len(new_username.strip()) < 2:
                    st.error("Username must be at least 2 characters")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif new_password != confirm:
                    st.error("Passwords do not match")
                else:
                    ok, err = create_user(new_username, display_name, new_password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.username = new_username.strip()
                        st.session_state.display_name = display_name.strip()
                        st.toast("Account created! Welcome!", icon="🎉")
                        st.rerun()
                    else:
                        st.error(err)
    st.stop()

# ── Dashboard (logged in) ───────────────────────────────────

render_sidebar()

username = st.session_state.get("username", "")
display_name = st.session_state.get("display_name", "")

st.markdown(f'<h1 style="text-align:center;">🧠 BrainDump</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center;color:#778DA9;">Welcome back, {display_name}!</p>', unsafe_allow_html=True)

# Stats
stats = get_stats(username)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">📝 {stats["total_notes"]}</div><div class="stat-label">Notes</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">🗂️ {stats["total_subjects"]}</div><div class="stat-label">Subjects</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">🧠 {stats["total_flashcards"]}</div><div class="stat-label">Flashcards</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">📊 {stats["total_quizzes"]}</div><div class="stat-label">Quizzes</div></div>', unsafe_allow_html=True)

st.markdown("")

# Motivational Quote
st.markdown("### 💡 Daily Motivation")
if "current_quote" not in st.session_state:
    st.session_state.current_quote = random.choice(MOTIVATIONAL_QUOTES)

st.markdown(f"""
<div class="quote-card" style="text-align:center; font-style:italic; font-size:1.2rem; padding:2rem;">
    <span style="font-size:2rem;color:#415A77;">"</span>{st.session_state.current_quote}<span style="font-size:2rem;color:#415A77;">"</span>
</div>
""", unsafe_allow_html=True)
if st.button("🔄 New Quote"):
    st.session_state.current_quote = random.choice(MOTIVATIONAL_QUOTES)
    st.rerun()

st.markdown("")

# Streak
st.markdown("### 🔥 Study Streak")
streak_data = get_streak_data(username)
streak = streak_data["streak"]
days = streak_data["days"]

day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
# Map dates to day names
from datetime import date as dt_date
day_labels = [dt_date.fromisoformat(d["date"]).strftime("%a") for d in days]

circles = "  ".join(["✅" if d["studied"] else "⭕" for d in days])
labels = "  ".join(day_labels)

st.markdown(f"""
<div class="streak-card" style="text-align:center;">
    <div style="font-size:1.5rem; letter-spacing:4px;">{circles}</div>
    <div style="color:#778DA9; font-size:0.85rem; letter-spacing:4px; margin-top:4px;">{labels}</div>
    <div style="margin-top:8px; font-weight:600;">🔥 {streak} / 7 Day Streak</div>
</div>
""", unsafe_allow_html=True)

if streak == 0:
    st.caption("Start your streak today! 💪")
elif streak <= 2:
    st.caption("Good start! 🌱")
elif streak <= 4:
    st.caption("Keep it up! 🔥")
elif streak <= 6:
    st.caption("Almost there! 🚀")
else:
    st.caption("PERFECT WEEK! 🏆🎉")

st.markdown("")

# Quick Actions
if stats["total_notes"] == 0:
    st.info("No notes yet! Create your first note to get started.")
    if st.button("📝 Create Your First Note", type="primary"):
        st.switch_page("pages/1_📝_Notes.py")
else:
    st.markdown("### 🚀 Quick Actions")
    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        if st.button("📝 Create New Note", type="primary", use_container_width=True):
            st.switch_page("pages/1_📝_Notes.py")
    with qc2:
        if st.button("🧠 Start Studying", use_container_width=True):
            st.switch_page("pages/3_🧠_Flashcards.py")
    with qc3:
        if st.button("📊 View Progress", use_container_width=True):
            st.switch_page("pages/6_📊_Progress.py")
