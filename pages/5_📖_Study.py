import streamlit as st
from utils.database import init_db, get_all_notes, get_note, update_summary, update_study_plan
from utils.ai import summarize_notes, explain_concept, generate_study_plan
from utils.helpers import render_sidebar, inject_custom_css, require_login

init_db()
require_login()

st.set_page_config(page_title="Study - BrainDump", page_icon="📖", layout="wide")
inject_custom_css()

username = st.session_state.get("username", "")

if "explain_history" not in st.session_state:
    st.session_state.explain_history = []

render_sidebar()

st.title("📖 Study")
st.caption("Summaries, explanations, and study plans to help you learn effectively")

notes = get_all_notes(username)
if not notes:
    st.info("No notes available. Create some notes first!")
    if st.button("📝 Go to Notes"):
        st.switch_page("pages/1_📝_Notes.py")
    st.stop()

note_options = {f"{n['title']} ({n['subject']})": n['id'] for n in notes}
selected_label = st.selectbox("Select a note", list(note_options.keys()))
selected_id = note_options[selected_label]
note = get_note(selected_id)

if not note:
    st.error("Note not found")
    st.stop()

st.markdown("---")

tab_summary, tab_explain, tab_plan = st.tabs(["📝 Summary", "💡 Explain", "📅 Study Plan"])

# ── SUMMARY TAB ─────────────────────────────────────────────
with tab_summary:
    st.markdown("Generate a concise summary of your note's key concepts.")

    if note.get('summary'):
        st.markdown("#### Saved Summary")
        st.markdown(note['summary'])
        if st.button("🔄 Regenerate Summary"):
            new_summary, err = summarize_notes(note['content'])
            if err:
                st.error(err)
            else:
                update_summary(note['id'], new_summary)
                st.toast("Summary regenerated!", icon="✅")
                st.rerun()
    else:
        if st.button("✨ Generate Summary", type="primary"):
            summary, err = summarize_notes(note['content'])
            if err:
                st.error(err)
            else:
                update_summary(note['id'], summary)
                st.toast("Summary saved!", icon="✅")
                st.rerun()

# ── EXPLAIN TAB ─────────────────────────────────────────────
with tab_explain:
    st.markdown("Get a simple explanation of any concept from your notes.")

    concept = st.text_input(
        "What concept do you need explained?",
        placeholder="e.g. photosynthesis, recursion, supply and demand...",
    )
    if st.button("💡 Explain This", type="primary", disabled=not concept):
        explanation, err = explain_concept(concept)
        if err:
            st.error(err)
        else:
            st.session_state.explain_history.insert(0, {"concept": concept, "explanation": explanation})
            st.rerun()

    if st.session_state.explain_history:
        st.markdown("---")
        st.markdown("#### Previous Explanations")
        for item in st.session_state.explain_history:
            with st.expander(f"💡 {item['concept']}"):
                st.markdown(item['explanation'])

# ── STUDY PLAN TAB ──────────────────────────────────────────
with tab_plan:
    st.markdown("Get a personalized study plan based on your note content.")

    if note.get('study_plan'):
        st.markdown("#### Saved Study Plan")
        st.markdown(note['study_plan'])
        if st.button("🔄 Regenerate Study Plan"):
            plan, err = generate_study_plan(note['content'])
            if err:
                st.error(err)
            else:
                update_study_plan(note['id'], plan)
                st.toast("Study plan regenerated!", icon="✅")
                st.rerun()
    else:
        if st.button("📅 Generate Study Plan", type="primary"):
            plan, err = generate_study_plan(note['content'])
            if err:
                st.error(err)
            else:
                update_study_plan(note['id'], plan)
                st.toast("Study plan saved!", icon="✅")
                st.rerun()
