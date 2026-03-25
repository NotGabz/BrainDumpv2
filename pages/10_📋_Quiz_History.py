import streamlit as st
import pandas as pd
from utils.database import init_db, get_all_quiz_results, get_stats, get_all_subjects
from utils.helpers import format_date, get_grade, get_performance_emoji, render_sidebar, inject_custom_css, require_login

init_db()
require_login()

st.set_page_config(page_title="Quiz History - BrainDump", page_icon="📋", layout="wide")
inject_custom_css()
render_sidebar()

username = st.session_state.get("username", "")

st.title("📋 Quiz History")
st.caption("Review all your past quiz attempts")

results = get_all_quiz_results(username)

if not results:
    st.info("No quiz history yet! Take a quiz to see your results here.")
    if st.button("📝 Take a Quiz", type="primary"):
        st.switch_page("pages/4_📝_Quiz.py")
    st.stop()

# ── Overview ─────────────────────────────────────────────────
st.markdown("### 📊 Overview")
stats = get_stats(username)
oc1, oc2, oc3, oc4 = st.columns(4)
with oc1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_quizzes"]}</div><div class="stat-label">Total Quizzes</div></div>', unsafe_allow_html=True)
with oc2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["avg_score"]}%</div><div class="stat-label">Average Score</div></div>', unsafe_allow_html=True)
with oc3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["best_score"]}%</div><div class="stat-label">Best Score</div></div>', unsafe_allow_html=True)
with oc4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["favorite_subject"]}</div><div class="stat-label">Top Subject</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Score Trends ─────────────────────────────────────────────
st.markdown("### 📈 Score Trends")
df = pd.DataFrame(results)
df['taken_at'] = pd.to_datetime(df['taken_at'])
df['date'] = df['taken_at'].dt.strftime('%Y-%m-%d')

try:
    import plotly.express as px
    fig = px.line(df.sort_values('taken_at'), x='taken_at', y='percentage', color='subject',
                  markers=True, title='Quiz Scores Over Time',
                  labels={'taken_at': 'Date', 'percentage': 'Score (%)', 'subject': 'Subject'})
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
except ImportError:
    chart_data = df[['taken_at', 'percentage']].sort_values('taken_at').set_index('taken_at')
    st.line_chart(chart_data, use_container_width=True)

st.markdown("---")

# ── History Table ────────────────────────────────────────────
st.markdown("### 📋 Quiz History")

# Filters
fc1, fc2 = st.columns(2)
subjects = ["All"] + sorted(df['subject'].dropna().unique().tolist())
with fc1:
    filter_subject = st.selectbox("Filter by subject", subjects)
with fc2:
    filter_search = st.text_input("Search", placeholder="Search by note title...")

filtered = df.copy()
if filter_subject != "All":
    filtered = filtered[filtered['subject'] == filter_subject]
if filter_search:
    filtered = filtered[filtered['note_title'].str.contains(filter_search, case=False, na=False)]

# Build display table
table_data = []
for _, row in filtered.iterrows():
    grade = get_grade(row['percentage'])
    grade_emoji = get_performance_emoji(row['percentage'])
    table_data.append({
        "Date": format_date(row['taken_at']),
        "Subject": row.get('subject', 'N/A'),
        "Note": row.get('note_title', 'N/A'),
        "Difficulty": row.get('difficulty', 'Medium'),
        "Score": f"{row['score']}/{row['total_questions']}",
        "Percentage": f"{grade_emoji} {row['percentage']:.0f}%",
        "Grade": grade,
    })

if table_data:
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
else:
    st.info("No matching results")
