import streamlit as st
import pandas as pd
import plotly.graph_objects as go

try:
    from statsbombpy import sb
    STATSBOMB_AVAILABLE = True
except ImportError:
    STATSBOMB_AVAILABLE = False
    st.warning("StatsBombPy not available. Using mock data for demonstration.")


# Define action categories
def classify_action(row):
    if row['type'] == 'Tackle':
        return 'Tackle'
    elif row['type'] == 'Block':
        return 'Block'
    elif row['type'] == 'Foul Committed':
        return 'Foul'
    elif row['type'] == 'Duel' and 'Won' in str(row['duel_outcome']):
        return 'Aerial Duel Won'
    else:
        return None

def draw_pitch_plot():
    MATCH_ID = 3869684  # Example match

    # Load events
    @st.cache_data
    def load_events(match_id):
        events = sb.events(match_id=match_id)
        return events

    events = load_events(MATCH_ID)

    # Defensive actions
    def_actions = ['Tackle', 'Block', 'Foul Committed', 'Duel']
    df = events[events['type'].isin(def_actions)].copy()

    # Extract coordinates
    df = df[['team', 'player', 'type', 'location', 'duel_outcome']].dropna(subset=['location'])
    df['x'] = df['location'].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
    df['y'] = df['location'].apply(lambda loc: loc[1] if isinstance(loc, list) else None)


    df['action_category'] = df.apply(classify_action, axis=1)
    df = df.dropna(subset=['action_category'])

    # Sidebar filters
    teams = df['team'].unique()
    selected_team = st.sidebar.selectbox("Select Team", teams)
    selected_events = st.sidebar.multiselect("Select Events", df['action_category'].unique(), default=df['action_category'].unique())

    # Filter dataframe
    filtered_df = df[(df['team'] == selected_team) & (df['action_category'].isin(selected_events))]

    # Plotly pitch
    fig = go.Figure()

    # Draw pitch (120x80)
    fig.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(color="white", width=2), fillcolor="#3f995b")
    fig.add_shape(type="line", x0=60, y0=0, x1=60, y1=80, line=dict(color="white", width=2))  # Halfway
    fig.add_shape(type="circle", x0=60-9.15, y0=40-9.15, x1=60+9.15, y1=40+9.15, line=dict(color="white"))  # Center circle
    fig.add_shape(type="rect", x0=0, y0=18, x1=18, y1=62, line=dict(color="white"))  # Left penalty
    fig.add_shape(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(color="white"))  # Right penalty

    # Color map for event types
    colors = {
        "Tackle": "blue",
        "Block": "orange",
        "Foul": "red",
        "Aerial Duel Won": "purple"
    }

    # Add events
    for cat in selected_events:
        cat_df = filtered_df[filtered_df['action_category'] == cat]
        fig.add_trace(go.Scatter(
            x=cat_df['x'], y=cat_df['y'],
            mode='markers',
            marker=dict(size=12, color=colors[cat], line=dict(width=1, color="black")),
            name=cat,
            text=cat_df['player'],
            hovertemplate="%{text}<br>%{x}, %{y}<extra></extra>"
        ))

    # Layout
    fig.update_yaxes(autorange="reversed", visible=False)
    fig.update_xaxes(visible=False)
    fig.update_layout(
        height=700,
        width=1000,
        plot_bgcolor="#3f995b",
        title=f"Defensive Actions - {selected_team}"
    )

    st.plotly_chart(fig, use_container_width=True)
