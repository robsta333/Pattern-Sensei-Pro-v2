import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import time


# ================================================================
#                 STREAMLIT PAGE CONFIG
# ================================================================
st.set_page_config(
    page_title="Pattern Sensei Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# TradingView-style colors
GREEN = "#26a69a"
RED = "#ef5350"
BG = "#0d1220"
GRID = "#1a1f2e"
HIGHLIGHT_COLOR = "#f7d400"


# ================================================================
#                 GLOBAL SESSION STATE
# ================================================================
if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "round" not in st.session_state:
    st.session_state.round = 1
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "mode" not in st.session_state:
    st.session_state.mode = "Set A"
if "unlock_b" not in st.session_state:
    st.session_state.unlock_b = False
if "unlock_c" not in st.session_state:
    st.session_state.unlock_c = False
if "dev_override" not in st.session_state:
    st.session_state.dev_override = False


def reset_game():
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.round = 1
    st.session_state.start_time = time.time()


# ================================================================
#          RANDOM WALK FOR BACKGROUND CANDLES
# ================================================================
def generate_background_prices(n=15):
    prices = [100]
    for _ in range(n - 1):
        prices.append(prices[-1] + np.random.normal(0, 1))
    return prices


# ================================================================
#              PATTERN GENERATORS (SET A)
# ================================================================
def make_hammer():
    body = random.uniform(0.2, 0.6)
    lower_wick = body * random.uniform(2.2, 3.5)
    upper_wick = body * random.uniform(0, 0.3)
    bullish = random.choice([True, False])

    if bullish:
        open_p = 100
        close_p = open_p + body
    else:
        close_p = 100
        open_p = close_p + body

    high = max(open_p, close_p) + upper_wick
    low = min(open_p, close_p) - lower_wick

    return {"name": "Hammer", "open": open_p, "close": close_p, "high": high, "low": low}


def make_shooting_star():
    body = random.uniform(0.2, 0.6)
    upper_wick = body * random.uniform(2.2, 3.5)
    lower_wick = body * random.uniform(0, 0.3)
    bullish = random.choice([True, False])

    if bullish:
        close_p = 100
        open_p = close_p - body
    else:
        open_p = 100
        close_p = open_p - body

    high = max(open_p, close_p) + upper_wick
    low = min(open_p, close_p) - lower_wick

    return {"name": "Shooting Star", "open": open_p, "close": close_p, "high": high, "low": low}


def make_doji():
    center = 100
    open_p = center + random.uniform(-0.05, 0.05)
    close_p = center + random.uniform(-0.05, 0.05)
    upper_wick = random.uniform(0.3, 1.2)
    lower_wick = random.uniform(0.3, 1.2)

    return {
        "name": "Doji",
        "open": open_p,
        "close": close_p,
        "high": max(open_p, close_p) + upper_wick,
        "low": min(open_p, close_p) - lower_wick
    }


def make_long_legged_doji():
    center = 100
    open_p = center + random.uniform(-0.05, 0.05)
    close_p = center + random.uniform(-0.05, 0.05)
    high = center + random.uniform(2.0, 3.5)
    low = center - random.uniform(2.0, 3.5)

    return {
        "name": "Long-legged Doji",
        "open": open_p,
        "close": close_p,
        "high": high,
        "low": low
    }


def make_bullish_engulfing():
    prev_open = 100
    prev_close = prev_open - random.uniform(0.3, 1.2)
    new_close = prev_open + random.uniform(0.5, 1.3)
    new_open = prev_close - random.uniform(0.1, 0.3)
    high = max(new_open, new_close) + random.uniform(0.2, 0.8)
    low = min(new_open, new_close) - random.uniform(0.2, 0.8)

    return {"name": "Bullish Engulfing", "open": new_open, "close": new_close, "high": high, "low": low}


def make_bearish_engulfing():
    prev_close = 100
    prev_open = prev_close + random.uniform(0.3, 1.2)
    new_close = prev_open - random.uniform(0.5, 1.3)
    new_open = prev_close + random.uniform(0.1, 0.3)
    high = max(new_open, new_close) + random.uniform(0.2, 0.8)
    low = min(new_open, new_close) - random.uniform(0.2, 0.8)

    return {"name": "Bearish Engulfing", "open": new_open, "close": new_close, "high": high, "low": low}


# ================================================================
#       PATTERN SET DEFINITIONS + HYBRID UNLOCK LOGIC
# ================================================================
PATTERNS_A = [
    "Hammer", "Shooting Star", "Doji",
    "Long-legged Doji", "Bullish Engulfing", "Bearish Engulfing"
]

PATTERNS_B = ["Morning Star", "Evening Star", "Inverted Hammer", "Gravestone Doji"]
PATTERNS_C = ["Harami", "Dark Cloud Cover", "Piercing Line", "Three White Soldiers", "Three Black Crows"]


def get_active_patterns():
    if st.session_state.mode == "Set A":
        return PATTERNS_A

    if st.session_state.mode == "Set B":
        if st.session_state.unlock_b or st.session_state.dev_override:
            return PATTERNS_A + PATTERNS_B
        st.warning("⚠️ Score 70% in Set A to unlock Set B.")
        st.session_state.mode = "Set A"
        return PATTERNS_A

    if st.session_state.mode == "Set C":
        if st.session_state.unlock_c or st.session_state.dev_override:
            return PATTERNS_A + PATTERNS_B + PATTERNS_C
        st.warning("⚠️ Score 70% in Set B to unlock Set C.")
        st.session_state.mode = "Set B" if st.session_state.unlock_b else "Set A"
        return PATTERNS_A


def pick_pattern():
    return random.choice(get_active_patterns())


def generate_pattern_candle(name):
    if name == "Hammer": return make_hammer()
    if name == "Shooting Star": return make_shooting_star()
    if name == "Doji": return make_doji()
    if name == "Long-legged Doji": return make_long_legged_doji()
    if name == "Bullish Engulfing": return make_bullish_engulfing()
    if name == "Bearish Engulfing": return make_bearish_engulfing()
    return make_doji()


# ================================================================
#                   MATPLOTLIB CHART RENDERING
# ================================================================
def draw_candle(ax, idx, candle):
    o, c, h, l = candle["open"], candle["close"], candle["high"], candle["low"]
    color = GREEN if c >= o else RED
    ax.vlines(idx, l, h, color=color, linewidth=2)
    body_bottom = min(o, c)
    body_height = abs(c - o)
    rect = patches.Rectangle((idx - 0.3, body_bottom), 0.6,
                             body_height if body_height > 0 else 0.02,
                             facecolor=color, edgecolor=color, linewidth=1.2)
    ax.add_patch(rect)


def render_chart_with_highlight(pattern_candle, pattern_index):
    num = random.randint(10, 15)
    prices = generate_background_prices(num)

    candles = []
    for i in range(num):
        op = prices[i] + np.random.uniform(-1.2, 1.2)
        cl = prices[i] + np.random.uniform(-1.2, 1.2)
        hi = max(op, cl) + np.random.uniform(0.2, 1.3)
        lo = min(op, cl) - np.random.uniform(0.2, 1.3)
        candles.append({"open": op, "close": cl, "high": hi, "low": lo})

    candles[pattern_index] = pattern_candle

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    for i, cndl in enumerate(candles):
        draw_candle(ax, i, cndl)

    pc = candles[pattern_index]
    highlight = patches.Rectangle(
        (pattern_index - 0.6, pc["low"] - 0.5),
        1.2,
        (pc["high"] - pc["low"]) + 1.0,
        linewidth=1.8,
        edgecolor=HIGHLIGHT_COLOR,
        facecolor="none"
    )
    ax.add_patch(highlight)

    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False, bottom=False)

    plt.tight_layout()
    return fig


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

if chosen_mode == "Set B" and not (st.session_state.unlock_b or st.session_state.dev_override):
    st.sidebar.warning("🔒 Locked — Score 70% in Set A")

if chosen_mode == "Set C" and not (st.session_state.unlock_c or st.session_state.dev_override):
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
pattern_index = random.randint(2, 12)

st.markdown("## 📊 CHART ACTION – Identify the highlighted pattern candle")
fig = render_chart_with_highlight(pattern_candle, pattern_index)
st.pyplot(fig)

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
