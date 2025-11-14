import streamlit as st
import random
import matplotlib.pyplot as plt


# -----------------------------------------
# PATTERNS LIST
# -----------------------------------------
PATTERNS = [
    "Hammer",
    "Shooting Star",
    "Doji",
    "Bullish Engulfing",
    "Bearish Engulfing"
]


# -----------------------------------------
# RANDOM CANDLE GENERATOR (simple)
# -----------------------------------------
def generate_candles(n=20):
    candles = []
    for _ in range(n):
        o = random.uniform(90, 110)
        c = o + random.uniform(-5, 5)
        high = max(o, c) + random.uniform(0, 5)
        low = min(o, c) - random.uniform(0, 5)
        candles.append((o, c, high, low))
    return candles


# -----------------------------------------
# PLOT WITH A HIGHLIGHTED CANDLE
# -----------------------------------------
def plot_candles(candles, highlight_index):
    fig, ax = plt.subplots(figsize=(10,4))

    for i, (o, c, h, l) in enumerate(candles):
        color = "green" if c > o else "red"
        ax.plot([i, i], [l, h], color=color)
        ax.plot([i, i], [o, c], color=color, linewidth=6)

        if i == highlight_index:
            ax.axvspan(i-0.4, i+0.4, color="yellow", alpha=0.3)

    ax.set_xlim(-1, len(candles))
    ax.set_title("Identify the highlighted candle")
    return fig


# -----------------------------------------
# INIT SESSION STATE
# -----------------------------------------
def new_round():
    st.session_state.correct_pattern = random.choice(PATTERNS)
    st.session_state.candles = generate_candles()
    st.session_state.highlight = random.randint(3, 16)

if "correct_pattern" not in st.session_state:
    new_round()


# -----------------------------------------
# UI
# -----------------------------------------
st.title("📊 Simple Candle Pattern Trainer")
st.write("Guess the pattern of the highlighted candle below:")

# ALWAYS load candles BEFORE rendering chart
candles = st.session_state.candles
highlight = st.session_state.highlight

# Draw chart
fig = plot_candles(candles, highlight)
st.pyplot(fig)

st.write("---")
st.write("### Choose the pattern:")

cols = st.columns(3)
clicked = None

for i, pat in enumerate(PATTERNS):
    if cols[i % 3].button(pat):
        clicked = pat


# -----------------------------------------
# SHOW RESULT AND WAIT
# -----------------------------------------
if clicked:
    if clicked == st.session_state.correct_pattern:
        st.success(f"🎉 Correct! It was **{st.session_state.correct_pattern}**.")
    else:
        st.error(f"❌ Incorrect — it was **{st.session_state.correct_pattern}**.")

    st.write("")
    st.write("### Ready for the next one?")
    
    if st.button("Next Round"):
        new_round()
        st.rerun()
