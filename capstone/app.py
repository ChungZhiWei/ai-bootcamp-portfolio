import streamlit as st

from mahjong_chatbot import (
    TILE_INFO,
    random_advice,
    advice_hand,
)

st.set_page_config(page_title="Mahjong Hand Analyzer", page_icon="🀄", layout="wide")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "counts" not in st.session_state:
    st.session_state.counts = [0] * 34
if "bonus" not in st.session_state:
    st.session_state.bonus = [0] * 2
if "advice" not in st.session_state:
    st.session_state.advice = random_advice()

# ---------------------------------------------------------------------------
# Sidebar settings
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Analyzer Settings")
st.sidebar.markdown("These reflect the house rules / variant of Singapore Mahjong you're playing.")

allow_7pairs = st.sidebar.checkbox("Allow Seven Pairs (Qi Dui)", value=True,
                                    help="Treat 7 pairs as a valid winning hand shape.")
allow_13orphans = st.sidebar.checkbox("Allow Thirteen Orphans (Shi San Yao)", value=True,
                                       help="Treat Thirteen Orphans as a valid winning hand shape. ")
allow_peaceful = st.sidebar.checkbox("Allow Peaceful Hand (Ping Hu)", value=True,
                                       help="Treat Peaceful Hand as a bonus hand shape. ")
min_points = st.sidebar.number_input("Minimum points to win (Ji Hu / limit)", min_value=0, max_value=13,
                                      value=1, step=1,
                                      help="Your table's minimum point/fan threshold required to declare a win.")


# ---------------------------------------------------------------------------
# Main page — build the hand tile by tile
# ---------------------------------------------------------------------------
st.title("🀄 Mahjong Hand Analyzer")
st.write("Build your opening hand tile by tile below, then click **Analyze Hand** for recommended plays.")
st.write("Mahjong advice for the day: " + st.session_state.advice)

SUIT_SECTIONS = [
    ("🀇 Characters (万)", [t for t in TILE_INFO if t["suit"] == "m"]),
    ("🀐 Bamboos (条)", [t for t in TILE_INFO if t["suit"] == "s"]),
    ("🀙 Dots (筒)", [t for t in TILE_INFO if t["suit"] == "p"]),
    ("🀀 Honors", [t for t in TILE_INFO if t["suit"] == "z"]),
]

for section_title, tiles in SUIT_SECTIONS:
    st.subheader(section_title)
    cols = st.columns(len(tiles))
    for col, tile in zip(cols, tiles):
        with col:
            st.markdown(
                f"<div style='text-align:center;font-size:34px;line-height:1.1'>{tile['char']}</div>"
                f"<div style='text-align:center;font-size:11px;color:gray'>{tile['label']}</div>",
                unsafe_allow_html=True,
            )
            st.session_state.counts[tile["idx"]] = st.number_input(
                tile["label"], min_value=0, max_value=4, step=1,
                value=st.session_state.counts[tile["idx"]],
                key=f"tile_{tile['idx']}", label_visibility="collapsed",
            )

st.subheader("🌸 Bonus Tiles")
col1, col2 = st.columns(2)
with col1:
    st.session_state.bonus[0] = st.number_input(
        "Total number of bonus tiles held",
        min_value=0, max_value=12, step=1,
        value=st.session_state.bonus[0],
        key="total_bonus_tiles",
    )
with col2:
    if st.session_state.bonus[1] > st.session_state.bonus[0]:
        st.session_state.bonus[1] = st.session_state.bonus[0]

    st.session_state.bonus[1] = st.number_input(
        "Total number of valid bonus tiles held",
        min_value=0, max_value=st.session_state.bonus[0], step=1,
        value=st.session_state.bonus[1],
        key="valid_bonus_tiles",
    )

# ---------------------------------------------------------------------------
# Hand summary
# ---------------------------------------------------------------------------
counts = st.session_state.counts
bonus = st.session_state.bonus
total_hand_tiles = sum(counts)

hand_str = "".join(TILE_INFO[i]["char"] * counts[i] for i in range(34))

st.divider()
st.subheader("🖐️ Current Hand")
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown(f"<div style='font-size:30px'>{hand_str if hand_str else '(empty)'}</div>", unsafe_allow_html=True)
    if bonus[0]:
        st.write(f"Total Bonus tiles held: **{bonus[0]}** 🌸")
    if bonus[1]:
        st.write(f"Total Valid Bonus tiles held: **{bonus[1]}** 🌸")
with c2:
    st.metric("Hand tiles", total_hand_tiles)
    st.metric("Bonus tiles", bonus[0])

if total_hand_tiles not in (13, 14):
    st.info(
        f"A standard opening hand has **13 tiles** (or **14** if you're the dealer / it's your turn to discard). "
        f"You currently have **{total_hand_tiles}** tiles counted (flowers excluded). "
    )

analyze = st.button("🔍 Analyze Hand", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

if analyze:
    if total_hand_tiles == 0:
        st.warning("Add some tiles to your hand first!")
    elif total_hand_tiles == 13 or total_hand_tiles == 14:
        st.write(advice_hand(counts, bonus, min_points, allow_7pairs, allow_13orphans, allow_peaceful))
    else:
        st.info("This section only runs for 13 or 14 tile hands.")