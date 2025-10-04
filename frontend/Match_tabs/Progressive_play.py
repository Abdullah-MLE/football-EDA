import streamlit as st
import pandas as pd
from Match_tabs.Base import create_progressive_passes
import numpy as np
import plotly.express as px


def progressive_play(events_df):
    st.subheader("Progressive Play Analysis")
    st.plotly_chart(create_progressive_passes(events_df), use_container_width=True)

    # Progressive pass statistics
    prog_passes = events_df[
        (events_df['type'] == 'Pass') & 
        (events_df['progressive'] == True)
    ]
    
    if not prog_passes.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            prog_by_team = prog_passes.groupby('team').size()
            fig_prog = px.bar(x=prog_by_team.index, y=prog_by_team.values,
                            title="Progressive Passes by Team",
                            color=prog_by_team.index,
                            color_discrete_map={'Home': 'blue', 'Away': 'red'})
            st.plotly_chart(fig_prog, use_container_width=True)
        
        with col2:
            prog_success = prog_passes.groupby('outcome').size()
            fig_success = px.pie(values=prog_success.values, names=prog_success.index,
                                title="Progressive Pass Success Rate")
            st.plotly_chart(fig_success, use_container_width=True)
