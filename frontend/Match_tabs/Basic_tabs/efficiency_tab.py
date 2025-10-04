import streamlit as st
from Match_tabs.Basic_tabs.basic_tab import BaseTab


class EfficiencyTab(BaseTab):
    def __init__(self):
        # data = load_data()
        super().__init__("efficiency")
    
    def add_custom_plot(self):
        pass


# def load_efficiency_tab():
#     st.markdown(f"## {tabs_have['Efficiency & Outcome']} Efficiency Analysis")
#     col1, col2,col3 = st.columns(3)
#     data = load_data()["efficiency"]
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

