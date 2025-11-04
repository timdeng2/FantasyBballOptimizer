import sys
from dotenv import load_dotenv
import os
load_dotenv()
import pandas as pd
import altair as alt

import numpy as np
s2 = os.getenv('TEST_S2')
swid = os.getenv('TEST_SWID')
year = int(os.getenv('TEST_YEAR'))
league_id = int(os.getenv('TEST_LEAGUE_ID'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from NineCat.fantasy_page import FantasyPage
import streamlit as st


from pathlib import Path
import base64

# -----------------------------
# Constants
# -----------------------------
from espn_api.basketball.constant import NINE_CAT_STATS
team_color_map = {
    "MIN" : "#236192",
    "NYK" : "#f58426",
    "CLE" : "#860038",
    "TOR" : "#b4975a",
    "DET" : "#1d42ba",
    "HOU" : "#ce1141",
    "IND" : "#fdbb30",
    "MIL" : "#00471b",
    "CHA" : "#00788c",
    "DEN" : "#fec524",
    "POR" : "#e03a3e",   
    "PHX" : "#e56020",
    "DAL" : "#b8c4ca",
    "UTA" : "#753bbd",
    "MIA" : "#98002e",
    "LAC" : "#1d428a",
    "CHI" : "#000000",
    "PHI" : "#002b5c",
    "SAS" : "#00b2a9",
    "MEM" : "#bc7844",
    "BKN" : "#ffffff",
    "NOP" : "#85714d",
    "BOS" : "#007a33",
    "OKC" : "#007ac1",
    "ORL" : "#0077c0",
    "GSW" : "#ffa300",
    "SAC" : "#5a2d81",
    "WAS" : "#e31837",
    "ATL" : "#c1d32f",
    "LAL" : "#552583"
}
# -----------------------------
# Load data
# -----------------------------
mock_path1 = os.path.join("mockData", "player_df.parquet")
mock_path2 = os.path.join("mockData", "scoreboard.parquet")

scoreboard = pd.read_parquet(mock_path2)
players_df = pd.read_parquet(mock_path1)

mock_matchups =[(5, 7), (6 , 4), (3, 2), (8, 1)]
num_matchups = len(mock_matchups)

players_df["Color"] = players_df["ProTeam"].map(team_color_map)

if 'players_df' not in st.session_state:
    st.session_state.players_df = players_df.copy()

# -----------------------------
# Session state for current matchup
# -----------------------------
# the storage that survives across reruns of UI
if 'matchup_idx' not in st.session_state:
    st.session_state.matchup_idx = 0

current_idx = st.session_state.matchup_idx
current_matchup = mock_matchups[current_idx]

team1_id, team2_id = current_matchup

# -----------------------------
# Helper functions
# -----------------------------
def remove_player(team_id, player_id):
    players_df = st.session_state.players_df
    if (players_df["Team ID"] == team_id).sum() <= 10:
        warning_dialog("Each team must have at least 10 players rostered.")
        return
    players_df.loc[players_df["Player ID"] == player_id, "Team ID"] = -1
    st.rerun()

def image_to_base64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

@st.dialog("Warning")
def warning_dialog(message : str):
    st.write(message)

@st.dialog("Add Player")
def add_player(player_id : int):
    st.write("Choose team to add to")
    players_df = st.session_state.players_df
    col1, col2 = st.columns(2)
    team1_name = scoreboard.loc[scoreboard['Team ID'] == team1_id, 'Team'].iloc[0]
    team2_name = scoreboard.loc[scoreboard['Team ID'] == team2_id, 'Team'].iloc[0]
    with col1:
        if st.button(team1_name, width='stretch'):
            if (players_df["Team ID"] == team1_id).sum() > 14:
                st.warning("Each team cannot have more than 14 players rostered.")
                return
            players_df.loc[players_df["Player ID"] == player_id, "Team ID"] = team1_id
            st.rerun()
            return
    with col2:
        if st.button(team2_name, width='stretch'):
            if (players_df["Team ID"] == team2_id).sum() > 14:
                st.warning("Each team cannot have more than 14 players rostered.")
                return
            players_df.loc[players_df["Player ID"] == player_id, "Team ID"] = team2_id
            st.rerun()
            return

@st.dialog("Player Details", width="large")
def show_player_details(player_data):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Player headshot
        path = Path("PlayerHeadshots") / f"{player_data['Player ID']}.png"
        if path.exists():
            st.image(str(path), use_container_width=True)
        
        # Basic info
        st.markdown(
            f'<p style="font-size: 36px; color: white; text-align: center;">{player_data["Player Name"]}</p>',
            unsafe_allow_html=True
        )
        positions = ["PG", "SG", "SF", "PF", "C"]
        playable = [pos for pos in positions if player_data[pos] == 1]
        st.markdown(
            f'<p style="font-size: 18px; color: #ccc; text-align: center; font-style: italic;">{", ".join(playable)}</p>',
            unsafe_allow_html=True
        )
        
        # Show badges
        st.subheader("Top Categories")
        badges = get_badges(player_data)

        # Create rows of 3 badges each
        for row_start in range(0, len(badges), 3):
            badge_cols = st.columns(3)
            row_badges = badges[row_start:row_start + 3]
            
            for idx, badge_path in enumerate(row_badges):
                with badge_cols[idx]:
                    badge_string = badge_path.split("/")[-1].split(".")[0]
                    badge_cat = badge_string.split("_")[0]
                    badge_tier = badge_string.split("_")[1]
                    if badge_tier != "HOF":
                        badge_tier = badge_tier.lower().capitalize()
                    else:
                        badge_tier = "Hall of Fame"
                    if Path(badge_path).exists():
                        st.image(badge_path, caption=f"{badge_tier} {badge_cat} Badge", use_container_width=True)
    
    with col2:
        st.subheader("Statistics")
        CATS = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG%', 'FT%', '3PM', 'TO']

        stat_cols = st.columns(3)
        for idx, cat in enumerate(CATS):
            with stat_cols[idx % 3]:
                actual_stat = player_data[cat]
                percentile = player_data[f"{cat}_percentile"]
                

                if cat in ['FG%', 'FT%']:
                    display_value = f"{actual_stat * 100:.0f}%"
                else:
                    display_value = f"{actual_stat:.1f}"
                if percentile >= 70:
                    color = "#147914" 
                elif percentile <= 35:
                    color = "#851616"  
                else:
                    color = "white"
                
                st.markdown(f"**{cat}**")
                st.markdown(
                    f'<p style="font-size: 28px; font-weight: normal; color: {color}; margin-bottom: 5px;">{display_value}</p>',
                    unsafe_allow_html=True
                )
        
        st.divider()

        st.subheader("Percentiles", help="Shows how the player ranks in each category compared to current rostered players.")
        for cat in CATS:
            percentile = player_data[f"{cat}_percentile"]
            col_cat, col_bar = st.columns([1, 3])
            with col_cat:
                st.markdown(f"**{cat}:**")
            with col_bar:
                st.progress(percentile / 100, text=f"{percentile:.1f}%")

def get_badges(row):
    CATS = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG%', 'FT%', '3PM', 'TO']
    badges = []
    cat_values = [(cat, row[f"{cat}_percentile"]) for cat in CATS]
    cat_values.sort(key=lambda x: x[1], reverse=True)
    for cat, val in cat_values:
        if val >= 95:
            badges.append("Badges/" + cat + "_HOF.png")
        elif val >= 84:
            badges.append("Badges/" + cat + "_GOLD.png")
        elif val >= 73:
            badges.append("Badges/" + cat + "_SILVER.png")
        elif val >= 60:
            badges.append("Badges/" + cat + "_BRONZE.png")
    return badges

def get_top_3_badges(row):
    CATS = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG%', 'FT%', '3PM', 'TO']
    badges = []
    cat_values = [(cat, row[f"{cat}_percentile"]) for cat in CATS]
    cat_values.sort(key=lambda x: x[1], reverse=True)
    top3 = cat_values[:3]
    for cat, val in top3:
        if val >= 95:
            badges.append("Badges/" + cat + "_HOF.png")
        elif val >= 84:
            badges.append("Badges/" + cat + "_GOLD.png")
        elif val >= 73:
            badges.append("Badges/" + cat + "_SILVER.png")
        elif val >= 60:
            badges.append("Badges/" + cat + "_BRONZE.png")
    return badges

def sort_key(row):
    if row["Name"] == "Current":
        return (row["Stat"], row["Team"], float('inf'))  # "Current" always last in sort = first in stack
    else:
        return (row["Stat"], row["Team"], -row["Value"])
# -----------------------------
# Setup Streamlit page
# -----------------------------
st.set_page_config(
    page_title="ESPN 9CAT Projector",
    page_icon="🏀",
    layout="wide"
)

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
# -----------------------------
# Header / Navbar / Buttons
# -----------------------------
st.markdown("<div style='text-align:center; font-size:18px; font-weight:bold;'>Fantasy Matchups</div>", unsafe_allow_html=True)


col_prev, empty_col, col_next = st.columns([1,23,1])

with col_prev:
    if st.button("⬅ PREV"):
        st.session_state.matchup_idx = max(st.session_state.matchup_idx - 1, 0)

with col_next:
    if st.button("NEXT ➡"):
        st.session_state.matchup_idx = min(st.session_state.matchup_idx + 1, num_matchups - 1)


# After buttons, update current matchup
current_idx = st.session_state.matchup_idx
current_matchup = mock_matchups[current_idx]
team1_id, team2_id = current_matchup
st.markdown("---")

# -----------------------------
# Middle matchup display
# -----------------------------
# -----------------------------
# Scoreboard display
# -----------------------------
col_left_outer, col_middle_outer, col_right_outer = st.columns([2, 5, 2])

# Left team name
with col_left_outer:
    inner_spacer, col_left = st.columns([0.1, 1])  # moves left content closer to center
    with col_left:
        st.markdown(f"""
        <div style="text-align:start; font-size:64px; font-weight:bold; font-family:Gill Sans, sans-serif;">
            {scoreboard.loc[scoreboard['Team ID'] == team1_id, 'Team'].iloc[0]}
        </div>
        """, unsafe_allow_html=True)
        
# Middle scores
with col_middle_outer:
    col_score1, col_vs, col_score2 = st.columns([1.045, 0.5, 1])  # split middle column
    # Team 1 score
    # projected scores just 4.5 for now
    with col_score1:
        st.markdown(f"""
        <div style="text-align:center; font-family:Gill Sans, sans-serif;">
            <span style="font-size:64px; font-weight:bold">{scoreboard.loc[scoreboard['Team ID'] == team1_id, 'Score'].iloc[0]}</span><br>
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
            {4.5} 
            </span>
        </div>
        """, unsafe_allow_html=True)
    with col_vs:
        st.markdown("<h3 style='text-align:center;'>VS</h3>", unsafe_allow_html=True)
    # Team 2 score
    with col_score2:
        st.markdown(f"""
        <div style="text-align:center; font-family:Gill Sans, sans-serif;">
            <span style="font-size:64px; font-weight:bold">{scoreboard.loc[scoreboard['Team ID'] == team2_id, 'Score'].iloc[0]}</span><br>
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
            {4.5}
            </span>
        </div>
        """, unsafe_allow_html=True)

# Right team name
with col_right_outer:
    st.markdown(f"""
    <div style="text-align:center; font-size:64px; font-weight:bold; font-family:Gill Sans, sans-serif;">
        {scoreboard.loc[scoreboard['Team ID'] == team2_id, 'Team'].iloc[0]}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# Roster + data display
# -----------------------------
col1, middle, col2 = st.columns((1,4,1))
with col1:
    team_players = st.session_state.players_df.loc[
        st.session_state.players_df["Team ID"] == team1_id
    ]

    css = """
    .st-key-black_b {
        background-color: rgba(64, 10, 32, 0.4);
    }
    
    /* Make buttons smaller and more compact */
    .st-key-black_b button {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.75rem !important;
        min-height: 1.75rem !important;
        height: 1.75rem !important;
    }
    
    /* Reduce gap between elements */
    .st-key-black_b [data-testid="column"] {
        padding: 0.25rem !important;
    }
    """

    st.html(f"<style>{css}</style>")
    
    with st.container(height=1500, gap="small", key="black_b"):
        for idx, (_, row) in enumerate(team_players.iterrows()):
            name = row["Player Name"]
            positions = ["PG", "SG", "SF", "PF", "C"]
            playable = [pos for pos in positions if row[pos] == 1]
            playable_pos = ", ".join(playable)
            pid = row["Player ID"]
            path = Path("PlayerHeadshots") / f"{pid}.png"
            badges = get_top_3_badges(row)
            

            col_img, col_info = st.columns([1.5, 2])
            
            with col_img:
                if path.exists():
                    st.image(str(path), use_container_width=True)
            
            with col_info:
                st.markdown(
                    f'<p style="font-size: 20px; font-weight: 600; margin-bottom: 0.25rem;">{name}</p>',
                    unsafe_allow_html=True
                )
                
                badge_cols = st.columns(3)
                for badge_idx, badge_path in enumerate(badges):
                    if badge_idx < 3:
                        with badge_cols[badge_idx]:
                            if Path(badge_path).exists():
                                st.image(badge_path, use_container_width=True)
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("Details", key=f"player_btn_{pid}", use_container_width=True):
                        show_player_details(row)
                with btn_col2:
                    if st.button("Remove", key=f"remove_btn_{pid}", type="primary", use_container_width=True):
                        remove_player(team1_id, pid)
            
            st.divider()
with col2:
    team_players = st.session_state.players_df.loc[
        st.session_state.players_df["Team ID"] == team2_id
    ]

    css = """
    .st-key-black_b2 {
        background-color: rgba(64, 10, 32, 0.4);
    }
    
    /* Make buttons smaller and more compact */
    .st-key-black_b2 button {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.75rem !important;
        min-height: 1.75rem !important;
        height: 1.75rem !important;
    }
    
    /* Reduce gap between elements */
    .st-key-black_b2 [data-testid="column"] {
        padding: 0.25rem !important;
    }
    """

    st.html(f"<style>{css}</style>")
    
    with st.container(height=1500, gap="small", key="black_b2"):
        for idx, (_, row) in enumerate(team_players.iterrows()):
            name = row["Player Name"]
            positions = ["PG", "SG", "SF", "PF", "C"]
            playable = [pos for pos in positions if row[pos] == 1]
            playable_pos = ", ".join(playable)
            pid = row["Player ID"]
            path = Path("PlayerHeadshots") / f"{pid}.png"
            badges = get_top_3_badges(row)
            
            col_info, col_img = st.columns([2, 1.5])
            
            with col_img:
                if path.exists():
                    st.image(str(path), use_container_width=True)
            
            with col_info:
                st.markdown(
                    f'<p style="font-size: 20px; font-weight: 600; margin-bottom: 0.25rem;">{name}</p>',
                    unsafe_allow_html=True
                )
                
                badge_cols = st.columns(3)
                for badge_idx, badge_path in enumerate(badges):
                    if badge_idx < 3:
                        with badge_cols[badge_idx]:
                            if Path(badge_path).exists():
                                st.image(badge_path, use_container_width=True)

                btn_col2, btn_col1 = st.columns(2)
                with btn_col1:
                    if st.button("Details", key=f"player_btn_{pid}", use_container_width=True):
                        show_player_details(row)
                with btn_col2:
                    if st.button("Remove", key=f"remove_btn_{pid}", type="primary", use_container_width=True):
                        remove_player(team2_id, pid)
            
            st.divider()



with middle:
    combined_data = []

    for stat in NINE_CAT_STATS:
        if stat not in ["FGA", "FTA", "FTM","FGM"]:
            expected_col = f"Expected {stat}"

            # TEAM 1: each player’s expected stat
            team1_name = scoreboard.loc[scoreboard["Team ID"] == team1_id, "Team"].iloc[0]
            team1_players = players_df.loc[players_df["Team ID"] == team1_id, ["Player Name", expected_col, "ProTeam"]]
            team1_players = team1_players.rename(columns={expected_col: "Value"})
            team1_players["Stat"] = stat
            team1_players["Name"] = team1_players["Player Name"]

            # add current as its own base segment
            team1_current = scoreboard.loc[scoreboard["Team ID"] == team1_id, stat].iloc[0]
            combined_data.append({
                "Team": team1_name,
                "Stat": stat,
                "Name": "Current",
                "Value": team1_current,
                'Color': 'grey'
            })

            # add player-level expected segments
            for _, row in team1_players.iterrows():
                combined_data.append({
                    "Team": team1_name,
                    "Stat": stat,
                    "Name": row["Name"],
                    "Value": row["Value"],
                    'Color': team_color_map[row["ProTeam"]]
                })

            # TEAM 2
            team2_name = scoreboard.loc[scoreboard["Team ID"] == team2_id, "Team"].iloc[0]
            team2_players = players_df.loc[players_df["Team ID"] == team2_id, ["Player Name", expected_col, "ProTeam"]]
            team2_players = team2_players.rename(columns={expected_col: "Value"})
            team2_players["Stat"] = stat
            team2_players["Name"] = team2_players["Player Name"]

            # add current
            team2_current = scoreboard.loc[scoreboard["Team ID"] == team2_id, stat].iloc[0]
            combined_data.append({
                "Team": team1_name,
                "Stat": stat,
                "Name": "Current",
                "Value": team2_current,
                'Color': 'grey'
            })

            for _, row in team2_players.iterrows():
                combined_data.append({
                    "Team": team2_name,
                    "Stat": stat,
                    "Name": row["Name"],
                    "Value": row["Value"],
                    'Color': team_color_map[row["ProTeam"]]
                })

    df_chart = pd.DataFrame(combined_data)

    # --------------------------------------------
    # Sort segments (so larger segments are lower)
    # --------------------------------------------
    # Sorting by Stat, Team, descending Value ensures biggest segments appear first (bottom of stack)
    df_chart['sort_key'] = df_chart.apply(sort_key, axis=1)
    df_chart = df_chart.sort_values(by='sort_key')
    df_chart = df_chart.drop(columns=['sort_key'])

    # --------------------------------------------
    # Build Altair Chart
    # --------------------------------------------
    bars = (
        alt.Chart(df_chart)
        .mark_bar()
        .encode(
            x=alt.X("Stat:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("sum(Value):Q", title=None),
            color=alt.Color("Color:N", 
                scale=None,  # scale=None tells Altair to use the values as-is
                legend=None  # hide legend if you want
            ),
            order=alt.Order("sort_key:Q"),  # This is key - tells Altair stack order
            xOffset="Team:N",
            tooltip=["Team", "Name", "Value"]
        )
    )
    text = (
        alt.Chart(df_chart)
        .mark_text(dy=-10, dx=4, color='white', fontSize=20)  # dy=-5 puts it slightly above the bar
        .encode(
            x=alt.X("Stat:N"),
            y=alt.Y("sum(Value):Q"),
            text=alt.Text("sum(Value):Q", format=".1f"),  # format to 1 decimal place
            xOffset="Team:N"
        )
    )

    # Combine the layers
    chart = (bars + text).properties(
        width=50,
        height=1500
    ).configure_mark()

    st.altair_chart(chart, use_container_width=True)

st.markdown("---")
st.markdown("### Free Agents")

free_agents_df = st.session_state.players_df.loc[
    st.session_state.players_df['Team ID'] == -1
].copy()

# Tabs for different filter categories
tab1, tab2 = st.tabs(["Stats", "Expected Stats"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_pts = st.slider("Min PTS", 0.0, 35.0, 0.0)
        filter_reb = st.slider("Min REB", 0.0, 15.0, 0.0)
        filter_ast = st.slider("Min AST", 0.0, 15.0, 0.0)
    with col2:
        filter_fg_pct = st.slider("Min FG%", 0.0, 1.0, 0.0)
        filter_ft_pct = st.slider("Min FT%", 0.0, 1.0, 0.0)
        filter_3pm = st.slider("Min 3PM", 0.0, 5.0, 0.0)
    with col3:
        filter_stl = st.slider("Min STL",  0.0, 5.0, 0.0)
        filter_blk = st.slider("Min BLK", 0.0, 5.0, 0.0)
        filter_to = st.slider("Max TO",  0.0, 10.0, 10.0)

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        exp_pts = st.slider("Min Expected PTS", 0.0, 250.0, 0.0)
        exp_reb = st.slider("Min Expected REB",  0.0, 150.0, 0.0)
        exp_ast = st.slider("Min Expected AST",  0.0, 150.0, 0.0)
    with col2:
        exp_3pm = st.slider("Min Expected 3PM", 0.0, 50.0, 0.0)
        exp_stl = st.slider("Min Expected STL",  0.0, 50.0, 0.0)
        exp_blk = st.slider("Min Expected BLK", 0.0, 50.0, 0.0)
    with col3:
        exp_to = st.slider("Max Expected TO",  0.0, 50.0, 50.0)

# Apply filters
filtered_df = free_agents_df[
    (free_agents_df['PTS'] >= filter_pts) &
    (free_agents_df['FG%'] >= filter_fg_pct) &
    (free_agents_df['FT%'] >= filter_ft_pct) &
    (free_agents_df['REB'] >= filter_reb) &
    (free_agents_df['AST'] >= filter_ast) &
    (free_agents_df['STL'] >= filter_stl) &
    (free_agents_df['BLK'] >= filter_blk) &
    (free_agents_df['3PM'] >= filter_3pm) &
    (free_agents_df['TO'] <= filter_to) &
    (free_agents_df['Expected PTS'] >= exp_pts) &
    (free_agents_df['Expected REB'] >= exp_reb) &
    (free_agents_df['Expected AST'] >= exp_ast) &
    (free_agents_df['Expected 3PM'] >= exp_3pm) &
    (free_agents_df['Expected STL'] >= exp_stl) &
    (free_agents_df['Expected BLK'] >= exp_blk) &
    (free_agents_df['Expected TO'] <= exp_to)
]

# Compact sort controls inline with count
col_count, col_sort1, col_sort2 = st.columns([1, 2, 1])
with col_count:
    st.markdown(f"**{len(filtered_df)} players available**")
with col_sort1:
    sort_by = st.selectbox("Sort", [
        "PTS", "REB", "AST", "FG%", "FT%", "3PM", "STL", "BLK", "TO",
        "Expected PTS", "Expected REB", "Expected AST"
    ], label_visibility="collapsed")
with col_sort2:
    ascending = st.toggle("↑ Asc", value=False, help="Toggle sort order")

# Apply sorting
filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
# Compact CSS for skinny rows
css_fa = """
.st-key-free_agents {
    background-color: rgba(32, 32, 64, 0.3);
}

.st-key-free_agents button {
    padding: 0.15rem 0.4rem !important;
    font-size: 0.7rem !important;
    min-height: 1.5rem !important;
    height: 1.5rem !important;
}

.st-key-free_agents [data-testid="column"] {
    padding: 0.1rem !important;
}

/* Reduce divider thickness */
.st-key-free_agents hr {
    margin: 0.25rem 0 !important;
}
"""

st.html(f"<style>{css_fa}</style>")

tab1, tab2 = st.tabs(["Free Agent List", "Compare Stats"])
with tab1:
    with st.container(height=800, key="free_agents"):
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            name = row["Player Name"]
            positions = ["PG", "SG", "SF", "PF", "C"]
            playable = [pos for pos in positions if row[pos] == 1]
            playable_pos = ", ".join(playable)
            pid = row["Player ID"]
            
            # Single row: Name/Position | Stats | Buttons
            col_name, col_stats, col_buttons = st.columns([1.5, 3, 1])
            
            with col_name:
                st.markdown(
                    f'<div style="padding: 0.25rem 0;">'
                    f'<p style="font-size: 24px; font-weight: 600; margin: 0; line-height: 1.2;">{name}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col_stats:
                # Ultra-compact stats display
                st.markdown(
                    f'<div style="font-size: 20px; line-height: 1.8; padding: 0.25rem 0;">'
                    f'<b>PTS:</b> {row["PTS"]:.1f} | '
                    f'<b>REB:</b> {row["REB"]:.1f} | '
                    f'<b>AST:</b> {row["AST"]:.1f} | '
                    f'<b>FG%:</b> {row["FG%"]:.3f} | '
                    f'<b>FT%:</b> {row["FT%"]:.3f} | '
                    f'<b>3PM:</b> {row["3PM"]:.1f} | '
                    f'<b>STL:</b> {row["STL"]:.1f} | '
                    f'<b>BLK:</b> {row["BLK"]:.1f} | '
                    f'<b>TO:</b> {row["TO"]:.1f}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col_buttons:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("Details", key=f"fa_details_{pid}", use_container_width=True, help="View Details"):
                        show_player_details(row)
                with btn_col2:
                    if st.button("➕", key=f"fa_sign_{pid}", type="primary", use_container_width=True, help="Sign Player"):
                        # Add sign player function here
                        add_player(pid)
            
            st.divider()
with tab2:
    numeric_columns = ['PTS', 'REB', 'AST', 'FG%', 'FT%', '3PM', 'STL', 'BLK', 'TO',
                       'Expected PTS', 'Expected REB', 'Expected AST', 'Expected 3PM',
                       'Expected STL', 'Expected BLK', 'Expected TO', 'FGA', 'FTA', 'FTM','FGM']

    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("X-axis", numeric_columns, index=0)
    with col2:
        y_axis = st.selectbox("Y-axis", numeric_columns, index=1)

        filtered_df['LocalPath'] = filtered_df['Player ID'].apply(
            lambda pid: str(Path("PlayerHeadshots") / f"{pid}.png")
            if (Path("PlayerHeadshots") / f"{pid}.png").exists()
            else str(Path("PlayerHeadshots") / "unknown.png")
        )
        filtered_df["ImageURL"] = filtered_df["LocalPath"].apply(image_to_base64)

    # Now build your Altair chart
    chart = (
        alt.Chart(filtered_df, background="#171B20")
        .mark_image(width=60, height=60)
        .encode(
            x=alt.X(x_axis, title=x_axis, axis=alt.Axis(tickCount=10)),
            y=alt.Y(y_axis, title=y_axis, axis=alt.Axis(tickCount=10)),
            url="ImageURL",
            tooltip=["Player Name", x_axis, y_axis]
        )
        .properties(
            width=900,
            height=900
        )
    )
    st.altair_chart(chart, use_container_width=True)