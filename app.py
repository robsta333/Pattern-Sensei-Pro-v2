import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import time
import pandas as pd
from datetime import datetime, timedelta


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
HIGHLIGHT_COLOR = "#ffd84d"   # Softer gold highlight


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
if "show_examples" not in st.session_state:
    st.session_state.show_examples = False


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
#          YOUR BASE CANDLE GENERATOR (PANDAS)
# ================================================================
def generate_base_candles(n=20):
    """Realistic volatility, trend drift, clean OHLC."""
    np.random.seed(int(time.time()) + random.randint(0, 999))

    start = random.uniform(80, 120)
    vol = random.uniform(0.008, 0.025)

    prices = [start]
    for _ in range(n - 1):
        drift = random.uniform(-vol, vol) * start
        prices.append(prices[-1] + drift)

    df = pd.DataFrame()
    df["open"] = prices
    df["close"] = [o + random.uniform(-vol, vol) * 10 for o in df["open"]]
    df["high"] = df[["open", "close"]].max(axis=1) + np.random.uniform(0.1, 0.5, n)
    df["low"] = df[["open", "close"]].min(axis=1) - np.random.uniform(0.1, 0.5, n)
    df["volume"] = np.random.randint(200000, 800000, n)
    df["date"] = [datetime.now() - timedelta(minutes=5 * i) for i in range(n)][::-1]

    df["high"] = df[["open", "close", "high"]].max(axis=1)
    df["low"] = df[["open", "close", "low"]].min(axis=1)

    return df


# ================================================================
#     PERFECT MERGED PATTERN GENERATOR (SAFE + ACCURATE)
# ================================================================
def generate_pattern_df(pattern_type):
    """Creates realistic + accurate patterns using a DataFrame."""
    df = generate_base_candles(20)

    idx = -2          # pattern candle index
    prev_idx = idx - 1

    # Baseline body size and level
    body = random.uniform(0.35, 0.85)
    base = df.iloc[idx]["open"]

    # ---------------------------------------------------------
    # HELPER FUNCTIONS
    # ---------------------------------------------------------
    def enforce_ohlc_safe(row):
        """Ensure high >= open/close and low <= open/close."""
        row["high"] = max(row["open"], row["close"], row["high"])
        row["low"] = min(row["open"], row["close"], row["low"])
        return row

    def safe_adjust(condition, adjust_fn):
        """If strict-rule check fails, adjust instead of asserting."""
        if not condition():
            adjust_fn()

    # ---------------------------------------------------------
    # PATTERN LOGIC
    # ---------------------------------------------------------

    # ────────────────────────────────
    # HAMMER
    # ────────────────────────────────
    if pattern_type == "Hammer":
        open_p = base
        close_p = base + body
        high_p = max(open_p, close_p) + body * 0.08       # <10% upper wick
        low_p = min(open_p, close_p) - body * 3           # long lower wick

        df.at[df.index[idx], "open"] = open_p
        df.at[df.index[idx], "close"] = close_p
        df.at[df.index[idx], "high"] = high_p
        df.at[df.index[idx], "low"] = low_p

        # SAFETY: ensure upper wick really is small
        def hammer_condition():
            return (high_p - close_p) < body * 0.1

        def hammer_adjust():
            df.at[df.index[idx], "high"] = close_p + body * 0.05

        safe_adjust(hammer_condition, hammer_adjust)

    # ────────────────────────────────
    # SHOOTING STAR
    # ────────────────────────────────
    elif pattern_type == "Shooting Star":
        open_p = base + body
        close_p = base
        high_p = max(open_p, close_p) + body * 3          # long upper wick
        low_p = min(open_p, close_p) - body * 0.08        # <10% lower wick

        df.at[df.index[idx], "open"] = open_p
        df.at[df.index[idx], "close"] = close_p
        df.at[df.index[idx], "high"] = high_p
        df.at[df.index[idx], "low"] = low_p

        def ss_condition():
            return (open_p - low_p) < body * 0.1

        def ss_adjust():
            df.at[df.index[idx], "low"] = min(open_p, close_p) - body * 0.05

        safe_adjust(ss_condition, ss_adjust)

    # ────────────────────────────────
    # LONG-LEGGED DOJI
    # ────────────────────────────────
    elif pattern_type == "Long-legged Doji":
        open_p = base
        close_p = base + random.uniform(-0.015, 0.015)     # near-equal
        high_p = base + body * 2.5
        low_p = base - body * 2.5

        df.at[df.index[idx], "open"] = open_p
        df.at[df.index[idx], "close"] = close_p
        df.at[df.index[idx], "high"] = high_p
        df.at[df.index[idx], "low"] = low_p

        rng = high_p - low_p

        def doji_condition():
            return abs(open_p - close_p) <= rng * 0.02

        def doji_adjust():
            df.at[df.index[idx], "close"] = open_p + random.uniform(
                -rng * 0.015, rng * 0.015
            )

        safe_adjust(doji_condition, doji_adjust)

    # ────────────────────────────────
    # BULLISH ENGULFING
    # ────────────────────────────────
    elif pattern_type == "Bullish Engulfing":
        # Previous red
        df.at[df.index[prev_idx], "open"] = base + body * 0.3
        df.at[df.index[prev_idx], "close"] = base - body * 0.3
        df.at[df.index[prev_idx], "high"] = max(
            df.iloc[prev_idx]["open"], df.iloc[prev_idx]["close"]
        ) + body * 0.1
        df.at[df.index[prev_idx], "low"] = min(
            df.iloc[prev_idx]["open"], df.iloc[prev_idx]["close"]
        ) - body * 0.1

        # Current BIG green
        df.at[df.index[idx], "open"] = base - body * 0.6
        df.at[df.index[idx], "close"] = base + body * 1.4
        df.at[df.index[idx], "high"] = base + body * 1.5
        df.at[df.index[idx], "low"] = base - body * 0.7

    # ────────────────────────────────
    # BEARISH ENGULFING
    # ────────────────────────────────
    elif pattern_type == "Bearish Engulfing":
        # Previous green
        df.at[df.index[prev_idx], "open"] = base - body * 0.3
        df.at[df.index[prev_idx], "close"] = base + body * 0.3
        df.at[df.index[prev_idx], "high"] = base + body * 0.4
        df.at[df.index[prev_idx], "low"] = base - body * 0.4

        # Current BIG red
        df.at[df.index[idx], "open"] = base + body * 0.6
        df.at[df.index[idx], "close"] = base - body * 1.4
        df.at[df.index[idx], "high"] = base + body * 0.7
        df.at[df.index[idx], "low"] = base - body * 1.5

    # Final OHLC enforcement
    df.iloc[idx] = enforce_ohlc_safe(df.iloc[idx])
    df.iloc[prev_idx] = enforce_ohlc_safe(df.iloc[prev_idx])

    return df, pattern_type, idx, prev_idx


def generate_pattern_candle(pattern_name: str):
    """
    Wrapper: uses your pandas-based generator and returns a simple dict
    with open, close, high, low for the pattern candle.
    """
    df, pattern_type, idx, prev_idx = generate_pattern_df(pattern_name)
    row = df.iloc[idx]
    return {
        "open": float(row["open"]),
        "close": float(row["close"]),
        "high": float(row["high"]),
        "low": float(row["low"])
    }


# ================================================================
#       PATTERN SET DEFINITIONS + HYBRID UNLOCK LOGIC
# ================================================================
PATTERNS_A = [
    "Hammer",
    "Shooting Star",
    "Doji",
    "Long-legged Doji",
    "Bullish Engulfing",
    "Bearish Engulfing",
]

PATTERNS_B = [
    "Morning Star",
    "Evening Star",
    "Inverted Hammer",
    "Gravestone Doji",
]

PATTERNS_C = [
    "Harami",
    "Dark Cloud Cover",
    "Piercing Line",
    "Three White Soldiers",
    "Three Black Crows",
]


def get_active_patterns():
    """Return patterns available in the current set, considering unlocks."""
    mode = st.session_state.mode

    if mode == "Set A":
        return PATTERNS_A

    if mode == "Set B":
        if st.session_state.unlock_b or st.session_state.dev_override:
            return PATTERNS_A + PATTERNS_B
        st.warning("⚠️ Set B locked — score 70%+ in Set A.")
        st.session_state.mode = "Set A"
        return PATTERNS_A

    if mode == "Set C":
        if st.session_state.unlock_c or st.session_state.dev_override:
            return PATTERNS_A + PATTERNS_B + PATTERNS_C
        st.warning("⚠️ Set C locked — score 70%+ in Set B.")
        st.session_state.mode = "Set B" if st.session_state.unlock_b else "Set A"
        return PATTERNS_A


def pick_pattern():
    return random.choice(get_active_patterns())


# ================================================================
#                   MATPLOTLIB CHART RENDERING
# ================================================================
def draw_candle(ax, idx, candle):
    """Draw a single TradingView-style candle."""
    o, c, h, l = candle["open"], candle["close"], candle["high"], candle["low"]
    color = GREEN if c >= o else RED

    # Wick
    ax.vlines(idx, l, h, color=color, linewidth=2)

    # Body
    body_bottom = min(o, c)
    body_height = abs(c - o)
    body_height = body_height if body_height > 0 else 0.02

    rect = patches.Rectangle(
        (idx - 0.3, body_bottom),
        0.6,
        body_height,
        facecolor=color,
        edgecolor=color,
        linewidth=1.2,
    )
    ax.add_patch(rect)


def render_chart_with_highlight(pattern_candle, pattern_index, num_candles):
    """
    Renders a mini-chart with the highlight box.
    num_candles is passed in from outside (fixes IndexError).
    """
    prices = generate_background_prices(num_candles)
    candles = []

    for i in range(num_candles):
        op = prices[i] + np.random.uniform(-1.2, 1.2)
        cl = prices[i] + np.random.uniform(-1.2, 1.2)
        hi = max(op, cl) + np.random.uniform(0.2, 1.3)
        lo = min(op, cl) - np.random.uniform(0.2, 1.3)

        candles.append({"open": op, "close": cl, "high": hi, "low": lo})

    # Insert the pattern candle at a safe index
    candles[pattern_index] = pattern_candle

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # Draw all candles
    for idx, cndl in enumerate(candles):
        draw_candle(ax, idx, cndl)

    # Highlight box
    pc = candles[pattern_index]
    highlight = patches.Rectangle(
        (pattern_index - 0.6, pc["low"] - 0.5),
        1.2,
        (pc["high"] - pc["low"]) + 1.0,
        linewidth=2.0,
        edgecolor=HIGHLIGHT_COLOR,
        facecolor="none",
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
    "Unlock all sets (developer mode)", value=st.session_state.dev_override
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Choose Pattern Set")

chosen_mode = st.sidebar.radio(
    "Select mode:",
    ["Set A", "Set B", "Set C"],
    index=["Set A", "Set B", "Set C"].index(st.session_state.mode),
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
    unsafe_allow_html=True,
)


# ================================================================
#                 MAIN GAME DISPLAY
# ================================================================
correct_pattern = pick_pattern()
pattern_candle = generate_pattern_candle(correct_pattern)

# SAFE number of candles and index
num_candles = random.randint(12, 16)
pattern_index = random.randint(1, num_candles - 2)

st.markdown("## 📊 CHART ACTION – Identify the highlighted pattern candle")

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
    st.markdown(
        """
    **Hammer:** Tiny body up top, long lower wick.  
    **Shooting Star:** Tiny body bottom, long upper wick.  
    **Doji / Long-Legged Doji:** Open ≈ close, long wicks.  
    **Bullish Engulfing:** Big green candle engulfs red.  
    **Bearish Engulfing:** Big red candle engulfs green.  
    """
    )


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

if st.session_state.show_examples:
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
