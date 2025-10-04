import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pages.data import tabs_have,icon_logo,home_team, away_team
import random

# Passing
passing_cols = [
    "possession_%"
    "total_passes",
    "completed_passes",
    "passing_accuracy",
    "progressive_passes",
    "final_third_passes",
    "penalty_area_passes",
    "crosses_attempted",
    "crosses_completed",
    "cross_success_rate"
]

# Attacking
attacking_cols = [
    "total_shots",
    "shots_on_target",
    "shots_blocked",
    "shots_off_target",
    "xg",
    "avg_xg_per_shot",
    "key_passes",
    "dribbles_attempted",
    "dribbles_successful",
    "dribble_success_rate",
    "touches_in_box",
    "set_piece_chances"
]

# Defensive
defensive_cols = [
    "pressures",
    "high_pressures",
    "tackles",
    "interceptions",
    "ball_recoveries",
    "blocks",
    "clearances",
    "xga",
    "pressing_success",
    "aerial_duels_won",
    "fouls_committed",
    "yellow_cards",
    "red_cards"
]

# Goalkeeper
goalkeeper_cols = [
    "saves",
    "shots_faced",
    "goals_conceded",
    "clean_sheets",
    "goals_prevented",
    "post_shot_xg_conceded",
    "psxg_plus_minus",
    "sweeper_actions"
]

# Transition
transition_cols = [
    "counter_attacks",
    "counter_attack_shots",
    "turnovers_to_shots",
    "avg_attack_speed",
    "press_to_attack_conversion"
]

# Efficiency
efficiency_cols = [
    "goals_scored",
    "goals_conceded",
    "conversion_rate",
    "xg_vs_goals_diff",
    "xga_vs_conceded_diff"
]

def get_match_events(match_id=None,columns=None,Match_or_team="Match",team1=None,team2=None):
    """
    For Match Data:
        Load match events from a CSV file based on match_id.
    For Team Comparison:
        Load team data from a CSV file based on team names.
    """
    df_ = None
    try:
        if Match_or_team =="Match":
            csv_file = './data/worldcup_2022_match_data.csv'
            df = pd.read_csv(csv_file, usecols=columns+['match_id', 'team_name', 'opponent_name'])
            df_ = df[df['match_id'] == match_id]
        elif Match_or_team =="Team":
            csv_file = './data/Team_comparison.csv'
            team1_df = pd.read_csv(csv_file, usecols=columns+['match_id', 'team_name'])
            team2_df = pd.read_csv(csv_file, usecols=columns+['match_id', 'team_name'])
            df_ = pd.concat([team1_df[team1_df['team_name'] == team1], team2_df[team2_df['team_name'] == team2]])
    except FileNotFoundError:
        print("File Not Found on the specified path.")
    except Exception as e:
        print("#-#"*10)
        print(f"An error occurred: {e}")
    
    return df_

def get_columns_by_prefix(prefix):
    """
    Return all column names from a CSV file that start with the given prefix.
    """
    csv_file = './data/worldcup_2022_match_data.csv'
    df = pd.read_csv(csv_file)
    cols = [col for col in df.columns if col.startswith(prefix)]
    return cols

class BaseTab:
    def __init__(self,name):
        """Initialize the tab with a name and data.
        Args:
            name (str): The name of the tab.
            home_team (str): Name of the home team.
            away_team (str): Name of the away team.
            data (dict): The data for the tab.
        """
        self.name = name
        self.data = None
        self.home_team = home_team
        self.away_team = away_team
    
    def clean_columns(self,cols, prefix):
        """
        Remove prefix and replace underscores with spaces.
        Example:
        'passing_total_passes' -> 'Total Passes'
        """
        cleaned = []
        for col in cols:
            if col.startswith(prefix):
                new_col = col[len(prefix):]  # remove prefix
            else:
                new_col = col
            new_col = new_col.replace("_", " ").title()  # e.g. total_passes -> Total Passes
            cleaned.append(new_col)
        return cleaned


    def load_data(self, metrics, match_id,Match_or_team="Match",team1=None,team2=None):
        """Load Match data from StatsBomb from Csv file (worldcup_2022_match_data.csv)."""
        # get original prefixed columns
        columns = get_columns_by_prefix(metrics)

        # read data
        match_data = get_match_events(match_id,columns=columns,Match_or_team=Match_or_team,team1=team1,team2=team2)
        if match_data.empty:
            raise ValueError(f"No data found for match_id {match_id}")

        if len(match_data) < 2:
            raise ValueError(f"Expected 2 rows (home & away) for match_id {match_id}, but got {len(match_data)}")

        # filter by position, not index label
        self.home_team = match_data.iloc[0]['team_name']
        self.away_team = match_data.iloc[1]['team_name']
        home_team_df = match_data.iloc[[0]]
        away_team_df = match_data.iloc[[1]]
   
        if match_data.empty:
            raise ValueError(f"No data found for match_id {match_id}")

        # drop metadata columns
        if Match_or_team =="Match":
            home_team_df = home_team_df.drop(columns=["match_id", "team_name", "opponent_name"])
            away_team_df = away_team_df.drop(columns=["match_id", "team_name", "opponent_name"])
        elif Match_or_team =="Team":
            home_team_df = home_team_df.drop(columns=["match_id", "team_name"])
            away_team_df = away_team_df.drop(columns=["match_id", "team_name"])
            # make round values to 2 decimals
            home_team_df = home_team_df.round(2)
            away_team_df = away_team_df.round(2)
        # clean column names
        cleaned_cols = self.clean_columns(home_team_df.columns, metrics)
        home_team_df.columns = cleaned_cols
        away_team_df.columns = cleaned_cols

        # save in dict
        self.data = {
            "home_team": home_team_df.squeeze().to_dict(),
            "away_team": away_team_df.squeeze().to_dict(),
        }


    def display_header(self):
        st.markdown(f"## {icon_logo[self.name][0]} {icon_logo[self.name][1]} Analysis")
    
    def display_stats(self):
        col1, col2, col3 = st.columns(3)

        # Home team column
        with col1:
            st.markdown(f'<div class="team-header home-header">🏠 {self.home_team}</div>', unsafe_allow_html=True)
            for _, value in self.data["home_team"].items():
                st.markdown(f"{value}")

        # Stats column
        with col2:
            st.markdown('<div class="team-header" style="background: linear-gradient(135deg, #34495E, #2C3E50); color: white;">📊 Statistics</div>', unsafe_allow_html=True)
            for stats, _ in self.data["home_team"].items():
                st.markdown(f"{stats}")

        # Away team column
        with col3:
            st.markdown(f'<div class="team-header away-header">✈️ {self.away_team}</div>', unsafe_allow_html=True)
            for _, value in self.data["away_team"].items():
                st.markdown(f"{value}")

    def render_plot(self):
        metrics = list(self.data['home_team'].keys())
        home_values = [self.data['home_team'][m] for m in metrics]
        away_values = [self.data['away_team'][m] for m in metrics]

        fig = go.Figure(data=[
            go.Bar(name=self.home_team, x=metrics, y=home_values, marker_color='blue'),
            go.Bar(name=self.away_team, x=metrics, y=away_values, marker_color='red')
        ])

        fig.update_layout(
            barmode='group',
            title="Team Efficiency & Outcome Comparison",
            xaxis_title="Metrics",
            yaxis_title="Value",
            legend_title="Team",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True, key=f"{random.randint(0,9999)}")
    
    def add_custom_plot(self):
        pass

    def render(self,match_id=None,team1=None,team2=None,Match_or_team="Match"):
        
        self.load_data(self.name, match_id=match_id,Match_or_team=Match_or_team,team1=team1,team2=team2)
        self.display_header()
        self.display_stats()
        self.render_plot()
        self.add_custom_plot()
