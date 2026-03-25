import streamlit as st
from utils.database import init_db, get_all_notes, get_note
from utils.ai import chat_about_notes
from utils.helpers import render_sidebar, inject_custom_css, require_login

init_db()
require_login()

st.set_page_config(page_title="Chat - BrainDump", page_icon="💬", layout="wide")
inject_custom_css()
render_sidebar()

username = st.session_state.get("username", "")

st.title("💬 Chat")
st.caption("Talk to AI about your notes — ask questions, get explanations, and deepen your understanding")

notes = get_all_notes(username)
if not notes:
    st.info("No notes available. Create some notes first!")
    if st.button("📝 Go to Notes"):
        st.switch_page("pages/1_📝_Notes.py")
    st.stop()

# Note selector
note_options = {f"{n['title']} ({n['subject']})": n['id'] for n in notes}
selected_label = st.selectbox("Select a note to chat about", list(note_options.keys()))
selected_id = note_options[selected_label]
note = get_note(selected_id)

if not note:
    st.error("Note not found")
    st.stop()

# Collapsible note content
with st.expander("📄 View note content", expanded=False):
    st.markdown(f"**{note['title']}** — {note['subject']}")
    st.markdown(note['content'])

st.markdown("---")

# Chat state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_note_id" not in st.session_state:
    st.session_state.chat_note_id = None

# Reset chat if note changed
if st.session_state.chat_note_id != selected_id:
    st.session_state.chat_messages = []
    st.session_state.chat_note_id = selected_id

# Suggested questions
st.markdown("#### 💡 Suggested Questions")
sq_col1, sq_col2, sq_col3, sq_col4 = st.columns(4)
suggestions = [
    ("Summarize this for me", sq_col1),
    ("What are the key points?", sq_col2),
    ("Explain this simply", sq_col3),
    ("Quiz me on this", sq_col4),
]
for text, col in suggestions:
    with col:
        if st.button(text, use_container_width=True, key=f"sug_{text}"):
            st.session_state.chat_messages.append({"role": "user", "content": text})
            answer, err = chat_about_notes(note['content'], text, st.session_state.chat_messages[:-1])
            if err:
                st.session_state.chat_messages.append({"role": "assistant", "content": f"⚠️ {err}"})
            else:
                st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()

st.markdown("---")

# Chat messages
st.markdown("#### 💬 Conversation")
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_messages:
        st.markdown('<p style="color:#778DA9; text-align:center; padding:2rem;">Start a conversation by typing a question below or clicking a suggestion above.</p>', unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-end; margin-bottom:0.75rem;">
                    <div style="background-color:#415A77; color:#E0E1DD; padding:0.75rem 1rem; border-radius:12px 12px 2px 12px; max-width:70%;">
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-start; margin-bottom:0.75rem;">
                    <div style="background-color:#1B263B; color:#E0E1DD; padding:0.75rem 1rem; border-radius:12px 12px 12px 2px; max-width:70%; border:1px solid #415A77;">
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Input area
st.markdown("")
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Your question", placeholder="Ask anything about this note...", label_visibility="collapsed")
    c1, c2 = st.columns([5, 1])
    with c1:
        submitted = st.form_submit_button("💬 Send", type="primary", use_container_width=True)
    with c2:
        clear = st.form_submit_button("🗑️ Clear", use_container_width=True)

if submitted and user_input:
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    answer, err = chat_about_notes(note['content'], user_input, st.session_state.chat_messages[:-1])
    if err:
        st.session_state.chat_messages.append({"role": "assistant", "content": f"⚠️ {err}"})
    else:
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    st.rerun()

if clear:
    st.session_state.chat_messages = []
    st.toast("Chat cleared", icon="🗑️")
    st.rerun()
