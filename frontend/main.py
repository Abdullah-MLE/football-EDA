from helpers import page_cfg
import streamlit as st
import pandas as pd

page_cfg.load_page_config()

# Read data
df = pd.read_csv("../data/matches_index.csv")

st.title("⚽ Football Analytics Platform")
st.write("Choose a section to explore:")

# Create 2x2 grid
col1, col2 = st.columns(2)

# ===== Tournament Analsysis SECTION =====
with col1:
    with st.container():
        st.subheader("Tournament Analsysis")
        
        # Get unique competitions
        competitions = df['competition'].unique().tolist()
        
        # Competition selection
        selected_competition = st.selectbox(
            "Select a Competition:",
            options = competitions,
            placeholder="Choose a competition...",
            key="comp_select"
        )
        
        # Button to navigate to TournamentProgression page
        if st.button("View Details", key="tournament_btn", use_container_width=True):
            if selected_competition:
                st.session_state['selected_competition'] = selected_competition
                st.switch_page("pages/Tournament Progression.py")
            else:
                st.warning("Please select a competition first!")

# ===== MATCH ANALYSIS SECTION =====
with col2:
    st.header("Match Analysis")

    # Define the default value for empty selections
    EMPTY_SELECTION = "Choose"

    # List of columns that users can filter by
    filter_columns = [
        "competition",       # The league or tournament name
        "season",            # The season/year
        "competition_stage", # Stage of competition (e.g., group stage, knockout)
        "team1",             # First team name
        "team2",             # Second team name
        "match_date",        # Date when the match was played
        "match_id"           # Unique identifier for the match
    ]

    # --- Initialize reset functionality ---
    # This flag helps us reset all filters when user clicks "Clear Filters"
    if "reset_flag" not in st.session_state:
        st.session_state.reset_flag = False

    # If reset was triggered, clear all selections
    if st.session_state.reset_flag:
        for column in filter_columns:
            st.session_state[column] = EMPTY_SELECTION
        st.session_state.reset_flag = False

    # Initialize session state for each filter column if not already present
    # This ensures all filters start with "Choose" as default value
    for column in filter_columns:
        if column not in st.session_state:
            st.session_state[column] = EMPTY_SELECTION

    def get_filtered_data_and_options(original_data):
        """
        Filter the data based on current selections and compute available options
        
        Parameters:
        - original_data: The complete unfiltered dataset
        
        Returns:
        - filtered_data: Data filtered based on current selections
        - available_options: Dictionary of available options for each filter
        """
        
        # Collect all current selections (excluding empty ones)
        active_filters = {
            column: st.session_state[column] 
            for column in filter_columns 
            if st.session_state[column] != EMPTY_SELECTION
        }
        
        # Start with a copy of the original data
        filtered_data = original_data.copy()
        
        # Apply each active filter to narrow down the data
        for column, selected_value in active_filters.items():
            filtered_data = filtered_data[
                filtered_data[column].astype(str) == str(selected_value)
            ]
        
        # Calculate available options for each filter based on current filtered data
        available_options = {}
        for column in filter_columns:
            # Get unique values from the filtered data
            unique_values = filtered_data[column].dropna().unique().tolist()
            # Convert all values to strings for consistency
            unique_values = [str(value) for value in unique_values]
            # Add "Choose" as first option and sort the rest
            available_options[column] = [EMPTY_SELECTION] + sorted(unique_values)
        
        return filtered_data, available_options

    # Get initial filtered data and options
    filtered_data, available_options = get_filtered_data_and_options(df)

    # Check if any current selections are no longer valid
    # This can happen when changing a filter removes options from other filters
    invalid_selection_detected = False
    for column in filter_columns:
        if st.session_state[column] not in available_options[column]:
            st.session_state[column] = EMPTY_SELECTION
            invalid_selection_detected = True

    # If any selections were reset, recalculate the filtered data
    if invalid_selection_detected:
        filtered_data, available_options = get_filtered_data_and_options(df)

    def calculate_default_index(column_name):
        """
        Calculate which item should be selected by default in a dropdown
        
        If there's only one option besides "Choose", select it automatically
        Otherwise, keep the current selection
        """
        if len(available_options[column_name]) == 2:  # Only "Choose" and one other option
            return 1  # Select the actual option, not "Choose"
        
        # Find the index of current selection, or default to 0 ("Choose")
        if st.session_state[column_name] in available_options[column_name]:
            return available_options[column_name].index(st.session_state[column_name])
        return 0

    # === Create the filter interface ===
    
    # First row of filters: Competition details
    filter_row_1 = st.columns(3)
    with filter_row_1[0]:
        st.selectbox(
            "Competition:", 
            options=available_options["competition"], 
            index=calculate_default_index("competition"), 
            key="competition"
        )
    with filter_row_1[1]:
        st.selectbox(
            "Season:", 
            options=available_options["season"], 
            index=calculate_default_index("season"), 
            key="season"
        )
    with filter_row_1[2]:
        st.selectbox(
            "Competition Stage:", 
            options=available_options["competition_stage"], 
            index=calculate_default_index("competition_stage"), 
            key="competition_stage"
        )

    # Second row of filters: Teams and date
    filter_row_2 = st.columns(3)
    with filter_row_2[0]:
        st.selectbox(
            "Home Team:", 
            options=available_options["team1"], 
            index=calculate_default_index("team1"), 
            key="team1"
        )
    with filter_row_2[1]:
        st.selectbox(
            "Away Team:", 
            options=available_options["team2"], 
            index=calculate_default_index("team2"), 
            key="team2"
        )
    with filter_row_2[2]:
        st.selectbox(
            "Match Date:", 
            options=available_options["match_date"], 
            index=calculate_default_index("match_date"), 
            key="match_date"
        )

    # Third row: Match ID and control buttons
    control_row = st.columns([1, 1, 1])
    with control_row[0]:
        st.selectbox(
            "Match ID:", 
            options=available_options["match_id"], 
            index=calculate_default_index("match_id"), 
            key="match_id"
        )
    with control_row[1]:
        # Button to clear all filters and start fresh
        if st.button("Clear All Filters"):
            st.session_state.reset_flag = True
            st.rerun()
    with control_row[2]:
        # Checkbox to show/hide the matches table
        show_matches_table = st.checkbox("Show Matches Table")

    # === Apply final filtering to get results ===
    
    # Collect all active filters (non-empty selections)
    active_filters = {
        column: st.session_state[column] 
        for column in filter_columns 
        if st.session_state[column] != EMPTY_SELECTION
    }
    
    # Apply filters to get final results
    final_results = df.copy()
    for column, selected_value in active_filters.items():
        final_results = final_results[
            final_results[column].astype(str) == str(selected_value)
        ]

    # Display the filtered matches table if checkbox is selected
    if show_matches_table:
        st.subheader("Filtered Matches")
        # Show the number of matches found
        st.write(f"Found {len(final_results)} matches")
        st.dataframe(final_results)
        
    
    # Navigation button to go to another section
    st.button("Go to Player Analysis", use_container_width=True)

# Add a visual separator
st.markdown("---")

col3, col4 = st.columns(2)
# ===== TEAM COMPARISON SECTION =====
with col3:
    with st.container():
        st.subheader("Team Comparison")
        st.write("Compare performance between any two teams")
        
        # Get all unique team names
        all_teams = pd.concat([df['team1'], df['team2']]).dropna().unique()
        all_teams = sorted(all_teams.tolist())
        
        team_cols = st.columns(2)
        with team_cols[0]:
            # First team selection
            st.markdown("**Select First Team:**")
            team_1 = st.selectbox(
                "First team",
                options=all_teams,
                key="comparison_team_1",
                label_visibility="collapsed"
            )
        
        with team_cols[1]:
            # Second team selection (excluding the first team)
            st.markdown("**Select Second Team:**")
            remaining_teams = [team for team in all_teams if team != team_1]
            team_2 = st.selectbox(
                "Second team",
                options=remaining_teams,
                key="comparison_team_2",
                label_visibility="collapsed"
            )
        
        # Button to go to comparison page
        if st.button("Go to Team Comparison", key="compare_team_btn", use_container_width=True):
            st.switch_page("pages/Team Comparison.py")

# ===== Player COMPARISON SECTION =====
with col4:
    with st.container():
        st.subheader("Player Comparison")
        st.write("Compare performance between any two Players")
        
        # Get all unique playes names
        all_players = pd.concat([df['team1'], df['team2']]).dropna().unique()
        all_players = sorted(all_players.tolist())
        
        player_cols = st.columns(2)
        with player_cols[0]:
            # First player selection
            st.markdown("**Select First player:**")
            player_1 = st.selectbox(
                "First player",
                options=all_players,
                key="comparison_player_1",
                label_visibility="collapsed"
            )
        
        with player_cols[1]:
            # Second player selection (excluding the first player)
            st.markdown("**Select Second player:**")
            remaining_players = [player for player in all_players if player != player_1]
            player_2 = st.selectbox(
                "Second player",
                options=remaining_players,
                key="comparison_player_2",
                label_visibility="collapsed"
            )
        
        # Button to go to comparison page
        if st.button("Go to player Comparison", key="compare_player_btn", use_container_width=True):
            st.switch_page("pages/player Comparison.py")
