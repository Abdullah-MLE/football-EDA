import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pages.data import load_data, tabs_have, home_team, away_team
from Match_tabs.Basic_tabs.basic_tab import BaseTab
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from Match_tabs.Basic_tabs.plot_tmp import draw_pitch_plot

try:
    from statsbombpy import sb
    STATSBOMB_AVAILABLE = True
except ImportError:
    STATSBOMB_AVAILABLE = False
    st.warning("StatsBombPy not available. Using mock data for demonstration.")


class AttackTab(BaseTab):
    def __init__(self):
        # data = load_data()
        super().__init__("attacking")
    
    def add_custom_plot(self):
        pass

# def load_attack_tab():
#     st.markdown(f"## {tabs_have['Attacking Metrics']} Attacking Analysis")
#     col1, col2 = st.columns(2)
#     data = load_data()
#     with col1:
#         st.markdown("home_team")
#         home_df = pd.DataFrame({
#             'Metric': ['Total Shots', 'Shots on Target', 'Shots Blocked', 'Shots off Target', 'xG', 'Avg xG per Shot', 'Key Passes', 'Dribbles Attempted', 'Dribbles Successful', 'Dribble Success Rate %', 'Touches in Box', 'Set Piece Chances'],
#             'Value': [
#                 data['attacking']['home_team']['total_shots'],
#                 data['attacking']['home_team']['shots_on_target'],
#                 data['attacking']['home_team']['shots_blocked'],
#                 data['attacking']['home_team']['shots_off_target'],
#                 data['attacking']['home_team']['xg'],
#                 data['attacking']['home_team']['avg_xg_per_shot'],
#                 data['attacking']['home_team']['key_passes'],
#                 data['attacking']['home_team']['dribbles_attempted'],
#                 data['attacking']['home_team']['dribbles_successful'],
#                 data['attacking']['home_team']['dribble_success_rate'],
#                 data['attacking']['home_team']['touches_in_box'],
#                 data['attacking']['home_team']['set_piece_chances']
#             ]
#         })
#         st.dataframe(home_df)
#         fig = px.bar(home_df, x='Metric', y='Value', title=f'{home_team} Shooting Metrics')
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         st.markdown(f"{away_team}")
#         away_df = pd.DataFrame({
#             'Metric': ['Total Shots', 'Shots on Target', 'Shots Blocked', 'Shots off Target', 'xG', 'Avg xG per Shot', 'Key Passes', 'Dribbles Attempted', 'Dribbles Successful', 'Dribble Success Rate %', 'Touches in Box', 'Set Piece Chances'],
#             'Value': [
#                 data['attacking']['away_team']['total_shots'],
#                 data['attacking']['away_team']['shots_on_target'],
#                 data['attacking']['away_team']['shots_blocked'],
#                 data['attacking']['away_team']['shots_off_target'],
#                 data['attacking']['away_team']['xg'],
#                 data['attacking']['away_team']['avg_xg_per_shot'],
#                 data['attacking']['away_team']['key_passes'],
#                 data['attacking']['away_team']['dribbles_attempted'],
#                 data['attacking']['away_team']['dribbles_successful'],
#                 data['attacking']['away_team']['dribble_success_rate'],
#                 data['attacking']['away_team']['touches_in_box'],
#                 data['attacking']['away_team']['set_piece_chances']
#             ]
#         })
#         st.dataframe(away_df)
#         fig = px.bar(away_df, x='Metric', y='Value', title=f'{away_team} Shooting Metrics')
#         st.plotly_chart(fig, use_container_width=True)

# def load_attack_tab_():
#     st.markdown(f"## {tabs_have['Attacking Metrics']} Attacking Analysis")
#     col1, col2,col3 = st.columns(3)
#     data = load_data()["attacking"]
#     with col1:
#         st.markdown(f'<div class="team-header home-header">🏠 {home_team}</div>', unsafe_allow_html=True)
#         for _, value in data['home_team'].items():
#             st.markdown(f"{value}")

#     with col2:
#         st.markdown('<div class="team-header" style="background: linear-gradient(135deg, #34495E, #2C3E50); color: white;">📊 Statistics</div>', unsafe_allow_html=True)
#         for stats, value in data['home_team'].items():
#             st.markdown(f"{stats}")

#     with col3:
#         st.markdown(f'<div class="team-header away-header">✈️ {away_team}</div>', unsafe_allow_html=True)
#         for _, value in data['away_team'].items():
#             st.markdown(f"{value}")

