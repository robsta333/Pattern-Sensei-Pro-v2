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
        "show_examples": False,
        "last_feedback": None,
        "feedback_time": 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# ================================================================
#          PATTERN SETS DEFINITIONS
# ================================================================
SET_A = ["Hammer", "Shooting Star", "Doji", "Long-legged Doji", "Bullish Engulfing", "Bearish Engulfing"]
SET_B = ["Morning Star", "Evening Star", "Harami", "Marubozu"]
SET_C = ["Three White Soldiers", "Three Black Crows", "Piercing Line", "Dark Cloud Cover"]

# ================================================================
#        REALISTIC PATTERN CANDLE GENERATOR
# ================================================================
def generate_random_candle(prev_close=None):
    """Generate a single random candle"""
    if prev_close is None:
        open_ = random.uniform(95, 105)
    else:
        open_ = prev_close
        
    close = open_ + random.uniform(-3, 3)
    high = max(open_, close) + random.uniform(0, 2)
    low = min(open_, close) - random.uniform(0, 2)
    return (open_, high, low, close)

def generate_context_candles(count, start_price=100):
    """Generate random candles for context"""
    candles = []
    prev_close = start_price
    for _ in range(count):
        candle = generate_random_candle(prev_close)
        candles.append(candle)
        prev_close = candle[3]  # close price
    return candles

def generate_pattern_candles(pattern):
    """Generate candles with the actual pattern embedded"""
    # Generate context before pattern
    candles = generate_context_candles(8, 100)
    pattern_start = len(candles)
    
    if pattern == "Hammer":
        body = random.uniform(95, 105)
        open_price = body
        close_price = body + random.uniform(-0.5, 0.5)
        low = min(open_price, close_price) - random.uniform(5, 8)
        high = max(open_price, close_price) + random.uniform(0, 0.5)
        candles.append((open_price, high, low, close_price))
        highlight_indices = [pattern_start]
        
    elif pattern == "Shooting Star":
        body = random.uniform(95, 105)
        open_price = body
        close_price = body + random.uniform(-0.5, 0.5)
        high = max(open_price, close_price) + random.uniform(5, 8)
        low = min(open_price, close_price) - random.uniform(0, 0.5)
        candles.append((open_price, high, low, close_price))
        highlight_indices = [pattern_start]
        
    elif pattern == "Doji":
        body = random.uniform(95, 105)
        open_price = body
        close_price = body + random.uniform(-0.1, 0.1)
        high = max(open_price, close_price) + random.uniform(1, 3)
        low = min(open_price, close_price) - random.uniform(1, 3)
        candles.append((open_price, high, low, close_price))
        highlight_indices = [pattern_start]
        
    elif pattern == "Long-legged Doji":
        body = random.uniform(95, 105)
        open_price = body
        close_price = body + random.uniform(-0.1, 0.1)
        high = max(open_price, close_price) + random.uniform(4, 6)
        low = min(open_price, close_price) - random.uniform(4, 6)
        candles.append((open_price, high, low, close_price))
        highlight_indices = [pattern_start]
        
    elif pattern == "Bullish Engulfing":
        # First a small red candle
        open1 = random.uniform(98, 102)
        close1 = open1 - random.uniform(1, 2)
        high1 = max(open1, close1) + random.uniform(0, 0.5)
        low1 = min(open1, close1) - random.uniform(0, 0.5)
        candles.append((open1, high1, low1, close1))
        
        # Then a big green candle that engulfs it
        open2 = close1
        close2 = open1 + random.uniform(1, 2)
        high2 = max(open2, close2) + random.uniform(0, 0.5)
        low2 = min(open2, close2) - random.uniform(0, 0.5)
        candles.append((open2, high2, low2, close2))
        highlight_indices = [pattern_start, pattern_start + 1]
        
    elif pattern == "Bearish Engulfing":
        # First a small green candle
        open1 = random.uniform(98, 102)
        close1 = open1 + random.uniform(1, 2)
        high1 = max(open1, close1) + random.uniform(0, 0.5)
        low1 = min(open1, close1) - random.uniform(0, 0.5)
        candles.append((open1, high1, low1, close1))
        
        # Then a big red candle that engulfs it
        open2 = close1
        close2 = open1 - random.uniform(1, 2)
        high2 = max(open2, close2) + random.uniform(0, 0.5)
        low2 = min(open2, close2) - random.uniform(0, 0.5)
        candles.append((open2, high2, low2, close2))
        highlight_indices = [pattern_start, pattern_start + 1]
        
    elif pattern == "Morning Star":
        # Red candle
        candles.append(generate_random_candle(100))
        # Doji
        body = random.uniform(95, 105)
        candles.append((body, body+0.5, body-0.5, body+0.1))
        # Green candle
        candles.append(generate_random_candle(body))
        highlight_indices = [pattern_start, pattern_start + 1, pattern_start + 2]
        
    elif pattern == "Evening Star":
        # Green candle
        candles.append(generate_random_candle(100))
        # Doji
        body = random.uniform(95, 105)
        candles.append((body, body+0.5, body-0.5, body+0.1))
        # Red candle
        candles.append(generate_random_candle(body))
        highlight_indices = [pattern_start, pattern_start + 1, pattern_start + 2]
        
    elif pattern == "Harami":
        # First a large candle
        open1 = random.uniform(98, 102)
        close1 = open1 + random.uniform(2, 4) if random.random() > 0.5 else open1 - random.uniform(2, 4)
        high1 = max(open1, close1) + 0.5
        low1 = min(open1, close1) - 0.5
        candles.append((open1, high1, low1, close1))
        
        # Then a small candle inside it
        open2 = random.uniform(min(open1, close1)+0.5, max(open1, close1)-0.5)
        close2 = open2 + random.uniform(-0.5, 0.5)
        high2 = max(open2, close2) + 0.2
        low2 = min(open2, close2) - 0.2
        candles.append((open2, high2, low2, close2))
        highlight_indices = [pattern_start, pattern_start + 1]
        
    elif pattern == "Marubozu":
        # Candle with no wicks
        open_price = random.uniform(95, 105)
        close_price = open_price + random.uniform(3, 6) if random.random() > 0.5 else open_price - random.uniform(3, 6)
        high = max(open_price, close_price)
        low = min(open_price, close_price)
        candles.append((open_price, high, low, close_price))
        highlight_indices = [pattern_start]
        
    elif pattern == "Three White Soldiers":
        for i in range(3):
            open_price = 95 + i
            close_price = open_price + random.uniform(2, 4)
            high = close_price + random.uniform(0, 0.5)
            low = open_price - random.uniform(0, 0.5)
            candles.append((open_price, high, low, close_price))
        highlight_indices = [pattern_start, pattern_start + 1, pattern_start + 2]
        
    elif pattern == "Three Black Crows":
        for i in range(3):
            open_price = 105 - i
            close_price = open_price - random.uniform(2, 4)
            high = open_price + random.uniform(0, 0.5)
            low = close_price - random.uniform(0, 0.5)
            candles.append((open_price, high, low, close_price))
        highlight_indices = [pattern_start, pattern_start + 1, pattern_start + 2]
        
    elif pattern == "Piercing Line":
        # Red candle
        open1 = random.uniform(100, 102)
        close1 = open1 - random.uniform(2, 3)
        high1 = max(open1, close1) + 0.5
        low1 = min(open1, close1) - 0.5
        candles.append((open1, high1, low1, close1))
        
        # Green candle that opens lower and closes above midpoint
        open2 = close1 - random.uniform(0.5, 1)
        close2 = open1 - (open1 - close1) * 0.6
        high2 = max(open2, close2) + 0.5
        low2 = min(open2, close2) - 0.5
        candles.append((open2, high2, low2, close2))
        highlight_indices = [pattern_start, pattern_start + 1]
        
    elif pattern == "Dark Cloud Cover":
        # Green candle
        open1 = random.uniform(98, 100)
        close1 = open1 + random.uniform(2, 3)
        high1 = max(open1, close1) + 0.5
        low1 = min(open1, close1) - 0.5
        candles.append((open1, high1, low1, close1))
        
        # Red candle that opens higher and closes below midpoint
        open2 = close1 + random.uniform(0.5, 1)
        close2 = open1 + (close1 - open1) * 0.6
        high2 = max(open2, close2) + 0.5
        low2 = min(open2, close2) - 0.5
        candles.append((open2, high2, low2, close2))
        highlight_indices = [pattern_start, pattern_start + 1]
        
    else:
        # Fallback for any missing patterns
        candles.append(generate_random_candle())
        highlight_indices = [pattern_start]
    
    # Add context after pattern
    last_close = candles[-1][3]
    candles.extend(generate_context_candles(5, last_close))
    
    return candles, highlight_indices

# ================================================================
#                IMPROVED MATPLOTLIB RENDERER
# ================================================================
def render_chart_with_highlight(candles, highlight_indices):
    fig, ax = plt.subplots(figsize=(10, 5))

    for i, (open_, high, low, close) in enumerate(candles):
        is_highlight = i in highlight_indices

        # Determine candle color
        base_color = "green" if close >= open_ else "red"

        # Highlight styling
        if is_highlight:
            wick_color = "yellow"
            body_edge = "yellow"
            body_alpha = 0.95
            line_width = 2.5
            
            # Add subtle background highlight
            ax.axvspan(i - 0.5, i + 0.5, color="yellow", alpha=0.1)
        else:
            wick_color = base_color
            body_edge = base_color
            body_alpha = 0.6
            line_width = 1.2

        # Draw wick
        ax.plot([i, i], [low, high], color=wick_color, linewidth=line_width, alpha=body_alpha)

        # Draw body
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
    ax.set_title(f"Pattern: {st.session_state.get('current_pattern', 'Unknown')}", 
                 color="white", fontsize=12, pad=20)
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#111111")
    
    # Add pattern name as subtitle during development
    if st.session_state.dev_override:
        fig.text(0.5, 0.02, f"DEV MODE: {st.session_state.get('current_pattern', '')}", 
                ha='center', color='orange', fontsize=8)
    
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

# Show current lock status
if st.session_state.dev_override:
    st.sidebar.info("🔓 Developer mode active")
else:
    if not st.session_state.unlock_b:
        st.sidebar.info("🔒 Set B: Score 70% in Set A")
    elif not st.session_state.unlock_c:
        st.sidebar.info("🔒 Set C: Score 70% in Set B")
    else:
        st.sidebar.success("✅ All sets unlocked!")

chosen_mode = st.sidebar.radio(
    "Select mode:",
    ["Set A", "Set B", "Set C"],
    index=["Set A", "Set B", "Set C"].index(st.session_state.mode),
    key="mode_selector"
)

st.session_state.mode = chosen_mode

# ================================================================
#               TOP STATS DISPLAY
# ================================================================
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    elapsed = int(time.time() - st.session_state.start_time)
    st.metric("⏱️ Timer", f"{elapsed}s")

with col2:
    st.metric("⭐ Score", st.session_state.score)

with col3:
    st.metric("🔥 Streak", st.session_state.streak)

with col4:
    accuracy = (st.session_state.score / max(1, st.session_state.round)) * 100
    st.metric("📊 Accuracy", f"{accuracy:.1f}%")

st.markdown("---")

# ================================================================
#               MAIN GAME DISPLAY
# ================================================================
# Generate new pattern if needed
if "current_pattern" not in st.session_state or st.session_state.get("new_round", True):
    correct_pattern = pick_pattern()
    st.session_state.current_pattern = correct_pattern
    candles, highlight_indices = generate_pattern_candles(correct_pattern)
    st.session_state.current_candles = candles
    st.session_state.current_highlights = highlight_indices
    st.session_state.new_round = False

st.markdown(f"## 📊 CHART ACTION – Identify the Pattern in **{st.session_state.mode}**")

fig = render_chart_with_highlight(st.session_state.current_candles, st.session_state.current_highlights)
st.pyplot(fig)

# ================================================================
#                 ANSWER BUTTONS
# ================================================================
st.markdown("## 🎯 IDENTIFY THE PATTERN")

active_patterns = get_active_patterns()
cols = st.columns(3)
clicked = None

for i, pat in enumerate(active_patterns):
    if cols[i % 3].button(pat, key=f"btn_{pat}", use_container_width=True):
        clicked = pat

# Handle answer
if clicked:
    correct = clicked == st.session_state.current_pattern
    
    if correct:
        st.session_state.last_feedback = "correct"
        st.session_state.score += 1
        st.session_state.streak += 1
    else:
        st.session_state.last_feedback = "incorrect"
        st.session_state.streak = 0
    
    st.session_state.round += 1
    st.session_state.start_time = time.time()
    st.session_state.new_round = True
    
    # Unlock logic
    if not st.session_state.unlock_b and st.session_state.mode == "Set A":
        if st.session_state.round >= 5 and (st.session_state.score / st.session_state.round) >= 0.7:
            st.session_state.unlock_b = True
            st.sidebar.success("🎉 Set B unlocked!")
            
    if not st.session_state.unlock_c and st.session_state.mode == "Set B" and st.session_state.unlock_b:
        if st.session_state.round >= 10 and (st.session_state.score / st.session_state.round) >= 0.7:
            st.session_state.unlock_c = True
            st.sidebar.success("🔥 Set C unlocked!")
    
    # Show feedback
    st.rerun()

# Show feedback message with timeout
if st.session_state.last_feedback:
    if time.time() - st.session_state.feedback_time < 2:  # Show for 2 seconds
        if st.session_state.last_feedback == "correct":
            st.success(f"🎉 Correct! It was **{st.session_state.current_pattern}**.")
        else:
            st.error(f"❌ Incorrect — it was **{st.session_state.current_pattern}**.")
    else:
        st.session_state.last_feedback = None

# ================================================================
#                       HINTS
# ================================================================
with st.expander("💡 Need a hint?"):
    mode = st.session_state.mode
    if mode == "Set A":
        st.markdown("""
        **Hammer:** Tiny body up top, long lower wick.  
        **Shooting Star:** Tiny body bottom, long upper wick.  
        **Doji:** Open ≈ close.  
        **Long-legged Doji:** Very long wicks, tiny body.  
        **Bullish Engulfing:** Big green candle engulfs previous red.  
        **Bearish Engulfing:** Big red candle engulfs previous green.
        """)
    elif mode == "Set B":
        st.markdown("""
        **Morning Star:** Red candle → Doji → Green candle.  
        **Evening Star:** Green candle → Doji → Red candle.  
        **Harami:** Small candle inside previous large candle.  
        **Marubozu:** Candle with no wicks (shaved head & tail).
        """)
    else:  # Set C
        st.markdown("""
        **Three White Soldiers:** Three consecutive green candles.  
        **Three Black Crows:** Three consecutive red candles.  
        **Piercing Line:** Red → Green that closes >50% into red.  
        **Dark Cloud Cover:** Green → Red that closes <50% into green.
        """)

st.markdown("---")

# ================================================================
#            PERFECT EXAMPLES GALLERY
# ================================================================
st.sidebar.markdown("### 📷 Perfect Examples")
if st.sidebar.button("CLICK FOR PERFECT EXAMPLES"):
    st.session_state.show_examples = True

if st.session_state.show_examples:
    st.markdown("## 📚 Perfect Textbook Examples")
    st.info(f"Showing {st.session_state.mode} patterns")
    
    # Simple visual representations
    example_patterns = get_active_patterns()
    cols = st.columns(3)
    
    for i, pat in enumerate(example_patterns):
        with cols[i % 3]:
            st.markdown(f"### {pat}")
            # Create a mini chart for each pattern
            fig, ax = plt.subplots(figsize=(3, 2))
            
            if pat in ["Hammer", "Shooting Star", "Doji", "Long-legged Doji", "Marubozu"]:
                # Single candle patterns
                if pat == "Hammer":
                    candle = (100, 100.5, 95, 100.2)
                elif pat == "Shooting Star":
                    candle = (100, 105, 99.5, 99.8)
                elif pat == "Doji":
                    candle = (100, 101, 99, 100)
                elif pat == "Long-legged Doji":
                    candle = (100, 105, 95, 100)
                else:  # Marubozu
                    candle = (98, 103, 98, 103)
                
                ax.plot([0, 0], [candle[2], candle[1]], color="black", linewidth=2)
                ax.add_patch(plt.Rectangle((-0.2, min(candle[0], candle[3])), 0.4, 
                                         abs(candle[3] - candle[0]), facecolor="green" if candle[3] >= candle[0] else "red"))
                ax.set_xlim(-1, 1)
                ax.set_ylim(candle[2]-1, candle[1]+1)
                
            elif pat in ["Bullish Engulfing", "Bearish Engulfing", "Harami", "Piercing Line", "Dark Cloud Cover"]:
                # Two candle patterns
                if pat == "Bullish Engulfing":
                    candles = [(102, 102.5, 99, 101), (101, 104, 100, 103.5)]
                    colors = ["red", "green"]
                elif pat == "Bearish Engulfing":
                    candles = [(98, 101.5, 97, 101), (101, 101.5, 97, 98)]
                    colors = ["green", "red"]
                elif pat == "Harami":
                    candles = [(98, 103, 97, 102), (100, 101.5, 99.5, 100.5)]
                    colors = ["green", "red"]
                elif pat == "Piercing Line":
                    candles = [(102, 102.5, 99, 100), (99, 101.5, 98.5, 101)]
                    colors = ["red", "green"]
                else:  # Dark Cloud Cover
                    candles = [(98, 101.5, 97, 101), (101, 102, 99.5, 99)]
                    colors = ["green", "red"]
                
                for i, (candle, color) in enumerate(zip(candles, colors)):
                    ax.plot([i, i], [candle[2], candle[1]], color="black", linewidth=2)
                    ax.add_patch(plt.Rectangle((i-0.2, min(candle[0], candle[3])), 0.4, 
                                             abs(candle[3] - candle[0]), facecolor=color))
                ax.set_xlim(-0.5, 2.5)
                ax.set_ylim(96, 105)
                
            else:
                # Three candle patterns
                if pat == "Morning Star":
                    candles = [(102, 102.5, 99, 100), (100, 100.5, 99.5, 100.1), (100, 103, 99.5, 102)]
                elif pat == "Evening Star":
                    candles = [(98, 101.5, 97, 101), (101, 101.5, 100.5, 101.1), (101, 101.5, 98, 99)]
                elif pat == "Three White Soldiers":
                    candles = [(98, 100, 97, 99.5), (99.5, 101, 99, 100.5), (100.5, 102, 100, 101.5)]
                else:  # Three Black Crows
                    candles = [(102, 103, 100, 102), (102, 102.5, 99, 100.5), (100.5, 101, 97, 98)]
                
                for i, candle in enumerate(candles):
                    color = "green" if candle[3] >= candle[0] else "red"
                    ax.plot([i, i], [candle[2], candle[1]], color="black", linewidth=2)
                    ax.add_patch(plt.Rectangle((i-0.2, min(candle[0], candle[3])), 0.4, 
                                             abs(candle[3] - candle[0]), facecolor=color))
                ax.set_xlim(-0.5, 3.5)
                ax.set_ylim(96, 105)
            
            ax.set_xticks([])
            ax.set_yticks([])
            fig.patch.set_facecolor("#f0f2f6")
            ax.set_facecolor("#f0f2f6")
            st.pyplot(fig)
            plt.close(fig)
    
    if st.button("Close Gallery", key="close_gallery"):
        st.session_state.show_examples = False
        st.rerun()

# ================================================================
#                     RESET GAME
# ================================================================
st.markdown("### 🔁 Reset Game")
if st.button("Start Over", key="reset_button"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
