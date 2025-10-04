import streamlit as st
from Match_tabs.Base import create_set_piece_analysis
import pandas as pd
import plotly.express as px

def Set_piece(events_df):
    st.subheader("Set Piece Analysis")
    st.plotly_chart(create_set_piece_analysis(events_df), use_container_width=True)

    # --- Extract Corners ---
    corners = events_df[
        (events_df["type"] == "Pass") & 
        (events_df["pass_type"] == "Corner")
    ].copy()
    corners["set_piece_type"] = "Corner"

    # --- Extract Free Kicks (Passes & Shots after free kick restart) ---
    free_kicks = events_df[
        (events_df["play_pattern"] == "From Free Kick") &
        (events_df["type"].isin(["Pass", "Shot"]))
    ].copy()
    free_kicks["set_piece_type"] = "Free Kick"

    # --- Extract Fouls (committed) ---
    fouls = events_df[events_df["type"] == "Foul Committed"].copy()
    fouls["set_piece_type"] = "Foul Committed"

    # --- Combine ---
    set_pieces = pd.concat([corners, free_kicks, fouls], ignore_index=True)

    if set_pieces.empty:
        st.info("No set piece data available for this match.")
        return

    # --- Layout ---
    col1, col2 = st.columns(2)

    with col1:
        sp_by_team = set_pieces.groupby(['team', 'set_piece_type']).size().unstack(fill_value=0)
        fig_sp = px.bar(
            sp_by_team,
            title="Set Pieces by Team (Corners, Free Kicks, Fouls)",
            barmode="group"
        )
        st.plotly_chart(fig_sp, use_container_width=True)

    with col2:
        # Only Corners & Free Kicks have outcomes
        sp_outcomes = set_pieces[
            set_pieces["set_piece_type"].isin(["Corner", "Free Kick"])
        ]["outcome"].dropna().value_counts()

        if not sp_outcomes.empty:
            fig_outcomes = px.pie(
                values=sp_outcomes.values,
                names=sp_outcomes.index,
                title="Set Piece Outcomes"
            )
            st.plotly_chart(fig_outcomes, use_container_width=True)
        else:
            st.info("No outcome data for Corners or Free Kicks.")
