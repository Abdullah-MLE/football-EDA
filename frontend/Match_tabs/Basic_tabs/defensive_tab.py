import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from Match_tabs.Basic_tabs.basic_tab import BaseTab


class DefensiveTab(BaseTab):
    def __init__(self):
        # data = load_data()
        super().__init__("defensive")
    
    def add_custom_plot(self):
        pass
        #st.image("./shot_img.png", caption="Shot Map Example", use_column_width=True)

# def load_defensive_tab():
#     st.markdown(f"## {tabs_have['Attacking Metrics']} Attacking Analysis")
#     col1, col2,col3 = st.columns(3)
#     data = load_data()["defensive"]
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


