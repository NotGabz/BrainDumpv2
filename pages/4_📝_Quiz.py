import streamlit as st
from utils.database import (
    init_db, get_all_notes, get_note, save_quiz_result, get_setting, record_study_day,
)
from utils.ai import generate_quiz
from utils.helpers import get_grade, get_performance_emoji, render_sidebar, inject_custom_css, require_login, play_correct_sound, play_wrong_sound

init_db()
require_login()

st.set_page_config(page_title="Quiz - BrainDump", page_icon="📝", layout="wide")
inject_custom_css()
render_sidebar()

username = st.session_state.get("username", "")

for key, default in [
    ("qz_mode", "setup"),
    ("qz_questions", None),
    ("qz_index", 0),
    ("qz_answers", []),
    ("qz_submitted", False),
    ("qz_note_id", None),
    ("qz_saved", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("📝 Quiz")
st.caption("Test your knowledge with AI-generated quizzes")

notes = get_all_notes(username)
if not notes:
    st.info("No notes available. Create some notes first!")
    if st.button("📝 Go to Notes"):
        st.switch_page("pages/1_📝_Notes.py")
    st.stop()

# ── SETUP MODE ──────────────────────────────────────────────
if st.session_state.qz_mode == "setup":
    note_options = {f"{n['title']} ({n['subject']})": n['id'] for n in notes}
    selected_label = st.selectbox("Select a note", list(note_options.keys()))
    selected_id = note_options[selected_label]
    note = get_note(selected_id)

    c1, c2 = st.columns(2)
    with c1:
        default_count = get_setting("default_quiz_count") or 5
        count = st.slider("Number of questions", 3, 15, int(default_count))
    with c2:
        default_diff = get_setting("default_quiz_difficulty") or "Medium"
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=["Easy", "Medium", "Hard"].index(default_diff))

    st.markdown("")
    if st.button("📝 Generate Quiz", type="primary"):
        questions, err = generate_quiz(note['content'], count, difficulty)
        if err:
            st.error(err)
        else:
            st.session_state.qz_questions = questions
            st.session_state.qz_note_id = selected_id
            st.session_state.qz_index = 0
            st.session_state.qz_answers = [None] * len(questions)
            st.session_state.qz_submitted = False
            st.session_state.qz_saved = False
            st.session_state.qz_mode = "quiz"
            st.toast(f"Generated {len(questions)} questions!", icon="✅")
            st.rerun()

# ── QUIZ MODE ───────────────────────────────────────────────
elif st.session_state.qz_mode == "quiz":
    questions = st.session_state.qz_questions
    idx = st.session_state.qz_index

    if st.session_state.qz_submitted:
        # ── RESULTS ─────────────────────────────────────────
        correct = sum(1 for i, q in enumerate(questions) if st.session_state.qz_answers[i] == q['correct'])
        total = len(questions)
        pct = (correct / total * 100) if total > 0 else 0
        grade = get_grade(pct)
        emoji = get_performance_emoji(pct)

        # Save result once
        if not st.session_state.qz_saved:
            note = get_note(st.session_state.qz_note_id)
            if note:
                save_quiz_result(username, note['id'], note['subject'], correct, total, "Medium")
            record_study_day(username)
            st.session_state.qz_saved = True

        st.markdown("## 🎉 Quiz Complete!")
        st.markdown(f"""
        <div class="score-card">
            <div class="grade-big">{emoji} {grade}</div>
            <h3>{correct}/{total} correct — {pct:.0f}%</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📋 Review")

        for i, q in enumerate(questions):
            user_ans = st.session_state.qz_answers[i]
            is_correct = user_ans == q['correct']
            icon = "✅" if is_correct else "❌"
            with st.expander(f"{icon} Question {i+1}: {q['question'][:60]}..."):
                st.markdown(f"**{q['question']}**")
                for opt in q['options']:
                    if opt.startswith(q['correct']):
                        st.markdown(f"✅ {opt} *(correct)*")
                    elif opt.startswith(user_ans) and not is_correct:
                        st.markdown(f"❌ {opt} *(your answer)*")
                    else:
                        st.markdown(f"  {opt}")
                st.markdown(f"**Explanation:** {q['explanation']}")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Retake Same Quiz", use_container_width=True, type="primary"):
                st.session_state.qz_index = 0
                st.session_state.qz_answers = [None] * len(questions)
                st.session_state.qz_submitted = False
                st.session_state.qz_saved = False
                st.rerun()
        with c2:
            if st.button("📝 Generate New Quiz", use_container_width=True):
                st.session_state.qz_mode = "setup"
                st.session_state.qz_questions = None
                st.rerun()

    elif idx < len(questions):
        # ── ACTIVE QUESTION ──────────────────────────────────
        q = questions[idx]
        progress = idx / len(questions)

        st.markdown(f"### Question {idx + 1} / {len(questions)}")
        st.markdown(f'<div class="progress-bar"><div class="progress-fill" style="width:{progress * 100}%"></div></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="quiz-question">
            <h3 style="color:#E0E1DD;">{q['question']}</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.qz_answers[idx] is None:
            for option in q['options']:
                letter = option[0]
                if st.button(option, use_container_width=True, key=f"q{idx}_{letter}", help=f"Select {letter}"):
                    st.session_state.qz_answers[idx] = letter
                    st.rerun()
        else:
            user_ans = st.session_state.qz_answers[idx]
            is_correct = user_ans == q['correct']
            if is_correct:
                play_correct_sound()
                st.success("✅ Correct!")
            else:
                play_wrong_sound()
                st.error(f"❌ Wrong — the correct answer is **{q['correct']}**")
                st.info(f"💡 {q['explanation']}")

            if idx < len(questions) - 1:
                if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                    st.session_state.qz_index += 1
                    st.rerun()
            else:
                if st.button("✅ Finish Quiz", use_container_width=True, type="primary"):
                    st.session_state.qz_submitted = True
                    st.rerun()
