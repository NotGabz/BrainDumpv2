import streamlit as st
import pandas as pd
from utils.database import init_db, get_stats, get_all_quiz_results
from utils.helpers import format_date, get_performance_emoji, render_sidebar, inject_custom_css, require_login

init_db()
require_login()

st.set_page_config(page_title="Progress - BrainDump", page_icon="📊", layout="wide")
inject_custom_css()
render_sidebar()

username = st.session_state.get("username", "")

st.title("📊 Progress")
st.caption("Track your learning progress and identify areas for improvement")

stats = get_stats(username)
quiz_results = get_all_quiz_results(username)

# Overall stats
st.markdown("## 📈 Overall Statistics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">📝 {stats["total_notes"]}</div><div class="stat-label">Total Notes</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">🧠 {stats["total_flashcards"]}</div><div class="stat-label">Flashcards Studied</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">📊 {stats["total_quizzes"]}</div><div class="stat-label">Quizzes Taken</div></div>', unsafe_allow_html=True)
with col4:
    emoji = get_performance_emoji(stats['avg_score'])
    st.markdown(f'<div class="stat-card"><div class="stat-number">{emoji} {stats["avg_score"]:.1f}%</div><div class="stat-label">Average Quiz Score</div></div>', unsafe_allow_html=True)

st.markdown("---")

if not quiz_results:
    st.info("No quiz data yet! Take some quizzes to see your progress here 📊")
    if st.button("📝 Take a Quiz", type="primary"):
        st.switch_page("pages/4_📝_Quiz.py")
else:
    df = pd.DataFrame(quiz_results)
    df['taken_at'] = pd.to_datetime(df['taken_at'])

    st.markdown("## 📊 Performance Charts")

    st.markdown("### Quiz Scores Over Time")
    chart_data = df[['taken_at', 'percentage']].copy()
    chart_data = chart_data.rename(columns={'taken_at': 'Date', 'percentage': 'Score (%)'})
    chart_data = chart_data.set_index('Date')
    st.line_chart(chart_data, use_container_width=True)

    st.markdown("---")

    st.markdown("### Average Score by Subject")
    subject_scores = df.groupby('subject')['percentage'].mean().sort_values(ascending=False)
    if not subject_scores.empty:
        st.bar_chart(subject_scores, use_container_width=True)
        struggling = subject_scores[subject_scores < 70]
        if not struggling.empty:
            st.markdown("#### 🎯 Subjects Needing Improvement")
            for subject, score in struggling.items():
                st.markdown(f"""
                <div class="suggestion-card">
                    <strong>📚 {subject}</strong> — Average: {score:.1f}%<br>
                    <small style="color:#778DA9;">Consider reviewing your notes on this subject!</small>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("## 📋 Recent Quiz History")
    table_data = []
    for result in quiz_results[:20]:
        emoji = get_performance_emoji(result['percentage'])
        table_data.append({
            "Date": format_date(result['taken_at']),
            "Note": result.get('note_title', 'N/A'),
            "Subject": result['subject'],
            "Score": f"{result['score']}/{result['total_questions']}",
            "Percentage": f"{emoji} {result['percentage']:.0f}%",
        })
    if table_data:
        st.table(pd.DataFrame(table_data))

    st.markdown("---")

    st.markdown("## 💡 Study Suggestions")
    suggestions = []

    if stats['avg_score'] >= 90:
        suggestions.append(("🏆", "Outstanding Performance!", f"You're averaging {stats['avg_score']:.1f}%! Keep it up!"))
    elif stats['avg_score'] >= 70:
        suggestions.append(("✅", "Good Progress!", f"You're averaging {stats['avg_score']:.1f}%. Keep studying!"))
    else:
        suggestions.append(("📚", "Keep Going!", f"Your average is {stats['avg_score']:.1f}%. Focus on understanding core concepts."))

    if not subject_scores.empty:
        struggling = subject_scores[subject_scores < 70]
        if not struggling.empty:
            worst = struggling.idxmin()
            suggestions.append(("🎯", f"Focus on {worst}", f"You're averaging {struggling[worst]:.1f}% in {worst}. Review those notes!"))
        strong = subject_scores[subject_scores >= 90]
        if not strong.empty:
            best = strong.idxmax()
            suggestions.append(("🌟", f"Excelling in {best}!", f"Great job — {strong[best]:.1f}% average!"))

    for emoji, title, msg in suggestions:
        st.markdown(f"""
        <div class="suggestion-card">
            <h3>{emoji} {title}</h3>
            <p style="color:#778DA9; margin-top:0.5rem;">{msg}</p>
        </div>
        """, unsafe_allow_html=True)
