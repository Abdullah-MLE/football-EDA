import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pages.data import load_data

import json
import os
from pathlib import Path

from Match_tabs.Basic_Analysis import load_basic_analysis
from Match_tabs.Shot_analysis import create_shot_map
from Match_tabs.Base import load_match_events
from Match_tabs.Movement_analysis import Movement_analysis
from Match_tabs.Progressive_play import progressive_play 
from Match_tabs.Set_piece import Set_piece
import random

try:
    from statsbombpy import sb
    STATSBOMB_AVAILABLE = True
except ImportError:
    STATSBOMB_AVAILABLE = False
    st.warning("StatsBombPy not available. Using mock data for demonstration.")


st.set_page_config(
    page_title="Match Analysis- World Cup 2022",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

MAX_COLUMNS = 2  # Maximum match analysis blocks per row

stages = ["All Stages", "Group Stage", "Round of 16", "Quarter-finals", "Semi-finals", "Final"]

# Data loading functions
@st.cache_data
def load_world_cup_data():
    """Load World Cup 2022 data from StatsBomb or create mock data"""
    try:
        # Get World Cup 2022 matches
        competitions = sb.competitions()
        wc_2022 = competitions[
            (competitions['competition_name'] == 'FIFA World Cup') & 
            (competitions['season_name'] == '2022')
        ]
        
        if not wc_2022.empty:
            competition_id = wc_2022.iloc[0]['competition_id']
            season_id = wc_2022.iloc[0]['season_id']
            matches = sb.matches(competition_id=competition_id, season_id=season_id)
            return matches, True
    except Exception as e:
        st.warning(f"Error loading StatsBomb data: {e}")
    
    return None, False


def render_match_analysis_block(block_id, block_number, matches_df, is_real_data):
    """Render a single match analysis block"""
    
    # Header with delete button
    col_header, col_delete = st.columns([10, 1])
    
    with col_header:
        st.subheader(f"Match Analysis {block_number}")
    
    with col_delete:
        # Delete button (disabled if only one block)
        disabled = (len(st.session_state["match_blocks"]) == 1)
        if st.button("❌", key=f"delete_match_{block_id}", disabled=disabled):
            if block_id in st.session_state["match_blocks"]:
                st.session_state["match_blocks"].remove(block_id)
            st.rerun()
    
    # Stage filter
    selected_stage = st.selectbox(
        "Filter by tournament stage", 
        stages, 
        key=f"stage_{block_id}"
    )
    
    # Filter matches by stage
    if selected_stage != 'All Stages':
        filtered_matches = matches_df[matches_df['competition_stage'] == selected_stage]
    else:
        filtered_matches = matches_df
    
    st.markdown(
        f'<p class="stage-header">🔍 {selected_stage}: {len(filtered_matches)} matches available</p>', 
        unsafe_allow_html=True
    )
    
    if not filtered_matches.empty:
        match_options = filtered_matches.apply(
            lambda x: f"{x['home_team']} vs {x['away_team']} ({x['match_date']}) - {x['competition_stage']}", 
            axis=1
        ).tolist()
        
        selected_match = st.selectbox(
            "Select a Match", 
            match_options, 
            key=f"match_{block_id}"
        )
        
        if selected_match:
            match_idx = match_options.index(selected_match)
            match_info = filtered_matches.iloc[match_idx]
            
            # Match info display
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Home Team", match_info['home_team'])
            with col2:
                st.metric("Away Team", match_info['away_team'])
            with col3:
                st.metric("Score", f"{match_info['home_score']} - {match_info['away_score']}")
            with col4:
                st.metric("Stage", match_info['competition_stage'])
            
            # Styled radio button
            st.markdown("""
                <style>
                div[data-testid="stRadio"] {
                    background-color: #FFE4B5;
                    padding: 15px;
                    border-radius: 10px;
                    border: 1px solid #ddd;
                    margin-bottom: 20px;
                }
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
            
            # Load match events
            events_df = load_match_events(match_info['match_id'], is_real_data)
            
            # ---------------------- BASIC ANALYSIS ---------------------- #
            if analysis_section == "📈 Basic Analysis":
                load_basic_analysis(match_id=match_info['match_id'], match_or_team="Match")
                
            elif analysis_section == "🎯 Shot Analysis":
                st.subheader("Shot Analysis & Expected Goals")
                fig, outcomes_ = create_shot_map(events_df)
                st.plotly_chart(fig, use_container_width=True, key=f"{match_info['match_id']}_{random.randint(0,9999)}")

                
                col1, col2, col3 = st.columns(3)
                
                home_team_ = events_df['team'].unique()[0]
                away_team_ = events_df['team'].unique()[1]
                home_shot_outcomes = outcomes_[home_team_]
                away_shot_outcomes = outcomes_[away_team_]
                
                if len(home_shot_outcomes.keys()) > len(away_shot_outcomes.keys()):
                    for key in home_shot_outcomes.keys():
                        if key not in away_shot_outcomes:
                            away_shot_outcomes[key] = 0
                elif len(home_shot_outcomes.keys()) < len(away_shot_outcomes.keys()):
                    for key in away_shot_outcomes.keys():
                        if key not in home_shot_outcomes:
                            home_shot_outcomes[key] = 0
                            
                with col1:
                    st.subheader(f"{home_team_} Team Shots")
                    for val in home_shot_outcomes.values():
                        st.markdown(val)
                    filtered_home = {k: v for k, v in outcomes_[home_team_].items() if k != "All Shots"}
                    fig_home = px.pie(
                        values=filtered_home.values(),
                        names=filtered_home.keys(),
                        title=f"{home_team_} Shot Outcomes",
                        color_discrete_sequence=['blue', 'lightblue', 'navy', 'darkblue']
                    )
                    st.plotly_chart(fig_home, use_container_width=True)
                                
                with col2:
                    st.subheader("Shot Outcomes")
                    for val in home_shot_outcomes.keys():
                        st.markdown(val)
                    
                with col3:
                    st.subheader(f"{away_team_} Team Shots")
                    for val in away_shot_outcomes.values():
                        st.markdown(val)
                    filtered_away = {k: v for k, v in outcomes_[away_team_].items() if k != "All Shots"}
                    fig_away = px.pie(
                        values=filtered_away.values(),
                        names=filtered_away.keys(),
                        title=f"{away_team_} Shot Outcomes",
                        color_discrete_sequence=['red', 'lightcoral', 'darkred', 'maroon']
                    )
                    st.plotly_chart(fig_away, use_container_width=True)
    
    st.divider()


def main():
    # Initialize blocks and next id counter
    if "match_blocks" not in st.session_state:
        st.session_state["match_blocks"] = [1]
    if "next_match_block_id" not in st.session_state:
        st.session_state["next_match_block_id"] = max(st.session_state["match_blocks"]) + 1
    
    data = load_data()
    
    # Title and Add button
    col_title, col_add = st.columns([10, 1])
    with col_title:
        st.title("⚽ Match Analysis - World Cup 2022")
    with col_add:
        add_disabled = len(st.session_state["match_blocks"]) >= 4  # Max 4 analyses
        if st.button("➕", help="Add new match analysis", disabled=add_disabled):
            new_id = st.session_state["next_match_block_id"]
            st.session_state["match_blocks"].append(new_id)
            st.session_state["next_match_block_id"] += 1
            st.rerun()
    
    st.header("📊 Match Analysis")
    
    # Load data
    matches_df, is_real_data = load_world_cup_data()
    
    if matches_df is None or matches_df.empty:
        st.error("No match data available. Please check your data source.")
        return
    
    # Display blocks
    blocks = st.session_state["match_blocks"]
    
    if len(blocks) == 1:
        render_match_analysis_block(blocks[0], 1, matches_df, is_real_data)
    else:
        for row_start in range(0, len(blocks), MAX_COLUMNS):
            row_blocks = blocks[row_start: row_start + MAX_COLUMNS]
            cols = st.columns(len(row_blocks))
            for i, block_id in enumerate(row_blocks):
                with cols[i]:
                    render_match_analysis_block(
                        block_id, 
                        row_start + i + 1, 
                        matches_df, 
                        is_real_data
                    )


if __name__ == "__main__":
    main()
