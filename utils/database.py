import sqlite3
import hashlib
import os
import random
import string
from datetime import datetime, date

DB_PATH = "braindump.db"

THEMES = {
    "Midnight": {"background": "#0D1B2A", "cards": "#1B263B", "accent": "#415A77", "secondary_text": "#778DA9", "primary_text": "#E0E1DD"},
    "Forest": {"background": "#1A1A2E", "cards": "#16213E", "accent": "#0F3460", "secondary_text": "#94A3B8", "primary_text": "#E2E8F0"},
    "Warm": {"background": "#1C1917", "cards": "#292524", "accent": "#B45309", "secondary_text": "#A8A29E", "primary_text": "#F5F5F4"},
    "Sandstone": {"background": "#6B705C", "cards": "#A5A58D", "accent": "#CB997E", "secondary_text": "#DDBEA9", "primary_text": "#FFE8D6"},
    "Evergreen": {"background": "#2F3E46", "cards": "#354F52", "accent": "#52796F", "secondary_text": "#84A98C", "primary_text": "#CAD2C5"},
}

FONTS = {
    "Inter": "Inter, sans-serif",
    "JetBrains Mono": "'JetBrains Mono', monospace",
    "Merriweather": "'Merriweather', serif",
}

DEFAULT_SETTINGS = {
    "theme": "Midnight", "font": "Inter", "default_flashcard_count": 10,
    "default_quiz_count": 5, "default_quiz_difficulty": "Medium",
    "show_confirmations": "True", "sound_effects": "True",
}


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _gen_code():
    return "".join(random.choices(string.digits, k=6))


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table with email + verification
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        email TEXT NOT NULL DEFAULT '',
        password_hash TEXT NOT NULL,
        is_verified INTEGER DEFAULT 0,
        verification_code TEXT DEFAULT '',
        reset_code TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    for col in ["email TEXT NOT NULL DEFAULT ''", "is_verified INTEGER DEFAULT 0",
                "verification_code TEXT DEFAULT ''", "reset_code TEXT DEFAULT ''"]:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col}")
        except Exception:
            pass

    c.execute("""CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL DEFAULT 'default',
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        content TEXT NOT NULL,
        summary TEXT,
        study_plan TEXT,
        is_favorite INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    for col in ["username TEXT NOT NULL DEFAULT 'default'", "is_favorite INTEGER DEFAULT 0"]:
        try:
            c.execute(f"ALTER TABLE notes ADD COLUMN {col}")
        except Exception:
            pass

    # Flashcard decks
    c.execute("""CREATE TABLE IF NOT EXISTS flashcard_decks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        note_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL
    )""")

    # Flashcards with deck_id
    c.execute("""CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER NOT NULL DEFAULT 0,
        deck_id INTEGER,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        times_correct INTEGER DEFAULT 0,
        times_wrong INTEGER DEFAULT 0,
        difficulty TEXT DEFAULT 'unrated',
        FOREIGN KEY (deck_id) REFERENCES flashcard_decks(id) ON DELETE CASCADE
    )""")
    try:
        c.execute("ALTER TABLE flashcards ADD COLUMN deck_id INTEGER")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE flashcards ADD COLUMN difficulty TEXT DEFAULT 'unrated'")
    except Exception:
        pass

    c.execute("""CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER NOT NULL DEFAULT 0,
        username TEXT NOT NULL DEFAULT 'default',
        subject TEXT,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        percentage REAL NOT NULL,
        difficulty TEXT DEFAULT 'Medium',
        taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    try:
        c.execute("ALTER TABLE quiz_results ADD COLUMN username TEXT NOT NULL DEFAULT 'default'")
    except Exception:
        pass

    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS study_streak (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        study_date DATE NOT NULL,
        UNIQUE(username, study_date)
    )""")

    conn.commit()
    for k, v in DEFAULT_SETTINGS.items():
        c.execute("SELECT 1 FROM settings WHERE key = ?", (k,))
        if not c.fetchone():
            c.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
    conn.commit()
    conn.close()


# ── Auth ─────────────────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, display_name, email, password):
    code = _gen_code()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO users (username, display_name, email, password_hash, verification_code) VALUES (?,?,?,?,?)",
                  (username.strip(), display_name.strip(), email.strip(), hash_password(password), code))
        conn.commit(); conn.close()
        return True, None, code
    except sqlite3.IntegrityError:
        return False, "Username already taken", None
    except Exception as e:
        return False, str(e), None


def verify_user(username, code):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT verification_code FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row and row[0] == code:
            c.execute("UPDATE users SET is_verified = 1, verification_code = '' WHERE username = ?", (username,))
            conn.commit(); conn.close(); return True
        conn.close(); return False
    except Exception:
        return False


def authenticate_user(username, password):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
        row = c.fetchone(); conn.close()
        if row and row["password_hash"] == hash_password(password):
            if not row["is_verified"]:
                return None, "Please verify your email first"
            return {"username": row["username"], "display_name": row["display_name"], "created_at": row["created_at"]}, None
        return None, "Invalid username or password"
    except Exception:
        return None, "Login failed"


def generate_reset_code(username):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not c.fetchone():
            conn.close(); return None, "Username not found"
        code = _gen_code()
        c.execute("UPDATE users SET reset_code = ? WHERE username = ?", (code, username))
        conn.commit(); conn.close()
        return code, None
    except Exception as e:
        return None, str(e)


def reset_password(username, code, new_password):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT reset_code FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if not row or row[0] != code:
            conn.close(); return False, "Invalid reset code"
        c.execute("UPDATE users SET password_hash = ?, reset_code = '' WHERE username = ?",
                  (hash_password(new_password), username))
        conn.commit(); conn.close(); return True, None
    except Exception as e:
        return False, str(e)


def get_user_info(username):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = c.fetchone(); conn.close(); return dict(row) if row else None
    except Exception:
        return None


def update_user_display_name(username, new_name):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE users SET display_name = ? WHERE username = ?", (new_name.strip(), username))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


# ── Settings ─────────────────────────────────────────────────

def get_setting(key):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = c.fetchone(); conn.close()
        if row:
            val = row[0]
            if val in ("True", "False"): return val == "True"
            if val.isdigit(): return int(val)
            return val
        return DEFAULT_SETTINGS.get(key)
    except Exception:
        return DEFAULT_SETTINGS.get(key)


def set_setting(key, value):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def get_all_settings():
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT key, value FROM settings"); rows = c.fetchall(); conn.close()
        settings = dict(DEFAULT_SETTINGS)
        for row in rows:
            val = row[1]
            if val in ("True", "False"): val = val == "True"
            elif val.isdigit(): val = int(val)
            settings[row[0]] = val
        return settings
    except Exception:
        return dict(DEFAULT_SETTINGS)


def write_theme_config(theme_name):
    colors = THEMES.get(theme_name, THEMES["Midnight"])
    path = os.path.join(".streamlit", "config.toml")
    try:
        os.makedirs(".streamlit", exist_ok=True)
        with open(path, "w") as f:
            f.write(f'[theme]\nprimaryColor = "{colors["accent"]}"\nbackgroundColor = "{colors["background"]}"\n'
                    f'secondaryBackgroundColor = "{colors["cards"]}"\ntextColor = "{colors["primary_text"]}"\nfont = "sans serif"\n')
        return True
    except Exception:
        return False


def clear_all_data(username):
    try:
        conn = get_connection(); c = conn.cursor()
        note_ids = [r[0] for r in c.execute("SELECT id FROM notes WHERE username = ?", (username,)).fetchall()]
        for nid in note_ids:
            c.execute("DELETE FROM flashcards WHERE note_id = ?", (nid,))
        deck_ids = [r[0] for r in c.execute("SELECT id FROM flashcard_decks WHERE username = ?", (username,)).fetchall()]
        for did in deck_ids:
            c.execute("DELETE FROM flashcards WHERE deck_id = ?", (did,))
        c.execute("DELETE FROM quiz_results WHERE username = ?", (username,))
        c.execute("DELETE FROM flashcard_decks WHERE username = ?", (username,))
        c.execute("DELETE FROM notes WHERE username = ?", (username,))
        c.execute("DELETE FROM study_streak WHERE username = ?", (username,))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


# ── Notes ────────────────────────────────────────────────────

def add_note(username, title, subject, content):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO notes (username, title, subject, content) VALUES (?,?,?,?)",
                  (username, title, subject, content))
        nid = c.lastrowid; conn.commit(); conn.close(); return nid
    except Exception:
        return None


def get_all_notes(username):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT * FROM notes WHERE username = ? ORDER BY is_favorite DESC, created_at DESC", (username,))
        notes = [dict(r) for r in c.fetchall()]; conn.close(); return notes
    except Exception:
        return []


def get_notes_by_subject(username, subject):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT * FROM notes WHERE username = ? AND subject = ? ORDER BY is_favorite DESC, created_at DESC",
                  (username, subject))
        notes = [dict(r) for r in c.fetchall()]; conn.close(); return notes
    except Exception:
        return []


def get_note(note_id):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = c.fetchone(); conn.close(); return dict(row) if row else None
    except Exception:
        return None


def update_note(note_id, title, subject, content):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE notes SET title=?, subject=?, content=?, updated_at=? WHERE id=?",
                  (title, subject, content, datetime.now(), note_id))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def update_summary(note_id, summary):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE notes SET summary=? WHERE id=?", (summary, note_id))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def update_study_plan(note_id, study_plan):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE notes SET study_plan=? WHERE id=?", (study_plan, note_id))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def delete_note(note_id):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("DELETE FROM flashcards WHERE note_id = ?", (note_id,))
        c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def get_all_subjects(username):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT DISTINCT subject FROM notes WHERE username = ? ORDER BY subject", (username,))
        subjects = [r[0] for r in c.fetchall()]; conn.close(); return subjects
    except Exception:
        return []


def toggle_favorite(note_id):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE notes SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END WHERE id = ?", (note_id,))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


# ── Flashcard Decks ──────────────────────────────────────────

def create_deck(username, name, description="", note_id=None):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO flashcard_decks (username, name, description, note_id) VALUES (?,?,?,?)",
                  (username, name, description, note_id))
        did = c.lastrowid; conn.commit(); conn.close(); return did
    except Exception:
        return None


def get_decks(username):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("""SELECT d.*, (SELECT COUNT(*) FROM flashcards WHERE deck_id = d.id) as card_count
                     FROM flashcard_decks d WHERE d.username = ? ORDER BY d.created_at DESC""", (username,))
        decks = [dict(r) for r in c.fetchall()]; conn.close(); return decks
    except Exception:
        return []


def get_deck(deck_id):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT * FROM flashcard_decks WHERE id = ?", (deck_id,))
        row = c.fetchone(); conn.close(); return dict(row) if row else None
    except Exception:
        return None


def delete_deck(deck_id):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("DELETE FROM flashcards WHERE deck_id = ?", (deck_id,))
        c.execute("DELETE FROM flashcard_decks WHERE id = ?", (deck_id,))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def rename_deck(deck_id, new_name):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE flashcard_decks SET name = ? WHERE id = ?", (new_name, deck_id))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


# ── Flashcards ───────────────────────────────────────────────

def save_flashcards(note_id, flashcards_list, deck_id=None):
    try:
        conn = get_connection(); c = conn.cursor()
        for card in flashcards_list:
            c.execute("INSERT INTO flashcards (note_id, deck_id, front, back) VALUES (?,?,?,?)",
                      (note_id, deck_id, card["front"], card["back"]))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def get_flashcards(note_id=None, deck_id=None):
    try:
        conn = get_connection(); c = conn.cursor()
        if deck_id:
            c.execute("SELECT * FROM flashcards WHERE deck_id = ?", (deck_id,))
        else:
            c.execute("SELECT * FROM flashcards WHERE note_id = ?", (note_id,))
        cards = [dict(r) for r in c.fetchall()]; conn.close(); return cards
    except Exception:
        return []


def delete_flashcards(note_id=None, deck_id=None):
    try:
        conn = get_connection(); c = conn.cursor()
        if deck_id:
            c.execute("DELETE FROM flashcards WHERE deck_id = ?", (deck_id,))
        else:
            c.execute("DELETE FROM flashcards WHERE note_id = ?", (note_id,))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def update_flashcard_score(flashcard_id, correct, difficulty=None):
    try:
        conn = get_connection(); c = conn.cursor()
        if correct:
            c.execute("UPDATE flashcards SET times_correct = times_correct + 1 WHERE id = ?", (flashcard_id,))
        else:
            c.execute("UPDATE flashcards SET times_wrong = times_wrong + 1 WHERE id = ?", (flashcard_id,))
        if difficulty:
            c.execute("UPDATE flashcards SET difficulty = ? WHERE id = ?", (difficulty, flashcard_id))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


# ── Quiz Results ─────────────────────────────────────────────

def save_quiz_result(username, note_id, subject, score, total, difficulty="Medium"):
    try:
        pct = (score / total) * 100 if total > 0 else 0
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO quiz_results (username, note_id, subject, score, total_questions, percentage, difficulty) VALUES (?,?,?,?,?,?,?)",
                  (username, note_id, subject, score, total, pct, difficulty))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def get_all_quiz_results(username):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("""SELECT qr.*, n.title as note_title FROM quiz_results qr
                     LEFT JOIN notes n ON qr.note_id = n.id WHERE qr.username = ? ORDER BY qr.taken_at DESC""", (username,))
        results = [dict(r) for r in c.fetchall()]; conn.close(); return results
    except Exception:
        return []


# ── Stats ────────────────────────────────────────────────────

def get_stats(username):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM notes WHERE username = ?", (username,))
        total_notes = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT subject) FROM notes WHERE username = ?", (username,))
        total_subjects = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM flashcards f JOIN notes n ON f.note_id = n.id WHERE n.username = ?", (username,))
        total_flashcards = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM quiz_results WHERE username = ?", (username,))
        total_quizzes = c.fetchone()[0]
        c.execute("SELECT AVG(percentage) FROM quiz_results WHERE username = ?", (username,))
        avg_score = c.fetchone()[0] or 0
        c.execute("SELECT MAX(percentage) FROM quiz_results WHERE username = ?", (username,))
        best_score = c.fetchone()[0] or 0
        c.execute("SELECT subject, COUNT(*) as cnt FROM notes WHERE username = ? GROUP BY subject ORDER BY cnt DESC LIMIT 1", (username,))
        fav_row = c.fetchone()
        fav_subject = fav_row[0] if fav_row else "N/A"
        conn.close()
        return {"total_notes": total_notes, "total_subjects": total_subjects, "total_flashcards": total_flashcards,
                "total_quizzes": total_quizzes, "avg_score": round(avg_score, 1), "best_score": round(best_score, 1),
                "favorite_subject": fav_subject}
    except Exception:
        return {"total_notes": 0, "total_subjects": 0, "total_flashcards": 0, "total_quizzes": 0,
                "avg_score": 0, "best_score": 0, "favorite_subject": "N/A"}


# ── Study Streak ─────────────────────────────────────────────

def record_study_day(username):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO study_streak (username, study_date) VALUES (?, ?)", (username, date.today().isoformat()))
        conn.commit(); conn.close(); return True
    except Exception:
        return False


def get_streak_data(username):
    try:
        from datetime import timedelta
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT study_date FROM study_streak WHERE username = ? ORDER BY study_date DESC", (username,))
        studied = set(r[0] for r in c.fetchall()); conn.close()
        today = date.today()
        streak = 0
        check = today
        while check.isoformat() in studied:
            streak += 1
            check = check - timedelta(days=1)
        days = []
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            days.append({"date": d, "studied": d in studied})
        return {"streak": min(streak, 7), "days": days}
    except Exception:
        from datetime import timedelta
        today = date.today()
        return {"streak": 0, "days": [{"date": (today - timedelta(days=i)).isoformat(), "studied": False} for i in range(6, -1, -1)]}
