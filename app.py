import streamlit as st
import time
import random

# --- Import your helper functions ---
from utils.patterns import pick_pattern, generate_pattern_candle, get_active_patterns
from utils.charting import render_chart_with_highlight
from utils.state import reset_game

# --- Initialize session state ---
if "dev_override" not in st.session_state:
    st.session_state.dev_override = False
if "unlock_b" not in st.session_state:
    st.session_state.unlock_b = False
if "unlock_c" not in st.session_state:
    st.session_state.unlock_c = False
if "mode" not in st.session_state:
    st.session_state.mode = "Set A"
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "round" not in st.session_state:
    st.session_state.round = 0
# ================================================================
#                   SIDEBAR UI
# ================================================================
st.sidebar.markdown("## 📘 PATTERN CHEAT SHEET")
st.sidebar.markdown("Study these perfect examples before trading!")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠 Developer Settings")
st.session_state.dev_override = st.sidebar.checkbox(
    "Unlock all sets (developer mode)",
    value=st.session_state.dev_override
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Choose Pattern Set")

chosen_mode = st.sidebar.radio(
    "Select mode:",
    ["Set A", "Set B", "Set C"],
    index=["Set A", "Set B", "Set C"].index(st.session_state.mode)
)

st.session_state.mode = chosen_mode

if chosen_mode == "Set B" and not (
    st.session_state.unlock_b or st.session_state.dev_override
):
    st.sidebar.warning("🔒 Locked — Score 70% in Set A")

if chosen_mode == "Set C" and not (
    st.session_state.unlock_c or st.session_state.dev_override
):
    st.sidebar.warning("🔒 Locked — Score 70% in Set B")


# ================================================================
#                 TOP TIMER DISPLAY
# ================================================================
elapsed = time.time() - st.session_state.start_time
st.markdown(
    f"""
    <h1 style='text-align:center; color:#ffcccc; font-size:64px;'>
        {elapsed:.1f}s
    </h1>
    """,
    unsafe_allow_html=True
)


# ================================================================
#                 MAIN GAME DISPLAY
# ================================================================
correct_pattern = pick_pattern()
pattern_candle = generate_pattern_candle(correct_pattern)

# FIXED RANGE + VALID INDEX
num_candles = random.randint(10, 15)
pattern_index = random.randint(1, num_candles - 2)

st.markdown("## 📊 CHART ACTION – Identify the highlighted pattern candle")

# FIXED SIGNATURE
fig = render_chart_with_highlight(pattern_candle, pattern_index, num_candles)
st.pyplot(fig)


# ================================================================
#                    ANSWER BUTTONS
# ================================================================
st.markdown("## 🎯 IDENTIFY THE PATTERN CANDLE")

active_patterns = get_active_patterns()
cols = st.columns(3)
clicked = None

for i, pat in enumerate(active_patterns):
    if cols[i % 3].button(pat):
        clicked = pat

if clicked:
    if clicked == correct_pattern:
        st.success(f"🎉 Correct! It was **{correct_pattern}**.")
        st.session_state.score += 1
        st.session_state.streak += 1
    else:
        st.error(f"❌ Incorrect — it was **{correct_pattern}**.")
        st.session_state.streak = 0

    st.session_state.round += 1
    st.session_state.start_time = time.time()

    # Unlock Set B
    if not st.session_state.unlock_b:
        if st.session_state.score >= max(5, int(st.session_state.round * 0.7)):
            st.session_state.unlock_b = True
            st.sidebar.success("🎉 Set B unlocked!")

    # Unlock Set C
    if st.session_state.unlock_b and not st.session_state.unlock_c:
        if st.session_state.score >= max(10, int(st.session_state.round * 0.7)):
            st.session_state.unlock_c = True
            st.sidebar.success("🔥 Set C unlocked!")

    st.experimental_rerun()


# ================================================================
#                       HINTS
# ================================================================
with st.expander("💡 Need a hint?"):
    st.markdown("""
    **Hammer:** Tiny body up top, long lower wick.  
    **Shooting Star:** Tiny body bottom, long upper wick.  
    **Doji:** Open ≈ close.  
    **Long-legged Doji:** Very long wicks, tiny body.  
    **Bullish Engulfing:** Big green candle engulfs red.  
    **Bearish Engulfing:** Big red candle engulfs green.  
    """)


# ================================================================
#                SCORE + STREAK DISPLAY
# ================================================================
st.markdown("---")
st.markdown(f"### ⭐ Score: `{st.session_state.score}`")
st.markdown(f"### 🔥 Streak: `{st.session_state.streak}`")
st.markdown("---")


# ================================================================
#            PERFECT EXAMPLES GALLERY
# ================================================================
st.sidebar.markdown("### 📷 Perfect Examples")
if st.sidebar.button("CLICK FOR PERFECT EXAMPLES"):
    st.session_state.show_examples = True

if st.session_state.get("show_examples", False):
    st.markdown("## 📚 Perfect Textbook Examples")
    st.info("Set A patterns shown below.")

    cols = st.columns(3)
    cols[0].markdown("### Hammer")
    cols[1].markdown("### Shooting Star")
    cols[2].markdown("### Doji")

    cols = st.columns(3)
    cols[0].markdown("### Long-legged Doji")
    cols[1].markdown("### Bullish Engulfing")
    cols[2].markdown("### Bearish Engulfing")

    if st.button("Close Gallery"):
        st.session_state.show_examples = False
        st.experimental_rerun()


# ================================================================
#                     RESET GAME
# ================================================================
st.markdown("### 🔁 Reset Game")
if st.button("Start Over"):
    reset_game()
    st.experimental_rerun()
