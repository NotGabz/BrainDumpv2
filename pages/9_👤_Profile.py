import streamlit as st
from utils.database import (
    init_db, get_stats, get_user_info, update_user_display_name,
    get_setting, set_setting,
)
from utils.helpers import render_sidebar, inject_custom_css, require_login, format_date

init_db()
require_login()

st.set_page_config(page_title="Profile - BrainDump", page_icon="👤", layout="wide")
inject_custom_css()
render_sidebar()

username = st.session_state.get("username", "")
display_name = st.session_state.get("display_name", "")
user_info = get_user_info(username)
stats = get_stats(username)
current_avatar = get_setting(f"avatar_{username}") or "🧑‍🎓"

st.title("👤 My Profile")
st.caption("Your BrainDump profile and stats")

st.markdown("")

# ── Section 1: User Info ─────────────────────────────────────
st.markdown("### User Info")
st.markdown(f"""
<div class="credit-card" style="text-align:center;">
    <div class="avatar">{current_avatar}</div>
    <h2>{display_name}</h2>
    <p style="color:#778DA9;">@{username}</p>
    <p style="color:#778DA9;">Member since: {format_date(user_info['created_at']) if user_info else 'N/A'}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Section 2: My Stats ─────────────────────────────────────
st.markdown("### 📊 My Stats")
sc1, sc2, sc3 = st.columns(3)
with sc1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">📝 {stats["total_notes"]}</div><div class="stat-label">Notes Created</div></div>', unsafe_allow_html=True)
with sc2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">🧠 {stats["total_flashcards"]}</div><div class="stat-label">Flashcards Studied</div></div>', unsafe_allow_html=True)
with sc3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">📊 {stats["total_quizzes"]}</div><div class="stat-label">Quizzes Taken</div></div>', unsafe_allow_html=True)

sc4, sc5, sc6 = st.columns(3)
with sc4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">📈 {stats["avg_score"]}%</div><div class="stat-label">Average Score</div></div>', unsafe_allow_html=True)
with sc5:
    st.markdown(f'<div class="stat-card"><div class="stat-number">🏆 {stats["best_score"]}%</div><div class="stat-label">Best Score</div></div>', unsafe_allow_html=True)
with sc6:
    st.markdown(f'<div class="stat-card"><div class="stat-number">📚 {stats["favorite_subject"]}</div><div class="stat-label">Favorite Subject</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Section 3: Preferences ──────────────────────────────────
st.markdown("### ⚙️ Preferences")

st.markdown("**Avatar**")
avatars = ["🧑‍🎓", "👨‍💻", "👩‍🔬", "🧑‍🏫", "🦊"]
av_cols = st.columns(5)
for i, av in enumerate(avatars):
    with av_cols[i]:
        is_current = av == current_avatar
        if st.button(av, key=f"av_{i}", use_container_width=True, type="primary" if is_current else "secondary"):
            set_setting(f"avatar_{username}", av)
            st.toast(f"Avatar updated!", icon="✅")
            st.rerun()

st.markdown("")
new_display_name = st.text_input("Display Name", value=display_name)
if st.button("💾 Save Display Name", type="primary"):
    if new_display_name.strip():
        update_user_display_name(username, new_display_name)
        st.session_state.display_name = new_display_name.strip()
        st.toast("Display name updated!", icon="✅")
        st.rerun()
