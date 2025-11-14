import streamlit as st
import random
import time
import matplotlib.pyplot as plt


# ================================================================
#          SESSION STATE INITIALIZATION
# ================================================================
def init_state():
    defaults = {
        "dev_override": False,
        "unlock_b": False,
        "unlock_c": False,
        "mode": "Set A",
        "start_time": time.time(),
        "score": 0,
        "streak": 0,
        "round": 0,
        "show_examples": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ================================================================
#          SIMPLE PATTERN PICKER
# ================================================================
SET_A = ["Hammer", "Shooting Star", "Doji",
         "Long-legged Doji", "Bullish Engulfing", "Bearish Engulfing"]

SET_B = ["Morning Star", "Evening Star", "Harami", "Marubozu"]

SET_C = ["Three White Soldiers", "Three Black Crows", "Piercing Line"]


def get_active_patterns():
    if st.session_state.mode == "Set A":
        return SET_A
    if st.session_state.mode == "Set B":
        return SET_B
    return SET_C


def pick_pattern():
    return random.choice(get_active_patterns())


# ================================================================
#        SIMPLE RANDOM CANDLE GENERATOR (NO UTILS)
# ================================================================
def generate_pattern_candle(pattern):
    """Return a synthetic candle structure for Matplotlib display."""
    # For C mode you don't care — so we just return random candles
    candles = []
    for _ in range(20):
        open_ = random.uniform(90, 110)
        close = open_ + random.uniform(-5, 5)
        high = max(open_, close) + random.uniform(0, 3)
        low = min(open_, close) - random.uniform(0, 3)
        candles.append((open_, high, low, close))
    return candles


# ================================================================
#                BASIC MATPLOTLIB RENDERER
# ================================================================
def render_chart_with_highlight(candles, highlight_idx):
    fig, ax = plt.subplots(figsize=(8, 4))

    for i, (open_, high, low, close) in enumerate(candles):
        is_highlight = (i == highlight_idx)

        # Normal color for the candle body
        base_color = "green" if close >= open_ else "red"

        # Highlight styling
        if is_highlight:
            wick_color = "yellow"
            body_edge = "yellow"
            body_alpha = 0.9
            line_width = 2.5

            # Soft band behind the highlighted candle
            ax.axvspan(i - 0.5, i + 0.5, color="yellow", alpha=0.12)
        else:
            wick_color = base_color
            body_edge = base_color
            body_alpha = 0.5
            line_width = 1.2

        # Wick
        ax.plot([i, i], [low, high],
                color=wick_color,
                linewidth=line_width,
                alpha=body_alpha)

        # Body
        ax.add_patch(plt.Rectangle(
            (i - 0.3, min(open_, close)),
            0.6,
            abs(close - open_),
            facecolor=base_color,
            edgecolor=body_edge,
            linewidth=line_width,
            alpha=body_alpha
        ))

    ax.set_xlim(-1, len(candles))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Identify the Highlighted Candle", color="white")
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#111111")
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

if chosen_mode == "Set B" and not (
    st.session_state.unlock_b or st.session_state.dev_override
):
    st.sidebar.warning("🔒 Locked — Score 70% in Set A")

if chosen_mode == "Set C" and not (
    st.session_state.unlock_c or st.session_state.dev_override
):
    st.sidebar.warning("🔒 Locked — Score 70% in Set B")


# ================================================================
#               TOP TIMER DISPLAY
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
#               MAIN GAME DISPLAY
# ================================================================
correct_pattern = pick_pattern()
candles = generate_pattern_candle(correct_pattern)
pattern_index = random.randint(2, len(candles) - 3)

st.markdown("## 📊 CHART ACTION – Identify the highlighted pattern candle")

fig = render_chart_with_highlight(candles, pattern_index)
st.pyplot(fig)


# ================================================================
#                 ANSWER BUTTONS
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

    st.rerun()



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
    st.rerun()


# ================================================================
#                     RESET GAME
# ================================================================
st.markdown("### 🔁 Reset Game")
if st.button("Start Over"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

