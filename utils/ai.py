import json
import re
import streamlit as st
from openai import OpenAI

MODEL = "minimax/minimax-m2.5"
BASE_URL = "https://openrouter.ai/api/v1"


def get_client():
    """Create OpenRouter client. Returns (client, error_string)."""
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key or api_key == "your-api-key-here":
        return None, (
            "No API key found. Add your OpenRouter API key to "
            "`.streamlit/secrets.toml`:\n\n"
            '```toml\nOPENROUTER_API_KEY = "sk-or-..."\n```'
        )

    client = OpenAI(base_url=BASE_URL, api_key=api_key)
    return client, None


def _extract_json(text):
    """Best-effort extraction of a JSON array from AI output."""
    text = text.strip()

    # 1. Try direct parse first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # 2. Try extracting from ```json ... ``` blocks
    blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)```", text)
    for block in blocks:
        try:
            parsed = json.loads(block.strip())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            continue

    # 3. Try finding the outermost [ ... ] array
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    return None


def _call_ai(system_prompt, user_content, error_label="AI"):
    """Central helper to call the model. Returns (response_text, error)."""
    client, err = get_client()
    if err:
        return None, err

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, f"{error_label} request failed: {e}"


# ── Summary ──────────────────────────────────────────────────

def summarize_notes(content):
    text, err = _call_ai(
        "You are a study assistant. Summarize the given study notes into clear, "
        "concise bullet points. Focus on key concepts, definitions, and important facts. "
        "Use simple language. Use bullet points with - prefix.",
        content,
        "Summary",
    )
    if err:
        return None, err
    return text, None


# ── Flashcards ───────────────────────────────────────────────

def generate_flashcards(content, count=10):
    system_prompt = (
        f"You are a study assistant. Generate exactly {count} flashcards from the given notes. "
        "Each flashcard should test one specific concept. "
        'Return ONLY a valid JSON array: [{"front": "question", "back": "answer"}]'
    )

    text, err = _call_ai(system_prompt, content, "Flashcard generation")
    if err:
        return None, err

    flashcards = _extract_json(text)
    if flashcards is None:
        return None, (
            f"Could not parse flashcards from the AI response. "
            f"Raw output:\n\n```\n{text[:500]}\n```"
        )

    valid = [c for c in flashcards if isinstance(c, dict) and "front" in c and "back" in c]
    if not valid:
        return None, "AI returned data but no valid flashcards were found (missing front/back keys)."

    return valid, None


# ── Quiz ─────────────────────────────────────────────────────

def generate_quiz(content, count=5, difficulty="Medium"):
    difficulty_instructions = {
        "Easy": "Generate simple recall and recognition questions. Use straightforward language. "
                "Questions should test basic facts and definitions directly stated in the notes.",
        "Medium": "Generate understanding and application questions. Require the student to "
                  "connect concepts and apply knowledge, not just recall facts.",
        "Hard": "Generate analysis and critical thinking questions. Require deep understanding, "
                "comparison of concepts, and evaluation. Include tricky distractors.",
    }
    diff_text = difficulty_instructions.get(difficulty, difficulty_instructions["Medium"])

    system_prompt = (
        f"You are a study assistant. Generate exactly {count} multiple choice questions from the notes. "
        f"Difficulty: {difficulty}. {diff_text} "
        "Each question must have exactly 4 options (A, B, C, D). "
        'Return ONLY a valid JSON array: [{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], '
        '"correct": "A", "explanation": "brief explanation"}]'
    )

    text, err = _call_ai(system_prompt, content, "Quiz generation")
    if err:
        return None, err

    questions = _extract_json(text)
    if questions is None:
        return None, (
            f"Could not parse quiz from the AI response. "
            f"Raw output:\n\n```\n{text[:500]}\n```"
        )

    required = ["question", "options", "correct", "explanation"]
    valid = [q for q in questions if isinstance(q, dict) and all(k in q for k in required)]
    if not valid:
        return None, "AI returned data but no valid questions were found (missing required keys)."

    return valid, None


# ── Explain ──────────────────────────────────────────────────

def explain_concept(text):
    result, err = _call_ai(
        "You are a friendly tutor. Explain this concept in very simple words "
        "that any student would understand. Use real-world examples. "
        "Keep it short - max 3 paragraphs.",
        text,
        "Explanation",
    )
    if err:
        return None, err
    return result, None


# ── Chat ─────────────────────────────────────────────────────

def chat_about_notes(notes_content, user_question, chat_history=None):
    client, err = get_client()
    if err:
        return None, err

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a study assistant. The student has these notes:\n\n{notes_content}\n\n"
                "Answer their question based on the notes. If the answer isn't in the notes, "
                "say so and provide a helpful answer anyway. Be concise."
            ),
        }
    ]
    if chat_history:
        for msg in chat_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_question})

    try:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        return response.choices[0].message.content, None
    except Exception as e:
        return None, f"Chat request failed: {e}"


# ── Study Plan ───────────────────────────────────────────────

def generate_study_plan(content):
    result, err = _call_ai(
        "You are a study planner. Based on the notes provided, create a structured "
        "study plan. Break it into numbered steps. For each step include:\n"
        "- What to study (topic name)\n"
        "- Why it matters (1 sentence)\n"
        "- Estimated time (e.g. 15 min)\n"
        "- A checkbox marker [ ]\n\n"
        "Order from foundational concepts first to advanced topics last. "
        "Keep it practical and actionable.",
        content,
        "Study plan",
    )
    if err:
        return None, err
    return result, None


# ── AI Notes Generator ───────────────────────────────────────

def generate_notes(subject, topic, difficulty, length):
    """Generate study notes on a topic. Returns (notes_markdown, error)."""

    length_instruction = {
        "Short": "Keep it concise - key points only, about 300-500 words.",
        "Medium": "Provide detailed notes covering the topic well, about 600-1000 words.",
        "Long": "Write comprehensive study notes with thorough coverage, about 1200-2000 words.",
    }

    if topic and topic.strip():
        topic_line = f"Focus specifically on: {topic}."
    else:
        topic_line = (
            "Pick a RANDOM and INTERESTING subtopic within this subject. "
            "Do NOT pick an obvious or generic topic. Be creative and choose something "
            "students would find useful and surprising."
        )

    length_text = length_instruction.get(length, length_instruction["Medium"])

    system_prompt = (
        f"You are a knowledgeable and engaging teacher creating study notes.\n\n"
        f"Subject: {subject}\n"
        f"{topic_line}\n"
        f"Difficulty: {difficulty}\n"
        f"Length: {length_text}\n\n"
        "Write notes in MARKDOWN format:\n"
        "# Title (specific and interesting, NOT generic)\n"
        "## Key Concepts\n"
        "- Define core ideas with **bold** for key terms\n"
        "## Detailed Explanation\n"
        "Thorough explanation with examples\n"
        "## Real-World Examples\n"
        "Concrete relatable examples\n"
        "## Important Facts\n"
        "- Key data, dates, numbers\n"
        "## Summary\n"
        "Main takeaways\n\n"
        "Make it educational, engaging, different from textbooks."
    )

    return _call_ai(system_prompt, f"Generate study notes for {subject}.", "Note generation")
