import streamlit as st
from utils.database import (
    init_db, get_all_settings, set_setting, get_all_notes,
    clear_all_data, write_theme_config, THEMES, FONTS,
)
from utils.helpers import render_sidebar, inject_custom_css, require_login

init_db()
require_login()

st.set_page_config(page_title="Settings - BrainDump", page_icon="⚙️", layout="wide")
inject_custom_css()
render_sidebar()

username = st.session_state.get("username", "")
display_name = st.session_state.get("display_name", "")

st.title("⚙️ Settings")
st.caption("Customize your BrainDump experience")

settings = get_all_settings()

# ── Theme Selector ──────────────────────────────────────────
st.markdown("## 🎨 Theme")
current_theme = settings.get("theme", "Midnight")
theme_items = list(THEMES.items())
for row_themes in [theme_items[:3], theme_items[3:]]:
    cols = st.columns(len(row_themes))
    for i, (name, colors) in enumerate(row_themes):
        with cols[i]:
            is_selected = name == current_theme
            border = f"3px solid {colors['accent']}" if is_selected else f"1px solid {colors['accent']}"
            check = "✅ " if is_selected else ""
            st.markdown(f"""
            <div style="background-color:{colors['background']};padding:1.2rem;border-radius:12px;border:{border};text-align:center;margin-bottom:0.5rem;min-height:120px;">
                <div style="color:{colors['primary_text']};font-weight:bold;font-size:1.05rem;margin-bottom:0.5rem;">{check}{name}</div>
                <div style="display:flex;justify-content:center;gap:6px;margin-top:0.5rem;">
                    <div style="width:22px;height:22px;border-radius:50%;background-color:{colors['background']};border:1px solid {colors['secondary_text']};"></div>
                    <div style="width:22px;height:22px;border-radius:50%;background-color:{colors['cards']};"></div>
                    <div style="width:22px;height:22px;border-radius:50%;background-color:{colors['accent']};"></div>
                    <div style="width:22px;height:22px;border-radius:50%;background-color:{colors['secondary_text']};"></div>
                    <div style="width:22px;height:22px;border-radius:50%;background-color:{colors['primary_text']};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if not is_selected:
                if st.button(f"Apply {name}", use_container_width=True, key=f"theme_{name}"):
                    set_setting("theme", name); write_theme_config(name)
                    st.toast(f"Theme: {name}!", icon="🎨"); st.rerun()

st.markdown("---")

# ── Font ────────────────────────────────────────────────────
st.markdown("## 🔤 Font")
current_font = settings.get("font", "Inter")
font_names = list(FONTS.keys())
font_idx = font_names.index(current_font) if current_font in font_names else 0
selected_font = st.selectbox("Font", font_names, index=font_idx)
if selected_font != current_font:
    set_setting("font", selected_font); st.toast(f"Font: {selected_font}!", icon="🔤"); st.rerun()

st.markdown("---")

# ── Preferences ─────────────────────────────────────────────
st.markdown("## 📋 Preferences")

new_confirm = st.toggle("Show confirmation dialogs", value=settings.get("show_confirmations", True))
if new_confirm != settings.get("show_confirmations"):
    set_setting("show_confirmations", new_confirm); st.toast("Saved!", icon="✅")

new_sound = st.toggle("🔊 Sound Effects", value=settings.get("sound_effects", True))
if new_sound != settings.get("sound_effects"):
    set_setting("sound_effects", new_sound); st.toast("Saved!", icon="✅")

st.markdown("")
c1, c2, c3 = st.columns(3)
with c1:
    fc = st.slider("Default flashcard count", 5, 20, int(settings.get("default_flashcard_count", 10)))
    if fc != settings.get("default_flashcard_count"):
        set_setting("default_flashcard_count", fc); st.toast("Saved!", icon="✅")
with c2:
    qz = st.slider("Default quiz count", 3, 15, int(settings.get("default_quiz_count", 5)))
    if qz != settings.get("default_quiz_count"):
        set_setting("default_quiz_count", qz); st.toast("Saved!", icon="✅")
with c3:
    diff_options = ["Easy", "Medium", "Hard"]
    cur_diff = settings.get("default_quiz_difficulty", "Medium")
    d_idx = diff_options.index(cur_diff) if cur_diff in diff_options else 1
    d = st.selectbox("Default quiz difficulty", diff_options, index=d_idx)
    if d != cur_diff:
        set_setting("default_quiz_difficulty", d); st.toast("Saved!", icon="✅")

st.markdown("---")
st.markdown("## 🤖 AI Settings")
st.markdown("AI Model: **MiniMax M2.5**")

st.markdown("---")

# ── Data Management ─────────────────────────────────────────
st.markdown("## 📦 Data Management")
c1, c2 = st.columns(2)
with c1:
    st.markdown("### Export All Notes")
    notes = get_all_notes(username)
    if notes:
        export_format = st.radio("Format", [".md", ".txt"], horizontal=True)
        if st.button("📥 Export", use_container_width=True):
            content = ""
            for note in notes:
                if export_format == ".md":
                    content += f"# {note['title']}\n\n**Subject:** {note['subject']}\n\n{note['content']}\n\n---\n\n"
                else:
                    content += f"{'='*60}\n{note['title']}\nSubject: {note['subject']}\n{'='*60}\n\n{note['content']}\n\n"
            ext = "md" if export_format == ".md" else "txt"
            mime = "text/markdown" if export_format == ".md" else "text/plain"
            st.download_button(f"💾 Download .{ext}", content, file_name=f"braindump_notes.{ext}", mime=mime, use_container_width=True)
    else:
        st.info("No notes to export")
with c2:
    st.markdown("### Clear All Data")
    st.warning("Permanently deletes all your notes, flashcards, and quiz results.")
    if st.checkbox("I understand this cannot be undone"):
        if st.checkbox("I really want to delete everything"):
            if st.button("🗑️ Delete All Data", type="primary", use_container_width=True):
                clear_all_data(username)
                st.toast("All data cleared!", icon="🗑️"); st.rerun()
