import sys
from dotenv import load_dotenv
import os
import random
load_dotenv()
import pandas as pd

s2 = os.getenv('TEST_S2')
swid = os.getenv('TEST_SWID')
year = int(os.getenv('TEST_YEAR'))
league_id = int(os.getenv('TEST_LEAGUE_ID'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NineCat.fantasy_page import FantasyPage
import streamlit as st

directions = ["to right", "to left", "to bottom", "to top", "to bottom right", "to top left"]
direction = random.choice(directions)

st.markdown(
    f"""
    <style>
    .stApp {{
        background: #071121;
        background: linear-gradient(0deg,rgba(7, 17, 33, 1) 0%, rgba(122, 22, 52, 1) 69%, rgba(84, 31, 36, 1) 100%);
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# --- Load data ---
# fp = FantasyPage(league_id, s2, swid, year, "projected")
# df = fp.player_dataframe


mock_matchups =[(4, 7), (8, 5), (1, 6), (2, 3)]
mock_path1 = os.path.join("..", "mockData", "players.csv")
mock_path2 = os.path.join("..", "mockData", "scoreboard.csv")

scoreboard = pd.read_csv(mock_path2)
players_df = pd.read_csv(mock_path1)

# -----------------------------
# Page config
# -----------------------------

st.set_page_config(
    page_title="ESPN 9CAT Projector",
    page_icon="🏀",
    layout="wide"
)

# -----------------------------
# Mock matchup data
# -----------------------------
matchups = [
    {
        "team1_name": "Yop's Good Trades",
        "team2_name": "TRZ Nnamdi",
        "team1_players": ["Alice","Bob","Charlie","David","Eve"],
        "team2_players": ["Frank","Grace","Hannah","Ian","Jack"],
        "current_score": {"team1":102, "team2":98},
        "projected_score": {"team1":110, "team2":105},
        "stats_labels": ["PTS", "REB", "AST", "BLK", "STL", "FG%", "FT%"],
        "team1_stats": {"projected":[110,45,25,8,12,48,85],"current":[102,42,22,6,10,46,82]},
        "team2_stats": {"projected":[105,40,28,7,10,47,80],"current":[98,38,26,5,9,45,78]}
    },
    {
        "team1_name": "Zesty Zion",
        "team2_name": "SGA fan club",
        "team1_players": ["Anna","Ben","Carl","Diana","Eli"],
        "team2_players": ["Fay","Gabe","Helen","Ian","Jack"],
        "current_score": {"team1":95, "team2":100},
        "projected_score": {"team1":105, "team2":110},
        "stats_labels": ["PTS", "REB", "AST", "BLK", "STL", "FG%", "FT%"],
        "team1_stats": {"projected":[105,43,24,7,11,47,84],"current":[95,40,20,6,9,44,80]},
        "team2_stats": {"projected":[110,42,26,8,12,48,82],"current":[100,39,25,6,11,46,79]}
    }
]

players = [
    "LeBron James", "Anthony Davis", "Austin Reaves",
    "D'Angelo Russell", "Jarred Vanderbilt",
    "Rui Hachimura", "Cam Reddish", "Jaxson Hayes"
]

num_matchups = len(matchups)

# -----------------------------
# Session state for current matchup
# -----------------------------
if 'matchup_idx' not in st.session_state:
    st.session_state.matchup_idx = 0

current_idx = st.session_state.matchup_idx
current_matchup = matchups[current_idx]

# -----------------------------
# Header (persistent)
# -----------------------------
# st.markdown("<h3 style='text-align:center;'>Fantasy Matchups</h3>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; font-size:18px; font-weight:bold;'>Fantasy Matchups</div>", unsafe_allow_html=True)



# -----------------------------
# Navigation buttons (centered)
# -----------------------------
col_prev, empty_col, col_next = st.columns([1,23,1])

with col_prev:
    if st.button("⬅ PREV"):
        st.session_state.matchup_idx = max(st.session_state.matchup_idx - 1, 0)

with col_next:
    if st.button("NEXT ➡"):
        st.session_state.matchup_idx = min(st.session_state.matchup_idx + 1, num_matchups - 1)

# After buttons, update current matchup
current_idx = st.session_state.matchup_idx
current_matchup = matchups[current_idx]
st.markdown("---")



# -----------------------------
# Middle matchup display
# -----------------------------
with st.container():
    # Outer layout: left / middle / right
    col_left_outer, col_middle_outer, col_right_outer = st.columns([2, 5, 2])

    # Left team name
    with col_left_outer:
        inner_spacer, col_left = st.columns([0.1, 1])  # moves left content closer to center
        with col_left:
            st.markdown(f"""
            <div style="text-align:start; font-size:64px; font-weight:bold; font-family:Gill Sans, sans-serif;">
                {current_matchup['team1_name']}
            </div>
            """, unsafe_allow_html=True)
            
    # Middle scores
    with col_middle_outer:
        col_score1, col_vs, col_score2 = st.columns([1.045, 0.5, 1])  # split middle column
        # Team 1 score
        with col_score1:
            st.markdown(f"""
            <div style="text-align:center; font-family:Gill Sans, sans-serif;">
                <span style="font-size:64px; font-weight:bold">{current_matchup['current_score']['team1']}</span><br>
                <span style="
                    font-size:18px;
                    font-weight:bold;
                    font-family:Courier New, monospace;
                    color:white;
                    background-color:rgba(0, 0, 0, 0.5);
                    padding:8px 16px;
                    border-radius:20px;
                    display:inline-block;
                ">
                {current_matchup['projected_score']['team1']}
                </span>
            </div>
            """, unsafe_allow_html=True)
        # VS text
        with col_vs:
            st.markdown("<h3 style='text-align:center;'>VS</h3>", unsafe_allow_html=True)
        # Team 2 score
        with col_score2:
            st.markdown(f"""
            <div style="text-align:center; font-family:Gill Sans, sans-serif;">
                <span style="font-size:64px; font-weight:bold">{current_matchup['current_score']['team2']}</span><br>
                <span style="
                    font-size:18px;
                    font-weight:bold;
                    font-family:Courier New, monospace;
                    color:white;
                    background-color:rgba(0, 0, 0, 0.5);
                    padding:8px 16px;
                    border-radius:20px;
                    display:inline-block;
                ">
                {current_matchup['projected_score']['team2']}
                </span>
            </div>
            """, unsafe_allow_html=True)

    # Right team name
    with col_right_outer:
        st.markdown(f"""
        <div style="text-align:center; font-size:64px; font-weight:bold; font-family:Gill Sans, sans-serif;">
            {current_matchup['team2_name']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Outer container
    with st.container():
        # Fixed height layout
        col_left, col_center, col_right = st.columns([2, 5, 2])

        # -----------------------------
        # Left roster
        # -----------------------------
        with col_left:
            st.markdown("""
            <style>
                .roster-container {
                    background-color: black;
                    height: 450px;
                    overflow-y: auto;
                    padding: 2px;
                    border-radius: 2px;
                }
                .player-card {
                    color: white;
                    background-color: #242222;
                    padding: 10px 16px;
                    height: 60px;
                    margin-bottom: 4px;
                    border-radius: 0px;
                    text-align: center;
                    font-weight: bold;
                    transition: all 0.2s ease;
                    cursor: pointer;
                }
                .player-card:hover {
                    background-color: #2ca02c;
                    transform: scale(1.03);
                }
                .player-card.selected {
                    background-color: #ff7f0e;
                    border: 2px solid #fff;
                }
            </style>
            """, unsafe_allow_html=True)

            # Initialize selected player state
            if "selected_player" not in st.session_state:
                st.session_state.selected_player = None

            # Build HTML cards (scrollable)
            html_cards = "".join([
                f'<div class="player-card" onclick="window.parent.postMessage({{"type":"select_player","player":"{p}"}}, \'*\')">{p}</div>'
                for p in players
            ])

            st.markdown(f'<div class="roster-container">{html_cards}</div>', unsafe_allow_html=True)

            # Listen for player selection from frontend
            st.markdown("""
            <script>
            window.addEventListener("message", (event) => {
                if (event.data.type === "select_player") {
                    const player = event.data.player;
                    const streamlitEvent = new CustomEvent("streamlit_event", {detail: {player}});
                    window.parent.document.dispatchEvent(streamlitEvent);
                }
            });
            </script>
            """, unsafe_allow_html=True)

            # Simple Streamlit hack: use st.experimental_js to listen
            # clicked_player = st.text_input("hidden_selected_player", "", label_visibility="collapsed")
            # if clicked_player:
            #     st.session_state.selected_player = clicked_player

            # if st.session_state.selected_player:
            #     st.write(f"**Selected player:** {st.session_state.selected_player}")

        # -----------------------------
        # Center stats grid (8x3)
        # -----------------------------
        with col_center:
            for i, label in enumerate(current_matchup['stats_labels']):
                st.markdown(f"""
                <div style="
                    display:grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    align-items:center;
                    border: 1px solid #999;
                    border-radius:1px;
                    margin-bottom:0px;
                    background-color:#000000;
                ">
                    <div style="text-align:center; padding:8px; border-right:1px solid #999;">
                        <span style="font-size:20px; font-weight:bold;">{current_matchup['team1_stats']['current'][i]}</span>
                        <span style="
                            font-size:18px;
                            font-weight:bold;
                            font-family:Courier New, monospace;
                            color:white;
                            background-color:rgba(0,0,0,0.5);
                            padding:6px 12px;
                            border-radius:8px;
                            display:inline-block;
                            margin-left:6px;
                        ">
                            {current_matchup['team1_stats']['projected'][i]}
                        </span>
                    </div>
                    <div style="text-align:center; font-weight:bold; border-right:1px solid #999;">
                        {label}
                    </div>
                    <div style="text-align:center; padding:8px;">
                        <span style="font-size:20px; font-weight:bold;">{current_matchup['team2_stats']['current'][i]}</span>
                        <span style="
                            font-size:18px;
                            font-weight:bold;
                            font-family:Courier New, monospace;
                            color:white;
                            background-color:rgba(0,0,0,0.5);
                            padding:6px 12px;
                            border-radius:8px;
                            display:inline-block;
                            margin-left:6px;
                        ">
                            {current_matchup['team2_stats']['projected'][i]}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # -----------------------------
        # Right roster
        # -----------------------------
        with col_right:
            st.markdown(f"""
            <div style="
                background-color:black;
                height:400px;
                overflow-y:auto;
                padding:8px;
                border-radius:8px;
            ">
            {"".join([
                f'<div style="color:white; background-color:#ff7f0e; padding:6px 12px; margin-bottom:4px; border-radius:12px; text-align:center;">{p}</div>'
                for p in current_matchup['team2_players']
            ])}
            </div>
            """, unsafe_allow_html=True)


# -----------------------------
# Bottom: free agent filter (persistent)
# -----------------------------
st.markdown("---")
st.markdown("### Free Agent Filter")
free_agents = pd.DataFrame({"Player": ["FA1","FA2","FA3"], "PTS": [5,8,12]})
filter_pts = st.slider("Min Points", 0, 20, 5)
st.dataframe(free_agents[free_agents['PTS'] >= filter_pts], use_container_width=True)