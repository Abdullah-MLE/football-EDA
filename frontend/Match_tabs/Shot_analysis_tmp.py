import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from Match_tabs.Base import create_football_pitch_bg


def load_json_shot_data(json_path):
    """Load and flatten shot data from JSON file into a DataFrame"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_shots = []
    for team in data.get("teams", []):
        team_name = team["team_name"]
        for match in team.get("matches", []):
            match_info = match["match_info"]
            for shot in match.get("shots", []):
                all_shots.append({
                    "match": f"{match_info['home_team']} vs {match_info['away_team']}",
                    "date": match_info.get("date"),
                    "team": shot.get("team", team_name),
                    "player": shot.get("player"),
                    "minute": shot.get("minute"),
                    "second": shot.get("second"),
                    "x": shot["position"]["x"],
                    "y": shot["position"]["y"],
                    "xG": shot.get("xG", 0),
                    "outcome": shot.get("outcome"),
                    "shot_type": shot.get("shot_type"),
                    "body_part": shot.get("body_part"),
                    "under_pressure": shot.get("under_pressure", False),
                    "from_counter": shot.get("from_counter", False),
                })

    return pd.DataFrame(all_shots)


def create_shot_map(events_df):
    """Create shot map with xG values and return outcomes"""
    if events_df.empty or "xG" not in events_df.columns:
        fig = create_football_pitch_bg()
        fig.add_annotation(
            text="No shot data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig, {}

    pitch_length, pitch_width = 120, 80
    teams = events_df["team"].unique()

    fig = create_football_pitch_bg()
    outcomes_ = {}

    # Add shots with different shapes for outcomes
    for team, color in zip(teams, ["blue", "red"]):
        team_shots = events_df[events_df["team"] == team]

        # Build outcomes dict for this team
        outcomes_[team] = (
            team_shots["outcome"].value_counts().to_dict()
            | {"All Shots": len(team_shots)}
        )

        for outcome, symbol in [
            ("Goal", "star"),
            ("Saved", "circle"),
            ("Off T", "x"),
            ("Blocked", "square"),
        ]:
            outcome_shots = team_shots[team_shots["outcome"] == outcome]
            if not outcome_shots.empty:
                fig.add_trace(go.Scatter(
                    x=outcome_shots["x"], y=outcome_shots["y"],
                    mode="markers",
                    marker=dict(
                        size=outcome_shots["xG"].fillna(0.1) * 30 + 10,
                        color=color,
                        opacity=0.8,
                        symbol=symbol,
                        line=dict(width=2, color="white")
                    ),
                    name=f"{team} {outcome}",
                    text=outcome_shots.apply(
                        lambda row: f"Player: {row['player']}<br>xG: {row['xG']:.2f}<br>Outcome: {row['outcome']}", axis=1
                    ),
                    hovertemplate="<b>%{text}</b><extra></extra>"
                ))

    fig.update_layout(
        title="Shot Map with xG Values & Outcomes",
        height=500,
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1,
            orientation="v",
            font=dict(size=12)
        ),
        showlegend=True
    )
    return fig, outcomes_
