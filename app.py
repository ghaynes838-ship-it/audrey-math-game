import random
import operator
import math
import streamlit as st

# -----------------------------
# Difficulty settings (1–5)
# -----------------------------
LEVEL_SETTINGS = {
    1: {"min_n": 0,  "max_n": 10,  "ops": ["add", "sub"],                   "integer_division_only": True, "allow_negative_sub": False},
    2: {"min_n": 0,  "max_n": 20,  "ops": ["add", "sub"],                   "integer_division_only": True, "allow_negative_sub": False},
    3: {"min_n": 0,  "max_n": 50,  "ops": ["add", "sub", "mul"],            "integer_division_only": True, "allow_negative_sub": False},
    4: {"min_n": 0,  "max_n": 100, "ops": ["add", "sub", "mul", "div"],     "integer_division_only": True, "allow_negative_sub": False},
    5: {"min_n": 0,  "max_n": 200, "ops": ["add", "sub", "mul", "div"],     "integer_division_only": True, "allow_negative_sub": False},
}

OP_MAP = {
    "add": ("+", operator.add),
    "sub": ("-", operator.sub),
    "mul": ("×", operator.mul),
    "div": ("÷", operator.truediv),
}

LEVEL_HINTS = {
    1: "Tiny numbers (+, −)",
    2: "Bigger numbers (+, −)",
    3: "Adds ×",
    4: "Adds ÷ (whole answers)",
    5: "Hard mode (bigger × and ÷)",
}

# -----------------------------
# Helpers
# -----------------------------
def generate_question(level: int):
    s = LEVEL_SETTINGS[level]
    min_n, max_n = s["min_n"], s["max_n"]
    allowed_ops = s["ops"]
    integer_division_only = s["integer_division_only"]
    allow_negative_sub = s["allow_negative_sub"]

    op_key = random.choice(allowed_ops)
    op_symbol, op_func = OP_MAP[op_key]

    if op_key == "div" and integer_division_only:
        # Whole-number division: dividend ÷ divisor = quotient
        divisor_min = 1
        divisor_max = max(2, min(max_n, 20 if level <= 4 else 30))
        divisor = random.randint(divisor_min, divisor_max)

        quotient_max = max(5, min(max_n, 20 if level <= 4 else 40))
        quotient = random.randint(min_n, quotient_max)

        dividend = divisor * quotient
        x, y = dividend, divisor
        correct = quotient
    else:
        x = random.randint(min_n, max_n)
        y = random.randint(min_n, max_n)

        if op_key == "sub" and not allow_negative_sub and y > x:
            x, y = y, x

        if op_key == "div" and y == 0:
            y = 1

        result = op_func(x, y)
        if op_key == "div" and not integer_division_only:
            correct = round(result, 2)
        else:
            correct = int(result)

    return {
        "x": x,
        "y": y,
        "op_key": op_key,
        "op_symbol": op_symbol,
        "correct": correct,
        "integer_division_only": integer_division_only,
    }

def reset_game(level: int):
    st.session_state.question = generate_question(level)
    st.session_state.feedback = "Type your answer, then tap Check."
    st.session_state.last_checked = False
    st.session_state.answer_input = ""

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="Audrey's Math Game", page_icon="🧮", layout="centered")

st.title("Audrey's Math Game 🧮")
st.caption("A simple, touch-friendly maths game for kids (Levels 1–5).")

# Initialise session state
if "level" not in st.session_state:
    st.session_state.level = 1
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "total_count" not in st.session_state:
    st.session_state.total_count = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = "Type your answer, then tap Check."
if "last_checked" not in st.session_state:
    st.session_state.last_checked = False
if "answer_input" not in st.session_state:
    st.session_state.answer_input = ""
if "question" not in st.session_state:
    st.session_state.question = generate_question(st.session_state.level)

# Difficulty selector
st.subheader("Choose Level")
level = st.radio(
    label="",
    options=[1, 2, 3, 4, 5],
    index=st.session_state.level - 1,
    horizontal=True
)

if level != st.session_state.level:
    st.session_state.level = level
    st.session_state.correct_count = 0
    st.session_state.total_count = 0
    reset_game(level)

st.info(LEVEL_HINTS[st.session_state.level])

# Current question
q = st.session_state.question

# Big equation display (touch-friendly)
st.markdown(
    f"""
    <div style="font-size:48px; font-weight:700; text-align:center; padding: 12px 0;">
        {q['x']} {q['op_symbol']} {q['y']} = ?
    </div>
    """,
    unsafe_allow_html=True,
)

# Input + buttons
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    answer = st.text_input(
        "Your answer",
        value=st.session_state.answer_input,
        key="answer_box",
        label_visibility="collapsed",
        placeholder="Type answer here",
    )

with col2:
    check = st.button("✅ Check", use_container_width=True)

with col3:
    nxt = st.button("➡️ Next", use_container_width=True)

# Store current input
st.session_state.answer_input = answer

# Actions
if nxt:
    reset_game(st.session_state.level)
    st.rerun()

if check:
    raw = (st.session_state.answer_input or "").strip()
    if raw == "":
        st.session_state.feedback = "Please type an answer first."
        st.session_state.last_checked = False
    else:
        try:
            user_answer = int(raw) if q["integer_division_only"] else float(raw)
        except ValueError:
            st.session_state.feedback = "Please enter numbers only."
            st.session_state.last_checked = False
        else:
            st.session_state.total_count += 1

            if q["integer_division_only"]:
                is_correct = (user_answer == q["correct"])
            else:
                is_correct = math.isclose(float(user_answer), float(q["correct"]), rel_tol=0.0, abs_tol=0.01)

            if is_correct:
                st.session_state.correct_count += 1
                st.session_state.feedback = "Correct! Great job. Tap Next for another one."
            else:
                st.session_state.feedback = f"Not quite. The correct answer is {q['correct']}. Tap Next to try another."

            st.session_state.last_checked = True

# Feedback + score
if st.session_state.last_checked and st.session_state.feedback.startswith("Correct"):
    st.success(st.session_state.feedback)
elif st.session_state.last_checked:
    st.warning(st.session_state.feedback)
else:
    st.write(st.session_state.feedback)

st.markdown(
    f"""
    <div style="font-size:20px; font-weight:700; text-align:center; padding-top: 6px;">
        Score: {st.session_state.correct_count}/{st.session_state.total_count}
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()
st.caption("Tip: On iPad, open the link in Safari → Share → Add to Home Screen for an app-like icon.")
