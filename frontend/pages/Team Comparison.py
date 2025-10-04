import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from Match_tabs.Base import load_match_events
from Match_tabs.Shot_analysis import create_shot_map
from Match_tabs.Movement_analysis import Movement_analysis  
from Match_tabs.Progressive_play import progressive_play
from Match_tabs.Set_piece import Set_piece
from Match_tabs.Basic_Analysis import load_basic_analysis
from Match_tabs.Base import get_shots_for_teams

MAX_COLUMNS = 2  # Maximum comparison blocks per row

def Team_Comparison():
    # Initialize blocks and next id counter
    if "team_blocks" not in st.session_state:
        st.session_state["team_blocks"] = [1]
    if "next_team_block_id" not in st.session_state:
        st.session_state["next_team_block_id"] = max(st.session_state["team_blocks"]) + 1

    # Title and Add button
    col_title, col_add = st.columns([10, 1])
    with col_title:
        st.header("🏆 Advanced Team Comparison")
    with col_add:
        add_disabled = len(st.session_state["team_blocks"]) >= 4  # Max 4 comparisons
        if st.button("➕", help="Add new team comparison", disabled=add_disabled):
            new_id = st.session_state["next_team_block_id"]
            st.session_state["team_blocks"].append(new_id)
            st.session_state["next_team_block_id"] += 1
            st.rerun()

    st.info(
        "ℹ️ The statistics and visualizations shown here represent **average values from previous matches**, "
        "not a single game. This helps compare overall team performance trends."
    )

    teams = ['Argentina', 'France', 'Croatia', 'Morocco', 'Brazil', 'Netherlands',
            'Portugal', 'England', 'Japan', 'Spain', 'Germany', 'Belgium']

    # Function to render a single comparison block
    def render_comparison_block(block_id, block_number):
        # Header with delete button
        col_header, col_delete = st.columns([10, 1])
        
        with col_header:
            st.subheader(f"Comparison {block_number}")
        
        with col_delete:
            # Delete button (disabled if only one block)
            disabled = (len(st.session_state["team_blocks"]) == 1)
            if st.button("❌", key=f"delete_team_{block_id}", disabled=disabled):
                if block_id in st.session_state["team_blocks"]:
                    st.session_state["team_blocks"].remove(block_id)
                st.rerun()

        # Team selection
        col1, col2 = st.columns(2)
        with col1:
            team1 = st.selectbox(
                "Select Team 1", 
                teams, 
                key=f"team1_{block_id}"
            )
        with col2:
            team2 = st.selectbox(
                "Select Team 2", 
                [t for t in teams if t != team1],
                key=f"team2_{block_id}"
            )

        if team1 and team2:
            st.markdown(f"**{team1} vs {team2}**")
            
            # Styled radio button
            st.markdown("""
                <style>
                /* Target radio widget container */
                div[data-testid="stRadio"] {
                    background-color: #FFE4B5;  /* light orange */
                    padding: 15px;
                    border-radius: 10px;
                    border: 1px solid #ddd;
                    margin-bottom: 20px;
                }

                /* Optional: style radio labels */
                div[data-testid="stRadio"] label {
                    font-weight: 500;
                    margin-right: 15px;
                }
                </style>
            """, unsafe_allow_html=True)

            analysis_section = st.radio(
                "Choose analysis type:",
                ["📈 Basic Analysis", "🎯 Shot Analysis"],
                horizontal=True,
                key=f"analysis_{block_id}"
            )

            # ---------------------- BASIC ANALYSIS ---------------------- #
            if analysis_section == "📈 Basic Analysis":
                load_basic_analysis(team1=team1, team2=team2, match_or_team="Team") 
                
            elif analysis_section == "🎯 Shot Analysis":
                st.subheader("Shot Analysis & Expected Goals")
                shots_df = get_shots_for_teams(team1, team2)
                shots_df = shots_df[shots_df['team'].isin([team1, team2])]

                if shots_df.empty:
                    st.warning(f"No shot data available for {team1} and {team2}.")
                    return
                    
                fig, outcomes_ = create_shot_map(shots_df)
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                
                # Mapping synonyms to standard names
                key_map = {
                    "Off T": "Off Target",
                    "Off Target": "Off Target"
                }

                # Normalize keys for each team
                normalized = {}
                for team, outcomes in outcomes_.items():
                    team_data = {}
                    for k, v in outcomes.items():
                        std_key = key_map.get(k, k)
                        team_data[std_key] = team_data.get(std_key, 0) + v
                    normalized[team] = team_data

                # Get all unique keys across teams
                all_keys = set()
                for team_data in normalized.values():
                    all_keys.update(team_data.keys())

                # Fill missing keys with 0
                for team, outcomes in normalized.items():
                    for k in all_keys:
                        outcomes.setdefault(k, 0)
               
                home_shot_outcomes = normalized[team1]
                away_shot_outcomes = normalized[team2]
                
                if len(home_shot_outcomes.keys()) > len(away_shot_outcomes.keys()):
                    for key in home_shot_outcomes.keys():
                        if key not in away_shot_outcomes:
                            away_shot_outcomes[key] = 0
                elif len(home_shot_outcomes.keys()) < len(away_shot_outcomes.keys()):
                    for key in away_shot_outcomes.keys():
                        if key not in home_shot_outcomes:
                            home_shot_outcomes[key] = 0
                            
                with col1:
                    st.subheader(f"{team1} Team Shots")
                    for val in home_shot_outcomes.values():
                        st.markdown(val)
                    filtered_home = {k: v for k, v in outcomes_[team1].items() if k != "All Shots"}
                    fig_home = px.pie(
                        values=filtered_home.values(),
                        names=filtered_home.keys(),
                        title=f"{team1} Shot Outcomes",
                        color_discrete_sequence=['blue', 'lightblue', 'navy', 'darkblue']
                    )
                    st.plotly_chart(fig_home, use_container_width=True)
                                
                with col2:
                    st.subheader("Shot Outcomes")
                    for val in home_shot_outcomes.keys():
                        st.markdown(val)
                    
                with col3:
                    st.subheader(f"{team2} Team Shots")
                    for val in away_shot_outcomes.values():
                        st.markdown(val)
                    filtered_away = {k: v for k, v in outcomes_[team2].items() if k != "All Shots"}
                    fig_away = px.pie(
                        values=filtered_away.values(),
                        names=filtered_away.keys(),
                        title=f"{team2} Shot Outcomes",
                        color_discrete_sequence=['red', 'lightcoral', 'darkred', 'maroon']
                    )
                    st.plotly_chart(fig_away, use_container_width=True)
        
        st.divider()

    # Display blocks
    blocks = st.session_state["team_blocks"]
    
    if len(blocks) == 1:
        render_comparison_block(blocks[0], 1)
    else:
        for row_start in range(0, len(blocks), MAX_COLUMNS):
            row_blocks = blocks[row_start: row_start + MAX_COLUMNS]
            cols = st.columns(len(row_blocks))
            for i, block_id in enumerate(row_blocks):
                with cols[i]:
                    render_comparison_block(block_id, row_start + i + 1)

if __name__ == "__main__":
    Team_Comparison()