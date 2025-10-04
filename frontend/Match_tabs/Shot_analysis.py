import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from Match_tabs.Base import load_match_events, create_football_pitch_bg, map_home_away


def create_shot_map(events_df):
    """Create shot map with xG values"""
    print(events_df.columns)
    if events_df.empty or 'xG' not in events_df.columns:
        fig = create_football_pitch_bg()
        fig.add_annotation(text="No shot data available", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    shots_df = events_df[events_df['type'] == 'Shot'].copy()
    # Flip away team shots
    pitch_length, pitch_width = 120, 80
    away_team = events_df['team'].unique()[1]
    shots_df.loc[shots_df['team'] == away_team, 'x'] = pitch_length - shots_df.loc[shots_df['team'] == away_team, 'x']
    shots_df.loc[shots_df['team'] == away_team, 'y'] = pitch_width - shots_df.loc[shots_df['team'] == away_team, 'y']

    if shots_df.empty:
        fig = create_football_pitch_bg()
        fig.add_annotation(text="No shots in this match", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        print("No shots in this match. but 'xG' column exists.")
        return fig
    
    fig = create_football_pitch_bg()
    
    # Add shots with different shapes for outcomes
    for team, color in [(events_df['team'].unique()[0], 'blue'), (events_df['team'].unique()[1], 'red')]:
        print("events_df team unique values:", events_df['team'].unique())
        print(f"Plotting shots for team: {team} with color {color}")
        team_shots = shots_df[shots_df['team'] == team]

        #dict of outcomes
        outcomes_ = {
            team: shots_df[shots_df['team'] == team]['outcome']
                    .value_counts()
                    .to_dict() | {"All Shots": len(shots_df[shots_df['team'] == team])}
            for team in events_df['team'].unique()
        }
        # outcomes_ = {
        #         team: shots_df[shots_df['team'] == team]['outcome']
        #                     .value_counts()
        #                     .to_dict() | {"All Shots": len(shots_df[shots_df['team'] == team])}
        #         for team in [team1, team2]
        # }

        if not team_shots.empty:
            print(f'outcomes for {team}:', team_shots['outcome'].value_counts().to_dict())
            for outcome, symbol in [('Goal', 'star'), ('Saved', 'circle'), ('Off T', 'x'), ('Blocked', 'square')]:
                outcome_shots = team_shots[team_shots['outcome'] == outcome]
                if not outcome_shots.empty:
                    fig.add_trace(go.Scatter(
                        x=outcome_shots['x'], y=outcome_shots['y'],
                        mode='markers',
                        marker=dict(
                            size=outcome_shots['xG'].fillna(0.1) * 30 + 10,
                            color=color,
                            opacity=0.8,
                            symbol=symbol,
                            line=dict(width=2, color='white')
                        ),
                        name=f'{team} {outcome}',
                        text=outcome_shots.apply(lambda row: f"Player: {row['player']}<br>xG: {row['xG']:.2f}<br>Outcome: {row['outcome']}", axis=1),
                        hovertemplate='<b>%{text}</b><extra></extra>'
                    ))
    
    fig.update_layout(title="Shot Map with xG Values & Outcomes", height=500)
    # add legend inside the pitch
    fig.update_layout(
        title="Shot Map with xG Values & Outcomes",
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
    return fig, outcomes_

# def create_shot_map(events_df, home_team=None, away_team=None):
#     """Create shot map with xG values for both teams"""
#     print(events_df.columns)

#     outcomes_ = {}
#     if events_df is None or events_df.empty or 'xG' not in events_df.columns:
#         fig = create_football_pitch_bg()
#         fig.add_annotation(
#             text="No shot data available",
#             xref="paper", yref="paper",
#             x=0.5, y=0.5, showarrow=False
#         )
#         return fig, outcomes_

#     # Filter only shots
#     shots_df = events_df[events_df['type'] == 'Shot'].copy()
#     pitch_length, pitch_width = 120, 80

#     # Flip only away team shots
#     if away_team and away_team in shots_df['team'].unique():
#         shots_df.loc[shots_df['team'] == away_team, 'x'] = pitch_length - shots_df.loc[shots_df['team'] == away_team, 'x']
#         shots_df.loc[shots_df['team'] == away_team, 'y'] = pitch_width - shots_df.loc[shots_df['team'] == away_team, 'y']

#     if shots_df.empty:
#         fig = create_football_pitch_bg()
#         fig.add_annotation(
#             text="No shots in this match",
#             xref="paper", yref="paper",
#             x=0.5, y=0.5, showarrow=False
#         )
#         print("No shots in this match, but 'xG' column exists.")
#         return fig, outcomes_

#     fig = create_football_pitch_bg()

#     # Color by team: home = blue, away = red
#     team_colors = {
#         home_team: 'blue' if home_team else 'blue',
#         away_team: 'red' if away_team else 'red'
#     }

#     # Plot shots
#     for team, color in team_colors.items():
#         if team and team in shots_df['team'].unique():
#             team_shots = shots_df[shots_df['team'] == team]

#             fig.add_scatter(
#                 x=team_shots['x'],
#                 y=team_shots['y'],
#                 mode='markers',
#                 marker=dict(
#                     size=team_shots['xG'] * 100,  # scale xG to circle size
#                     color=color,
#                     opacity=0.7,
#                     line=dict(width=1, color='black')
#                 ),
#                 name=f"{team} shots",
#                 text=[
#                     f"{p}<br>xG: {xg:.2f}<br>Outcome: {out}"
#                     for p, xg, out in zip(
#                         team_shots['player'],
#                         team_shots['xG'],
#                         team_shots['outcome']
#                     )
#                 ],
#                 hoverinfo="text"
#             )

#     # Build outcome stats
#     outcomes_ = {
#         team: shots_df[shots_df['team'] == team]['outcome']
#                 .value_counts()
#                 .to_dict() | {"All Shots": len(shots_df[shots_df['team'] == team])}
#         for team in shots_df['team'].unique()
#     }

#     return fig, outcomes_

# def create_shot_map(events_df, home_team=None, away_team=None):
#     """Create shot map with xG values for both teams with enhanced legends"""
#     print(events_df.columns)

#     outcomes_ = {}
#     if events_df is None or events_df.empty or 'xG' not in events_df.columns:
#         fig = create_football_pitch_bg()
#         fig.add_annotation(
#             text="No shot data available",
#             xref="paper", yref="paper",
#             x=0.5, y=0.5, showarrow=False
#         )
#         return fig, outcomes_

#     # Filter only shots
#     shots_df = events_df[events_df['type'] == 'Shot'].copy()
#     pitch_length, pitch_width = 120, 80

#     # Flip only away team shots
#     if away_team and away_team in shots_df['team'].unique():
#         shots_df.loc[shots_df['team'] == away_team, 'x'] = pitch_length - shots_df.loc[shots_df['team'] == away_team, 'x']
#         shots_df.loc[shots_df['team'] == away_team, 'y'] = pitch_width - shots_df.loc[shots_df['team'] == away_team, 'y']

#     if shots_df.empty:
#         fig = create_football_pitch_bg()
#         fig.add_annotation(
#             text="No shots in this match",
#             xref="paper", yref="paper",
#             x=0.5, y=0.5, showarrow=False
#         )
#         print("No shots in this match, but 'xG' column exists.")
#         return fig, outcomes_

#     fig = create_football_pitch_bg()

#     # Enhanced color mapping with better contrast
#     team_colors = {
#         home_team: '#1f77b4',  # Professional blue
#         away_team: '#d62728'   # Professional red
#     }
    
#     # Enhanced marker styles for different outcomes with distinct shapes
#     outcome_markers = {
#         'Goal': dict(symbol='star', line=dict(width=3, color='gold')),
#         'Saved': dict(symbol='circle', line=dict(width=2, color='white')),
#         'Blocked': dict(symbol='square', line=dict(width=2, color='black')),
#         'Off Target': dict(symbol='x', line=dict(width=3, color='white')),
#         'Post': dict(symbol='diamond', line=dict(width=3, color='orange')),
#         'Wayward': dict(symbol='triangle-up', line=dict(width=2, color='gray')),
#         'Own Goal': dict(symbol='hexagon', line=dict(width=3, color='purple')),
#         'Missed': dict(symbol='triangle-down', line=dict(width=2, color='red'))
#     }
    
#     # Shot type markers (if shot type data is available)
#     shot_type_markers = {
#         'Header': dict(symbol='pentagon', line=dict(width=2, color='darkblue')),
#         'Free Kick': dict(symbol='cross', line=dict(width=2, color='green')),
#         'Penalty': dict(symbol='circle-dot', line=dict(width=3, color='purple')),
#         'Volley': dict(symbol='hourglass', line=dict(width=2, color='orange')),
#         'Half Volley': dict(symbol='bowtie', line=dict(width=2, color='cyan')),
#         'Tap In': dict(symbol='circle-open', line=dict(width=2, color='lightgreen')),
#         'Lob': dict(symbol='triangle-up-open', line=dict(width=2, color='pink')),
#         'Chip': dict(symbol='diamond-open', line=dict(width=2, color='yellow')),
#         'Curler': dict(symbol='circle-cross', line=dict(width=2, color='navy')),
#         'Normal': dict(symbol='circle', line=dict(width=1, color='black'))
#     }

#     # Calculate xG ranges for legend
#     if not shots_df['xG'].empty:
#         max_xg = shots_df['xG'].max()
#         xg_ranges = [
#             (0, 0.1, "Low chance (0-0.1)"),
#             (0.1, 0.3, "Medium chance (0.1-0.3)"),
#             (0.3, 0.6, "Good chance (0.3-0.6)"),
#             (0.6, 1.0, "Great chance (0.6+)")
#         ]
    
#     # Plot shots by team with enhanced styling and different shapes
#     for team, color in team_colors.items():
#         if team and team in shots_df['team'].unique():
#             team_shots = shots_df[shots_df['team'] == team]
            
#             # Check if shot_type column exists
#             has_shot_type = 'shot_type' in team_shots.columns
            
#             # Group by outcome for better legend organization
#             for outcome in team_shots['outcome'].unique():
#                 outcome_shots = team_shots[team_shots['outcome'] == outcome]
                
#                 if has_shot_type:
#                     # Further group by shot type if available
#                     for shot_type in outcome_shots['shot_type'].unique():
#                         type_shots = outcome_shots[outcome_shots['shot_type'] == shot_type]
                        
#                         # Prioritize shot type marker, fallback to outcome marker
#                         if shot_type in shot_type_markers:
#                             marker_style = shot_type_markers[shot_type]
#                             legend_name = f"{team} - {shot_type} {outcome} ({len(type_shots)})"
#                         else:
#                             marker_style = outcome_markers.get(outcome, dict(symbol='circle', line=dict(width=1, color='black')))
#                             legend_name = f"{team} - {outcome} ({len(type_shots)})"
                        
#                         fig.add_scatter(
#                             x=type_shots['x'],
#                             y=type_shots['y'],
#                             mode='markers',
#                             marker=dict(
#                                 size=type_shots['xG'] * 80 + 10,  # Better scaling with minimum size
#                                 color=color,
#                                 opacity=0.8,
#                                 symbol=marker_style['symbol'],
#                                 line=marker_style['line'],
#                                 sizemode='diameter'
#                             ),
#                             name=legend_name[:25] + "..." if len(legend_name) > 25 else legend_name,  # Truncate long names
#                             text=[
#                                 f"<b>{p}</b><br>"
#                                 f"Team: {team}<br>"
#                                 f"Shot Type: {st}<br>"
#                                 f"xG: {xg:.3f}<br>"
#                                 f"Outcome: {out}<br>"
#                                 f"Minute: {minute if 'minute' in type_shots.columns else 'N/A'}"
#                                 for p, xg, out, minute, st in zip(
#                                     type_shots['player'],
#                                     type_shots['xG'],
#                                     type_shots['outcome'],
#                                     type_shots.get('minute', ['N/A'] * len(type_shots)),
#                                     type_shots['shot_type']
#                                 )
#                             ],
#                             hoverinfo="text",
#                             hovertemplate="%{text}<extra></extra>",
#                             legendgroup=team,  # Group by team in legend
#                             showlegend=True
#                         )
#                 else:
#                     # Use outcome-based markers when shot type is not available
#                     marker_style = outcome_markers.get(outcome, dict(symbol='circle', line=dict(width=1, color='black')))
                    
#                     fig.add_scatter(
#                         x=outcome_shots['x'],
#                         y=outcome_shots['y'],
#                         mode='markers',
#                         marker=dict(
#                             size=outcome_shots['xG'] * 80 + 10,  # Better scaling with minimum size
#                             color=color,
#                             opacity=0.8,
#                             symbol=marker_style['symbol'],
#                             line=marker_style['line'],
#                             sizemode='diameter'
#                         ),
#                         name=f"{team}-{outcome} ({len(outcome_shots)})"[:25],  # Shorter names
#                         text=[
#                             f"<b>{p}</b><br>"
#                             f"Team: {team}<br>"
#                             f"xG: {xg:.3f}<br>"
#                             f"Outcome: {out}<br>"
#                             f"Minute: {minute if 'minute' in outcome_shots.columns else 'N/A'}"
#                             for p, xg, out, minute in zip(
#                                 outcome_shots['player'],
#                                 outcome_shots['xG'],
#                                 outcome_shots['outcome'],
#                                 outcome_shots.get('minute', ['N/A'] * len(outcome_shots))
#                             )
#                         ],
#                         hoverinfo="text",
#                         hovertemplate="%{text}<extra></extra>",
#                         legendgroup=team,  # Group by team in legend
#                         showlegend=True
#                     )
    
#     # # Compact shape and xG reference in corners
#     # if not shots_df.empty:
#     #     # Smaller, more compact shape reference
#     #     outcome_ref_y = 75
#     #     key_outcomes = ['Goal', 'Saved', 'Blocked', 'Off Target']  # Show only key outcomes
        
#     #     for i, outcome in enumerate(key_outcomes):
#     #         if outcome in outcome_markers:
#     #             marker_style = outcome_markers[outcome]
#     #             fig.add_scatter(
#     #                 x=[102 + i * 4],
#     #                 y=[outcome_ref_y],
#     #                 mode='markers',
#     #                 marker=dict(
#     #                     size=12,  # Smaller reference markers
#     #                     color='lightgray',
#     #                     opacity=0.8,
#     #                     symbol=marker_style['symbol'],
#     #                     line=marker_style['line']
#     #                 ),
#     #                 name=f"Shape: {outcome}",
#     #                 showlegend=False,
#     #                 hoverinfo='skip'
#     #             )
                
#     #             # Compact text labels
#     #             fig.add_annotation(
#     #                 x=102 + i * 4,
#     #                 y=outcome_ref_y - 3,
#     #                 text=f"{outcome[:4]}",  # Abbreviated
#     #                 showarrow=False,
#     #                 font=dict(size=7, color='black'),
#     #                 bgcolor="rgba(255,255,255,0.8)"
#     #             )
        
#     #     # Compact xG size reference
#     #     ref_xg_values = [0.2, 0.5, 0.8]  # Fewer reference points
#     #     for i, xg_val in enumerate(ref_xg_values):
#     #         fig.add_scatter(
#     #             x=[102 + i * 4],
#     #             y=[65],
#     #             mode='markers',
#     #             marker=dict(
#     #                 size=xg_val * 80 + 10,
#     #                 color='lightblue',
#     #                 opacity=0.6,
#     #                 symbol='circle',
#     #                 line=dict(width=1, color='black')
#     #             ),
#     #             name=f"xG {xg_val}",
#     #             showlegend=False,
#     #             hoverinfo='skip'
#     #         )
            
#     #         # Compact xG labels
#     #         fig.add_annotation(
#     #             x=102 + i * 4,
#     #             y=60,
#     #             text=f"{xg_val}",
#     #             showarrow=False,
#     #             font=dict(size=7, color='black'),
#     #             bgcolor="rgba(255,255,255,0.8)"
#     #         )
    
#     # # Smaller, inline titles
#     # fig.add_annotation(
#     #     x=108,
#     #     y=78,
#     #     text="<b>Shapes</b>",
#     #     showarrow=False,
#     #     font=dict(size=8, weight='bold'),
#     #     bgcolor="rgba(255,255,255,0.9)"
#     # )
    
#     # fig.add_annotation(
#     #     x=108,
#     #     y=68,
#     #     text="<b>xG</b>",
#     #     showarrow=False,
#     #     font=dict(size=8, weight='bold'),
#     #     bgcolor="rgba(255,255,255,0.9)"
#     # )

#     # Compact horizontal legend formatting
#     # fig.update_layout(
#     #     legend=dict(
#     #         orientation="h",  # Horizontal orientation
#     #         yanchor="bottom",
#     #         y=-0.15,  # Below the pitch
#     #         xanchor="center",
#     #         x=0.5,  # Centered
#     #         bgcolor="rgba(255,255,255,0.95)",
#     #         bordercolor="rgba(0,0,0,0.3)",
#     #         borderwidth=1,
#     #         font=dict(size=8),  # Smaller font
#     #         itemsizing='constant',
#     #         itemwidth=30,  # Control item width
#     #         tracegroupgap=5,  # Less space between groups
#     #         entrywidth=100,        # width of each entry in pixels
#     #         entrywidthmode="fraction",
            
#     #         title=dict(
#     #             text="<b>Legend:</b> Shape = Outcome/Type | Size = xG | Color = Team",
#     #             font=dict(size=10),
#     #             side="top"
#     #         )
#     #     ),
#     #     margin=dict(b=120, r=50, l=50)  # More bottom margin, less right margin
#     # )
#     fig.update_layout(
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=-0.15,
#             xanchor="center",
#             x=0.5,
#             bgcolor="rgba(255,255,255,0.95)",
#             bordercolor="rgba(0,0,0,0.3)",
#             borderwidth=1,
#             font=dict(size=8),
#             itemsizing='constant',
#             tracegroupgap=5,
#             title=dict(
#                 text="<b>Legend:</b> Shape = Outcome/Type | Size = xG | Color = Team",
#                 font=dict(size=10),
#                 side="top"
#             )
#         ),
#         margin=dict(b=120, r=50, l=50)
#     )

#     # Add summary statistics as annotations
#     if home_team and away_team:
#         home_shots = shots_df[shots_df['team'] == home_team]
#         away_shots = shots_df[shots_df['team'] == away_team]
        
#         home_xg = home_shots['xG'].sum() if not home_shots.empty else 0
#         away_xg = away_shots['xG'].sum() if not away_shots.empty else 0
        
#         # Add xG summary
#         fig.add_annotation(
#             x=60,
#             y=-5,
#             text=f"<b>Expected Goals (xG)</b><br>{home_team}: {home_xg:.2f} | {away_team}: {away_xg:.2f}",
#             showarrow=False,
#             font=dict(size=12, color='black'),
#             bgcolor="rgba(255,255,255,0.9)",
#             bordercolor="rgba(0,0,0,0.3)",
#             borderwidth=1,
#             xanchor='center'
#         )

#     # Build outcome stats (unchanged)
#     outcomes_ = {
#         team: shots_df[shots_df['team'] == team]['outcome']
#                 .value_counts()
#                 .to_dict() | {"All Shots": len(shots_df[shots_df['team'] == team])}
#         for team in shots_df['team'].unique()
#     }

#     return fig, outcomes_


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



def load_shot_analysis(events_df):
    st.subheader("Shot Analysis & Expected Goals")
    st.plotly_chart(create_shot_map(events_df), use_container_width=True)
    
    # Shot statistics
    shots_df = events_df[events_df['type'] == 'Shot']
    if not shots_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Home Team Shots")
            home_shots = shots_df[shots_df['team'] == 'Home']
            if not home_shots.empty:
                home_shot_stats = home_shots['outcome'].value_counts()
                fig_home = px.pie(values=home_shot_stats.values, names=home_shot_stats.index,
                                title="Home Team Shot Outcomes", color_discrete_sequence=['blue', 'lightblue', 'navy', 'darkblue'])
                st.plotly_chart(fig_home, use_container_width=True)
        
        with col2:
            st.subheader("Away Team Shots")
            away_shots = shots_df[shots_df['team'] == 'Away']
            if not away_shots.empty:
                away_shot_stats = away_shots['outcome'].value_counts()
                fig_away = px.pie(values=away_shot_stats.values, names=away_shot_stats.index,
                                title="Away Team Shot Outcomes", color_discrete_sequence=['red', 'lightcoral', 'darkred', 'maroon'])
                st.plotly_chart(fig_away, use_container_width=True)
