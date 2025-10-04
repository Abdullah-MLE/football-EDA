import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pages.data import load_data, tabs_have, home_team, away_team
from Match_tabs.Basic_tabs.attack_tab import AttackTab
from Match_tabs.Basic_tabs.defensive_tab import DefensiveTab
from Match_tabs.Basic_tabs.efficiency_tab import EfficiencyTab
from Match_tabs.Basic_tabs.transition_tab import TransitionTab
from Match_tabs.Basic_tabs.goalkeeper_tab import GoalkeeperTab
from Match_tabs.Basic_tabs.pass_analysis import PassTab

def load_basic_analysis(match_id=None,team1=None,team2=None,match_or_team="Match"):
    st.subheader("Basic Match Analysis")
    poss_tab,attack_tab,defense_tab,trans_tabs,keeper_tab,outcome_tab =st.tabs(tabs_have.keys())
    
    with poss_tab:
        PassTab().render(match_id=match_id,team1=team1,team2=team2,Match_or_team=match_or_team)
    with attack_tab:
        AttackTab().render(match_id=match_id,team1=team1,team2=team2,Match_or_team=match_or_team)
    with defense_tab:
        DefensiveTab().render(match_id=match_id,team1=team1,team2=team2,Match_or_team=match_or_team)
    with trans_tabs:
        TransitionTab().render(match_id=match_id,team1=team1,team2=team2,Match_or_team=match_or_team)
    with keeper_tab:
        GoalkeeperTab().render(match_id=match_id,team1=team1,team2=team2,Match_or_team=match_or_team)
    with outcome_tab:
        EfficiencyTab().render(match_id=match_id,team1=team1,team2=team2,Match_or_team=match_or_team)



# st.header(f"{tabs_have['Defensive Metrics']} defensive Analysis")
# col1, col2 = st.columns(2)
# with col1:
#     st.subheader("Defensive Actions")
#     defense_df = pd.DataFrame({
#         'Metric': ['Tackles', 'Interceptions', 'Clearances', 'Blocks', 'Aerial Duels Won', 'Fouls Committed', 'Yellow Cards', 'Red Cards'],
#         home_team: [
#             data['defensive']['home_team']['tackles'],
#             data['defensive']['home_team']['interceptions'],
#             data['defensive']['home_team']['clearances'],
#             data['defensive']['home_team']['blocks'],
#             data['defensive']['home_team']['aerial_duels_won'],
#             data['defensive']['home_team']['fouls_committed'],
#             data['defensive']['home_team']['yellow_cards'],
#             data['defensive']['home_team']['red_cards']
#         ],
#         away_team: [
#             data['defensive']['away_team']['tackles'],
#             data['defensive']['away_team']['interceptions'],
#             data['defensive']['away_team']['clearances'],
#             data['defensive']['away_team']['blocks'],
#             data['defensive']['away_team']['aerial_duels_won'],
#             data['defensive']['away_team']['fouls_committed'],
#             data['defensive']['away_team']['yellow_cards'],
#             data['defensive']['away_team']['red_cards']
#         ]
#     })
#     st.dataframe(defense_df)

#     fig = px.bar(defense_df, x='Metric', y=[home_team, away_team], barmode='group', title='Defensive Metrics Comparison')
#     st.plotly_chart(fig, use_container_width=True)

# with col2:
#     st.subheader("Goalkeeper Stats")
#     gk_df = pd.DataFrame({
#         'Metric': ['Saves', 'Save Percentage', 'Clean Sheets', 'Goals Conceded', 'Punches', 'Catches', 'Distribution Accuracy %'],
#         home_team: [
#             data['goalkeeping']['home_team']['saves'],
#             data['goalkeeping']['home_team']['save_percentage'],
#             data['goalkeeping']['home_team']['clean_sheets'],
#             data['goalkeeping']['home_team']['goals_conceded'],
#             data['goalkeeping']['home_team']['punches'],
#             data['goalkeeping']['home_team']['catches'],
#             data['goalkeeping']['home_team']['distribution_accuracy']
#         ],
#         away_team: [
#             data['goalkeeping']['away_team']['saves'],
#             data['goalkeeping']['away_team']['save_percentage'],
#             data['goalkeeping']['away_team']['clean_sheets'],
#             data['goalkeeping']['away_team']['goals_conceded'],
#             data['goalkeeping']['away_team']['punches'],
#             data['goalkeeping']['away_team']['catches'],
#             data['goalkeeping']['away_team']['distribution_accuracy']
#         ]
#     }
#     )