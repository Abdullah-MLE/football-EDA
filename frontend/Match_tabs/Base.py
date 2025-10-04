import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go



try:
    from statsbombpy import sb
    STATSBOMB_AVAILABLE = True
except ImportError:
    STATSBOMB_AVAILABLE = False
    st.warning("StatsBombPy not available. Using mock data for demonstration.")


@st.cache_data
def load_match_events(match_id, is_real_data=False):
    """Load events for a specific match"""
    if is_real_data:
        try:
            events = sb.events(match_id=match_id)
            return preprocess_statsbomb_events(events)
        except Exception as e:
            st.warning(f"Error loading match events: {e}")
    df = pd.read_csv("processed_events.csv")
    return df
    # Mock events data
    return create_mock_events_data()


def create_player_heatmap(events_df, selected_player):
    """Create player movement heatmap"""
    if events_df.empty:
        fig = create_football_pitch_bg()
        fig.add_annotation(text="No player data available", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    player_events = events_df[events_df['player'] == selected_player]
    if player_events.empty:
        fig = create_football_pitch_bg()
        fig.add_annotation(text=f"No data for {selected_player}", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = create_football_pitch_bg()
    
    # Create heatmap using hexbin-style visualization
    fig.add_trace(go.Histogram2d(
        x=player_events['x'],
        y=player_events['y'],
        colorscale='Reds',
        opacity=0.7,
        nbinsx=20,
        nbinsy=15,
        name='Activity Density'
    ))
    
    fig.update_layout(title=f"Player Movement Heatmap - {selected_player}", height=500)
    return fig

def create_progressive_passes(events_df):
    """Create progressive passing analysis"""
    if events_df.empty:
        fig = create_football_pitch_bg()
        fig.add_annotation(text="No pass data available", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    passes_df = events_df[
        (events_df['type'] == 'Pass') & 
        (events_df['progressive'] == True) &
        (events_df['outcome'] == 'Complete')
    ].copy()
    
    if passes_df.empty:
        fig = create_football_pitch_bg()
        fig.add_annotation(text="No progressive passes found", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = create_football_pitch_bg()
    
    # Add progressive passes as arrows
    for team, color in [('Home', 'blue'), ('Away', 'red')]:
        team_passes = passes_df[passes_df['team'] == team]
        if not team_passes.empty:
            for _, pass_event in team_passes.iterrows():
                fig.add_annotation(
                    x=pass_event['end_x'] if pass_event['end_x'] else pass_event['x'] + 10,
                    y=pass_event['end_y'] if pass_event['end_y'] else pass_event['y'],
                    ax=pass_event['x'],
                    ay=pass_event['y'],
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=2,
                    arrowcolor=color,
                    opacity=0.7
                )
    
    fig.update_layout(title="Progressive Passing Analysis", height=500)
    return fig

def create_set_piece_analysis(events_df):
    """Create set piece analysis visualization"""
    if events_df.empty:
        fig = create_football_pitch_bg()
        fig.add_annotation(
            text="No set piece data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    # --- Extract Corners ---
    corners = events_df[
        (events_df["type"] == "Pass") &
        (events_df["pass_type"] == "Corner")
    ].copy()
    corners["set_piece_type"] = "Corner"

    # --- Extract Free Kicks (≈ fouls won) ---
    free_kicks = events_df[events_df["type"] == "Foul Won"].copy()
    free_kicks["set_piece_type"] = "Free Kick"

    # --- Extract Fouls (committed) ---
    fouls_committed = events_df[events_df["type"] == "Foul Committed"].copy()
    fouls_committed["set_piece_type"] = "Foul Committed"

    # --- Combine ---
    set_pieces = pd.concat([corners, free_kicks, fouls_committed], ignore_index=True)

    print(f"Corners: {len(corners)}, Free Kicks: {len(free_kicks)}, Fouls: {len(fouls_committed)}")
    print("Set pieces df shape:", set_pieces.shape)

    if set_pieces.empty:
        fig = create_football_pitch_bg()
        fig.add_annotation(
            text="No set pieces in this match",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    fig = create_football_pitch_bg()

    # Define plotting style
    plot_map = {
        "Corner": {"symbol": "triangle-up"},
        "Free Kick": {"symbol": "diamond"},
        "Foul Committed": {"symbol": "circle"}
    }

    teams = events_df["team"].dropna().unique()
    colors = {teams[0]: "blue", teams[1]: "red"} if len(teams) >= 2 else {}

    # Add set pieces
    for team, color in colors.items():
        team_set_pieces = set_pieces[set_pieces["team"] == team]

        for sp_type, style in plot_map.items():
            sp_events = team_set_pieces[team_set_pieces["set_piece_type"] == sp_type]
            if not sp_events.empty:
                fig.add_trace(go.Scatter(
                    x=sp_events["x"], y=sp_events["y"],
                    mode="markers",
                    marker=dict(
                        size=15,
                        color=color,
                        symbol=style["symbol"],
                        line=dict(width=2, color="white")
                    ),
                    name=f"{team} {sp_type}",
                    text=sp_events.apply(
                        lambda row: f"Player: {row['player']}<br>Type: {row['set_piece_type']}<br>Outcome: {row.get('outcome', 'N/A')}",
                        axis=1
                    ),
                    hovertemplate="<b>%{text}</b><extra></extra>"
                ))

    fig.update_layout(title="Set Piece Analysis", height=500)
    fig.update_layout(
        height=500,
        legend=dict(
            x=0.01,   # push legend to left
            y=0.99,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1,
            orientation="v",  # vertical layout
            font=dict(size=12)
        ),
        showlegend=True   # force legend to appear
    )
    return fig


def create_tactical_analysis(events_df):
    """Create advanced tactical analysis"""
    if events_df.empty:
        return go.Figure().add_annotation(text="No tactical data available", 
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    # Calculate tactical metrics
    home_events = events_df[events_df['team'] == 'Home']
    away_events = events_df[events_df['team'] == 'Away']
    
    metrics = {}
    
    # Possession
    total_events = len(events_df)
    metrics['Home Possession %'] = len(home_events) / total_events * 100 if total_events > 0 else 0
    metrics['Away Possession %'] = len(away_events) / total_events * 100 if total_events > 0 else 0
    
    # Pass accuracy
    home_passes = home_events[home_events['type'] == 'Pass']
    away_passes = away_events[away_events['type'] == 'Pass']
    
    metrics['Home Pass Accuracy %'] = len(home_passes[home_passes['outcome'] == 'Complete']) / len(home_passes) * 100 if len(home_passes) > 0 else 0
    metrics['Away Pass Accuracy %'] = len(away_passes[away_passes['outcome'] == 'Complete']) / len(away_passes) * 100 if len(away_passes) > 0 else 0
    
    # Pressure events
    metrics['Home Pressure Events'] = len(home_events[home_events['pressure'] == True])
    metrics['Away Pressure Events'] = len(away_events[away_events['pressure'] == True])
    
    # Create comparison chart
    fig = go.Figure()
    
    categories = ['Possession %', 'Pass Accuracy %', 'Pressure Events']
    home_values = [metrics['Home Possession %'], metrics['Home Pass Accuracy %'], metrics['Home Pressure Events']]
    away_values = [metrics['Away Possession %'], metrics['Away Pass Accuracy %'], metrics['Away Pressure Events']]
    
    fig.add_trace(go.Scatterpolar(
        r=home_values,
        theta=categories,
        fill='toself',
        name='Home Team',
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=away_values,
        theta=categories,
        fill='toself',
        name='Away Team',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        title="Advanced Tactical Analysis",
        height=500
    )
    
    return fig



def preprocess_statsbomb_events(events: pd.DataFrame) -> pd.DataFrame:
    """Convert StatsBomb events to the schema expected by the app."""
    df = events.copy()

    # Extract location (start position)
    if 'location' in df.columns:
        df['x'] = df['location'].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
        df['y'] = df['location'].apply(lambda loc: loc[1] if isinstance(loc, list) else None)

    # Extract end location for passes and carries
    if 'pass_end_location' in df.columns:
        df['end_x'] = df['pass_end_location'].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
        df['end_y'] = df['pass_end_location'].apply(lambda loc: loc[1] if isinstance(loc, list) else None)
    elif 'carry_end_location' in df.columns:
        df['end_x'] = df['carry_end_location'].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
        df['end_y'] = df['carry_end_location'].apply(lambda loc: loc[1] if isinstance(loc, list) else None)

    # Standardize event type
    df['type'] = df['type'].astype(str)

    # Shots
    if 'shot_statsbomb_xg' in df.columns:
        df['xG'] = df['shot_statsbomb_xg']
    if 'shot_outcome' in df.columns:
        df['outcome'] = df['shot_outcome']
    
    # Passes
    if 'pass_outcome' in df.columns:
        df.loc[df['type'] == 'Pass', 'outcome'] = df['pass_outcome'].fillna('Complete')
    
    # Progressive passes (very simple definition: pass that gains >30% of pitch length)
    if 'pass_length' in df.columns:
        df['progressive'] = df['pass_length'] > 30
    else:
        df['progressive'] = False

    # Pressure events
    if 'under_pressure' in df.columns:
        df['pressure'] = df['under_pressure'].fillna(False)
    else:
        df['pressure'] = False
    # print("======================================================")
    # df.to_csv("processed_events.csv")
    # print("======================================================")
    return df

def determine_outcome(event_type):
    """Determine realistic outcomes based on event type"""
    if event_type == 'Shot':
        return np.random.choice(['Goal', 'Saved', 'Off Target', 'Blocked'], p=[0.1, 0.4, 0.35, 0.15])
    elif event_type == 'Pass':
        return np.random.choice(['Complete', 'Incomplete'], p=[0.85, 0.15])
    elif event_type in ['Dribble', 'Tackle']:
        return np.random.choice(['Success', 'Fail'], p=[0.6, 0.4])
    else:
        return np.random.choice(['Success', 'Fail'], p=[0.7, 0.3])

def create_football_pitch_bg():
    """Create a football pitch background for plotly"""
    fig = go.Figure()
    
    # Pitch outline
    fig.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Center circle
    fig.add_shape(type="circle", x0=50, y0=30, x1=70, y1=50,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Center line
    fig.add_shape(type="line", x0=60, y0=0, x1=60, y1=80,
                  line=dict(color="white", width=2))
    
    # Penalty areas
    fig.add_shape(type="rect", x0=0, y0=18, x1=18, y1=62,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    fig.add_shape(type="rect", x0=102, y0=18, x1=120, y1=62,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Goal areas
    fig.add_shape(type="rect", x0=0, y0=30, x1=6, y1=50,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    fig.add_shape(type="rect", x0=114, y0=30, x1=120, y1=50,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    fig.update_layout(
        xaxis=dict(range=[0, 120], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 80], showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#2E7D32',  # Dark green pitch color
        paper_bgcolor='white',
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig


def map_home_away(events_df, match_info):
    """Map StatsBomb team names to 'Home' and 'Away'."""
    df = events_df.copy()
    home_team = match_info['home_team']
    away_team = match_info['away_team']
    df['team'] = df['team'].apply(lambda t: 'Home' if t == home_team else ('Away' if t == away_team else t))
    return df

def create_mock_events_data():
    """Create comprehensive mock events data for demonstration"""
    events = []
    players = [f'Player_{i}' for i in range(1, 23)]
    
    # Generate more realistic event data
    for minute in range(90):
        # Multiple events per minute possible
        num_events = np.random.poisson(0.8)  # Average 0.8 events per minute
        
        for _ in range(num_events):
            event_type = np.random.choice(
                ['Shot', 'Pass', 'Dribble', 'Tackle', 'Foul', 'Corner', 'Free Kick', 'Throw-in'], 
                p=[0.05, 0.6, 0.1, 0.08, 0.05, 0.03, 0.04, 0.05]
            )
            
            team = np.random.choice(['Home', 'Away'])
            player = np.random.choice(players[:11] if team == 'Home' else players[11:])
            
            # Position based on team and event type
            if team == 'Home':
                x = np.random.uniform(0, 120)
                y = np.random.uniform(0, 80)
            else:
                x = np.random.uniform(0, 120)
                y = np.random.uniform(0, 80)
            
            # Set pieces have specific locations
            if event_type == 'Corner':
                x = np.random.choice([0, 120])
                y = np.random.choice([0, 80])
            elif event_type == 'Free Kick':
                x = np.random.uniform(20, 100)
                y = np.random.uniform(10, 70)
            
            event = {
                'minute': minute,
                'player': player,
                'team': team,
                'type': event_type,
                'x': x,
                'y': y,
                'end_x': x + np.random.uniform(-20, 20) if event_type == 'Pass' else None,
                'end_y': y + np.random.uniform(-10, 10) if event_type == 'Pass' else None,
                'outcome': determine_outcome(event_type),
                'xG': np.random.uniform(0.05, 0.8) if event_type == 'Shot' else None,
                'progressive': np.random.choice([True, False], p=[0.3, 0.7]) if event_type == 'Pass' else False,
                'pressure': np.random.choice([True, False], p=[0.2, 0.8]),
                'body_part': np.random.choice(['Right Foot', 'Left Foot', 'Head', 'Other'], p=[0.6, 0.25, 0.1, 0.05]),
                'pass_height': np.random.choice(['Ground Pass', 'Low Pass', 'High Pass'], p=[0.7, 0.2, 0.1]) if event_type == 'Pass' else None
            }
            
            events.append(event)
    
    return pd.DataFrame(events)

import json
import pandas as pd

# Load JSON once

def get_shots_for_teams(team1, team2):
    with open("./data/shot_map_data.json", "r", encoding="utf-8") as f:
        shot_data = json.load(f)


    all_shots = []

    # loop for both selected teams
    for team in [team1, team2]:
        matches = shot_data["teams"][team]["matches"]
        for match in matches:
            for s in match["shots"]:
                all_shots.append({
                    "match_id": match["match_info"]["match_id"],
                    "team": s["team"],
                    "player": s["player"],
                    "x": s["position"]["x"],
                    "y": s["position"]["y"],
                    "xG": s.get("xG", 0.0),
                    "outcome": s["outcome"],
                    "type": "Shot"  # needed for create_shot_map
                })

    return pd.DataFrame(all_shots)
