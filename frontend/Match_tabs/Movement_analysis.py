import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pages.data import load_data, tabs_have, home_team, away_team
from Match_tabs.Base import create_player_heatmap


def Movement_analysis(events_df):
    """Analyze player movement and create heatmaps"""
    st.subheader("Player Movement & Heat Maps")

    # Player selection for heatmap
    all_players = events_df['player'].unique().tolist() if not events_df.empty else []
    if all_players:
        selected_heatmap_player = st.selectbox("Select Player for Heatmap", all_players)
        st.plotly_chart(create_player_heatmap(events_df, selected_heatmap_player), use_container_width=True)
        
        # Player activity summary
        player_events = events_df[events_df['player'] == selected_heatmap_player]
        Movement_dict = {}
        if not player_events.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Events", len(player_events))
                Movement_dict["Total Events"] =len(player_events)
            with col2:
                passes = len(player_events[player_events['type'] == 'Pass'])
                Movement_dict["Passes"] = passes
                st.metric("Passes", passes)
            with col3:
                shots = len(player_events[player_events['type'] == 'Shot'])
                Movement_dict["Shots"] = shots
                st.metric("Shots", shots)
            with col4:
                dribbles = len(player_events[player_events['type'] == 'Dribble'])
                Movement_dict["Dribbles"] = dribbles
                st.metric("Dribbles", dribbles)
        print("===============================")
        print("Movement summary:", Movement_dict)
        print("===============================")
    else:
        st.info("No player data available for heatmap")
