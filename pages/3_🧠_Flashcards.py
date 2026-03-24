import random
import streamlit as st
from utils.database import (
    init_db, get_all_notes, get_note, get_flashcards,
    save_flashcards, delete_flashcards, update_flashcard_score,
    get_setting, record_study_day,
)
from utils.ai import generate_flashcards
from utils.helpers import truncate_text, render_sidebar, inject_custom_css, require_login, play_correct_sound, play_wrong_sound

init_db()
require_login()

st.set_page_config(page_title="Flashcards - BrainDump", page_icon="🧠", layout="wide")
inject_custom_css()
render_sidebar()

username = st.session_state.get("username", "")

show_confirmations = get_setting("show_confirmations")

# Session state init
for key, default in [
    ("fc_mode", "setup"),
    ("fc_cards", []),
    ("fc_index", 0),
    ("fc_show_answer", False),
    ("fc_scores", []),
    ("fc_difficulties", []),
    ("fc_note_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("🧠 Flashcards")
st.caption("Study with flashcards using active recall")

notes = get_all_notes(username)
if not notes:
    st.info("No notes available. Create some notes first!")
    if st.button("📝 Go to Notes"):
        st.switch_page("pages/1_📝_Notes.py")
    st.stop()


def _get_difficulty_counts(cards):
    """Return dict of difficulty -> count from a list of flashcard dicts."""
    counts = {"easy": 0, "medium": 0, "hard": 0, "unrated": 0}
    for c in cards:
        d = c.get("difficulty", "unrated") or "unrated"
        counts[d] = counts.get(d, 0) + 1
    return counts


def _sort_by_spaced_repetition(cards):
    """Sort cards: hard first, then medium, then unrated, then easy last."""
    order = {"hard": 0, "medium": 1, "unrated": 2, "easy": 3}
    return sorted(cards, key=lambda c: order.get(c.get("difficulty", "unrated"), 2))


# ── SETUP MODE ──────────────────────────────────────────────
if st.session_state.fc_mode == "setup":
    note_options = {f"{n['title']} ({n['subject']})": n['id'] for n in notes}
    selected_label = st.selectbox("Select a note", list(note_options.keys()))
    selected_id = note_options[selected_label]
    note = get_note(selected_id)

    existing_fc = get_flashcards(selected_id)

    if not existing_fc:
        st.info("No flashcards for this note yet.")
        default_count = get_setting("default_flashcard_count") or 10
        count = st.slider("How many flashcards?", 5, 20, int(default_count))
        if st.button("🧠 Generate Flashcards", type="primary"):
            new_fc, err = generate_flashcards(note['content'], count)
            if err:
                st.error(err)
            else:
                save_flashcards(selected_id, new_fc)
                st.toast(f"Generated {len(new_fc)} flashcards!", icon="✅")
                st.rerun()
    else:
        st.success(f"✅ {len(existing_fc)} flashcards ready for this note.")

        # Difficulty breakdown
        dc = _get_difficulty_counts(existing_fc)
        total = len(existing_fc)
        st.markdown("#### Difficulty Breakdown")
        if dc["easy"] > 0:
            pct = dc["easy"] / total * 100
            st.markdown(f'<div class="diff-bar" style="background:#22c55e; width:{pct}%;">😊 Easy: {dc["easy"]}</div>', unsafe_allow_html=True)
        if dc["medium"] > 0:
            pct = dc["medium"] / total * 100
            st.markdown(f'<div class="diff-bar" style="background:#f59e0b; width:{pct}%;">😐 Medium: {dc["medium"]}</div>', unsafe_allow_html=True)
        if dc["hard"] > 0:
            pct = dc["hard"] / total * 100
            st.markdown(f'<div class="diff-bar" style="background:#ef4444; width:{pct}%;">😰 Hard: {dc["hard"]}</div>', unsafe_allow_html=True)
        if dc["unrated"] > 0:
            pct = dc["unrated"] / total * 100
            st.markdown(f'<div class="diff-bar" style="background:#6b7280; width:{pct}%;">❓ Unrated: {dc["unrated"]}</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("▶️ Study All", type="primary", use_container_width=True):
                cards = _sort_by_spaced_repetition(existing_fc.copy())
                st.session_state.fc_cards = cards
                st.session_state.fc_index = 0
                st.session_state.fc_show_answer = False
                st.session_state.fc_scores = []
                st.session_state.fc_difficulties = []
                st.session_state.fc_note_id = selected_id
                st.session_state.fc_mode = "study"
                st.rerun()
        with col2:
            hard_cards = [c for c in existing_fc if c.get("difficulty") == "hard"]
            if st.button(f"😰 Study Hard ({len(hard_cards)})", use_container_width=True, disabled=not hard_cards):
                st.session_state.fc_cards = hard_cards
                st.session_state.fc_index = 0
                st.session_state.fc_show_answer = False
                st.session_state.fc_scores = []
                st.session_state.fc_difficulties = []
                st.session_state.fc_note_id = selected_id
                st.session_state.fc_mode = "study"
                st.rerun()
        with col3:
            default_count = get_setting("default_flashcard_count") or 10
            count = st.slider("Count", 5, 20, int(default_count), key="regen_count")
        with col4:
            if st.button("🔄 Regenerate", use_container_width=True, help="Delete old and generate new flashcards"):
                if show_confirmations:
                    st.session_state["confirm_regen"] = True
                    st.rerun()
                else:
                    delete_flashcards(selected_id)
                    new_fc, err = generate_flashcards(note['content'], count)
                    if err:
                        st.error(err)
                    else:
                        save_flashcards(selected_id, new_fc)
                        st.toast(f"Regenerated {len(new_fc)} flashcards!", icon="✅")
                        st.rerun()

        # Regenerate confirmation
        if show_confirmations and st.session_state.get("confirm_regen"):
            st.warning("Regenerating will delete all existing flashcards for this note. Continue?")
            rc1, rc2 = st.columns(2)
            with rc1:
                if st.button("✅ Yes, regenerate", type="primary"):
                    st.session_state.pop("confirm_regen", None)
                    delete_flashcards(selected_id)
                    new_fc, err = generate_flashcards(note['content'], count)
                    if err:
                        st.error(err)
                    else:
                        save_flashcards(selected_id, new_fc)
                        st.toast(f"Regenerated {len(new_fc)} flashcards!", icon="✅")
                        st.rerun()
            with rc2:
                if st.button("❌ Cancel"):
                    st.session_state.pop("confirm_regen", None)
                    st.rerun()

        # Preview
        with st.expander("👁️ Preview flashcards"):
            for i, card in enumerate(existing_fc, 1):
                d = card.get("difficulty", "unrated")
                icon = {"easy": "😊", "medium": "😐", "hard": "😰"}.get(d, "❓")
                st.markdown(f"**{i}.** {card['front']} {icon}")

# ── STUDY MODE ──────────────────────────────────────────────
elif st.session_state.fc_mode == "study":
    cards = st.session_state.fc_cards
    idx = st.session_state.fc_index

    if idx >= len(cards):
        st.session_state.fc_mode = "results"
        st.rerun()

    card = cards[idx]
    progress = idx / len(cards)

    st.markdown(f"### Card {idx + 1} / {len(cards)}")
    st.markdown(f'<div class="progress-bar"><div class="progress-fill" style="width:{progress * 100}%"></div></div>', unsafe_allow_html=True)

    if not st.session_state.fc_show_answer:
        st.markdown(f"""
        <div class="flashcard">
            <div>
                <div style="color:#778DA9; font-size:0.9rem; margin-bottom:1rem;">QUESTION</div>
                {card['front']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👁️ Flip Card", use_container_width=True, type="primary"):
            st.session_state.fc_show_answer = True
            st.rerun()
    else:
        st.markdown(f"""
        <div class="flashcard">
            <div>
                <div style="color:#778DA9; font-size:0.9rem; margin-bottom:1rem;">ANSWER</div>
                {card['back']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**How well did you know this?**")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("😊 Easy", use_container_width=True, type="primary"):
                play_correct_sound()
                update_flashcard_score(card['id'], True, "easy")
                st.session_state.fc_scores.append(True)
                st.session_state.fc_difficulties.append("easy")
                st.session_state.fc_index += 1
                st.session_state.fc_show_answer = False
                st.rerun()
        with c2:
            if st.button("😐 Medium", use_container_width=True):
                update_flashcard_score(card['id'], True, "medium")
                st.session_state.fc_scores.append(True)
                st.session_state.fc_difficulties.append("medium")
                st.session_state.fc_index += 1
                st.session_state.fc_show_answer = False
                st.rerun()
        with c3:
            if st.button("😰 Hard", use_container_width=True):
                play_wrong_sound()
                update_flashcard_score(card['id'], False, "hard")
                st.session_state.fc_scores.append(False)
                st.session_state.fc_difficulties.append("hard")
                st.session_state.fc_index += 1
                st.session_state.fc_show_answer = False
                st.rerun()

# ── RESULTS MODE ────────────────────────────────────────────
elif st.session_state.fc_mode == "results":
    scores = st.session_state.fc_scores
    difficulties = st.session_state.fc_difficulties
    correct = sum(1 for s in scores if s)
    total = len(scores)
    pct = (correct / total * 100) if total > 0 else 0

    # Record study day for streak
    record_study_day(username)

    st.markdown("## 🎉 Session Complete!")
    st.markdown(f"""
    <div class="score-card">
        <h2>{correct}/{total} — {pct:.0f}%</h2>
    </div>
    """, unsafe_allow_html=True)

    # Difficulty breakdown
    easy_cards = [st.session_state.fc_cards[i] for i, d in enumerate(difficulties) if d == "easy"]
    medium_cards = [st.session_state.fc_cards[i] for i, d in enumerate(difficulties) if d == "medium"]
    hard_cards = [st.session_state.fc_cards[i] for i, d in enumerate(difficulties) if d == "hard"]

    st.markdown("#### Session Breakdown")
    st.markdown(f"- 😊 Easy: **{len(easy_cards)}** cards")
    st.markdown(f"- 😐 Medium: **{len(medium_cards)}** cards")
    st.markdown(f"- 😰 Hard: **{len(hard_cards)}** cards")

    if hard_cards:
        st.markdown("### Cards to review")
        for i, card in enumerate(hard_cards, 1):
            with st.expander(f"😰 Card {i}: {truncate_text(card['front'], 50)}"):
                st.markdown(f"**Q:** {card['front']}")
                st.markdown(f"**A:** {card['back']}")

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🔄 Study All Again", use_container_width=True, type="primary"):
            st.session_state.fc_cards = _sort_by_spaced_repetition(st.session_state.fc_cards)
            st.session_state.fc_index = 0
            st.session_state.fc_show_answer = False
            st.session_state.fc_scores = []
            st.session_state.fc_difficulties = []
            st.session_state.fc_mode = "study"
            st.rerun()
    with c2:
        if st.button("😰 Study Hard Only", use_container_width=True, disabled=not hard_cards):
            st.session_state.fc_cards = hard_cards
            st.session_state.fc_index = 0
            st.session_state.fc_show_answer = False
            st.session_state.fc_scores = []
            st.session_state.fc_difficulties = []
            st.session_state.fc_mode = "study"
            st.rerun()
    with c3:
        if st.button("📚 Study Medium+Hard", use_container_width=True, disabled=not (hard_cards or medium_cards)):
            medium_cards = [st.session_state.fc_cards[i] for i, d in enumerate(difficulties) if d == "medium"]
            st.session_state.fc_cards = medium_cards + hard_cards
            st.session_state.fc_index = 0
            st.session_state.fc_show_answer = False
            st.session_state.fc_scores = []
            st.session_state.fc_difficulties = []
            st.session_state.fc_mode = "study"
            st.rerun()
    with c4:
        if st.button("← Back to Notes", use_container_width=True):
            st.session_state.fc_mode = "setup"
            st.rerun()
