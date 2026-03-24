import streamlit as st
from utils.helpers import render_sidebar, inject_custom_css, require_login
from utils.database import init_db

init_db()
require_login()

st.set_page_config(page_title="Credits - BrainDump", page_icon="🏆", layout="wide")
inject_custom_css()
render_sidebar()

st.title("🏆 Credits")
st.caption("The team behind BrainDump")

st.markdown("")

# ── Section 1: Made By ──────────────────────────────────────
st.markdown("### Made By")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="credit-card">
        <div class="avatar">👨‍💻</div>
        <h3 style="margin:0.25rem 0;">Gabriel Ndava</h3>
        <p style="margin:0; font-size:0.9rem;">Co-Creator &amp; Developer</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="credit-card">
        <div class="avatar">👨‍💻</div>
        <h3 style="margin:0.25rem 0;">Mambo Kwembeya</h3>
        <p style="margin:0; font-size:0.9rem;">Co-Creator &amp; Developer</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Section 2: Built With ───────────────────────────────────
st.markdown("### Built With")

tech_stack = [
    ("Python", 75),
    ("Streamlit", 15),
    ("SQLite", 5),
    ("OpenRouter AI", 5),
]

for name, pct in tech_stack:
    st.markdown(f"""
    <div class="tech-bar" style="width:{max(pct, 15)}%;">
        {name} &nbsp;—&nbsp; {pct}%
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Section 3: About BrainDump ──────────────────────────────
st.markdown("### About BrainDump")

st.markdown("""
<div class="about-box">
BrainDump is an AI-powered study companion built to help students
take better notes and study smarter. We believe that learning should
be simple, effective, and accessible to everyone. BrainDump uses
artificial intelligence to transform your notes into interactive
flashcards, quizzes, and study plans — making exam preparation
effortless.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Section 4: Tech Stack Details ───────────────────────────
st.markdown("### Tech Stack Details")

st.markdown("""
<table class="tech-table">
<tr><td>Python</td><td>Core application logic</td></tr>
<tr><td>Streamlit</td><td>User interface framework</td></tr>
<tr><td>SQLite</td><td>Local database for storing notes and progress</td></tr>
<tr><td>OpenRouter</td><td>AI API gateway for free AI models</td></tr>
<tr><td>MiniMax M2.5</td><td>AI model powering summaries, flashcards, and quizzes</td></tr>
</table>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Section 5: Version ──────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:1rem 0;">
    <h3>BrainDump v1.0.0</h3>
    <p class="version-text">Released 2025</p>
</div>
""", unsafe_allow_html=True)
