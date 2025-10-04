import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    mock_data = {
            # Possession & Passing Data
            'possession': {
                'home_team': {'possession_%': 62.5, 'total_time_have_ball': 58.75}, # total_time_have_ball will removed
                'away_team': {'possession_%': 37.5, 'total_time_have_ball': 32.25} 
            },
            
            'passing': {
                'home_team': {
                    'total_passes': 542,
                    'completed_passes': 478,
                    'passing_accuracy': 88.2,
                    'progressive_passes': 34,
                    'final_third_passes': 67,# Mean for pass in Attack
                    'penalty_area_passes': 23,
                    'crosses_attempted': 18,
                    'crosses_completed': 7,
                    'cross_success_rate': 38.9
                },
                'away_team': {
                    'total_passes': 321,
                    'completed_passes': 267,
                    'passing_accuracy': 83.2,
                    'progressive_passes': 28,
                    'final_third_passes': 45,
                    'penalty_area_passes': 19,
                    'crosses_attempted': 24,
                    'crosses_completed': 9,
                    'cross_success_rate': 37.5
                }
            },
            
            # Attacking Data
            'attacking': {
                'home_team': {
                    'total_shots': 16,
                    'shots_on_target': 7,
                    'shots_blocked': 4,
                    'shots_off_target': 5,
                    'xg': 2.34,
                    'avg_xg_per_shot': 0.146,
                    'key_passes': 12,
                    'dribbles_attempted': 23,
                    'dribbles_successful': 14,
                    'dribble_success_rate': 60.9,
                    'touches_in_box': 31,
                    'set_piece_chances': 8
                },
                'away_team': {
                    'total_shots': 11,
                    'shots_on_target': 4,
                    'shots_blocked': 3,
                    'shots_off_target': 4,
                    'xg': 1.67,
                    'avg_xg_per_shot': 0.152,
                    'key_passes': 8,
                    'dribbles_attempted': 19,
                    'dribbles_successful': 11,
                    'dribble_success_rate': 57.9,
                    'touches_in_box': 24,
                    'set_piece_chances': 6
                }
            },
            
            # Defensive Data
            'defensive': {
                'home_team': {
                    'pressures': 89,
                    'high_pressures': 34,
                    'tackles': 18,
                    'interceptions': 12,
                    'ball_recoveries': 56,
                    'blocks': 7,
                    'clearances': 23,
                    'xga': 1.67,
                    'pressing_success': 23.6,
                    "aerial_duels_won": 6,
                    "fouls_committed": 12,
                    "yellow_cards": 3,
                    "red_cards": 1
                },
                'away_team': {
                    'pressures': 112,
                    'high_pressures': 41,
                    'tackles': 23,
                    'interceptions': 15,
                    'ball_recoveries': 71,
                    'blocks': 4,
                    'clearances': 34,
                    'xga': 2.34,
                    'pressing_success': 28.1,
                    "aerial_duels_won": 6,
                    "fouls_committed": 10,
                    "yellow_cards": 2,
                    "red_cards": 0
                }
            },
            
            # Team Shape Data
            # 'team_shape': {
            #     'home_team': {
            #         'avg_defensive_line': 42.3,
            #         'formation_attacking': '4-3-3',
            #         'formation_defensive': '4-4-2',
            #         'avg_team_width': 68.4
            #     },
            #     'away_team': {
            #         'avg_defensive_line': 38.7,
            #         'formation_attacking': '3-5-2',
            #         'formation_defensive': '5-3-2',
            #         'avg_team_width': 71.2
            #     }
            # },
            # # goalkeeping Data
            'goalkeeper': {
                'home_team': {
                    'saves': 3,                         # from Save events
                    'shots_faced': 4,                   # total Shots on target faced
                    'goals_conceded': 1,                # Shots with outcome "Goal"
                    'clean_sheets': 0,                  # 1 if goals_conceded == 0 else 0
                    'goals_prevented': 0.67,            # sum(xG of shots on target faced) - goals_conceded
                    'post_shot_xg_conceded': 1.34,      # total psxG conceded (from StatsBomb shot data)
                    'psxg_plus_minus': +0.67,           # goals_prevented above
                    'sweeper_actions': 2                # GK defensive actions outside box (pressures, tackles, interceptions)
                },
                'away_team': {
                    'saves': 5,
                    'shots_faced': 7,
                    'goals_conceded': 2,
                    'clean_sheets': 0,
                    'goals_prevented': 1.12,
                    'post_shot_xg_conceded': 3.12,
                    'psxg_plus_minus': +1.12,
                    'sweeper_actions': 1
                }
            },

            # Transition Data
            'transition': {
                'home_team': {
                    'counter_attacks': 7,
                    'counter_attack_shots': 3,
                    'turnovers_to_shots': 4,
                    'avg_attack_speed': 2.1,
                    'press_to_attack_conversion': 15.7
                },
                'away_team': {
                    'counter_attacks': 9,
                    'counter_attack_shots': 4,
                    'turnovers_to_shots': 6,
                    'avg_attack_speed': 2.4,
                    'press_to_attack_conversion': 18.9
                }
            },
            
           
            # Efficiency Data
            'efficiency': {
                'home_team': {
                    'goals_scored': 2,
                    'goals_conceded': 1,
                    'conversion_rate': 12.5,
                    'xg_vs_goals_diff': -0.34,
                    'xga_vs_conceded_diff': -0.67
                },
                'away_team': {
                    'goals_scored': 1,
                    'goals_conceded': 2,
                    'conversion_rate': 9.1,
                    'xg_vs_goals_diff': -0.67,
                    'xga_vs_conceded_diff': 0.34
                }
            }
        }

    return mock_data
    # In a real scenario, you would load data from a file or database
    # For example:
    # from statsbomby as sb
    # data = sb.events(match_id=match_id, team_id=team_id)

tabs_have = {
    "Possession & Passing": "⚽",
    "Attacking Metrics": "🎯",
    "Defensive Metrics": "🛡️",
    "Transition Play": "↔️",
    "Goalkeeper Performance": "🧤",
    "Efficiency & Outcome": "📈"
}

icon_logo ={
    "passing":["⚽","Possession & Passing"],
    "attacking":["🎯","Attacking Metrics"],
    "defensive":["🛡️","Defensive Metrics"],
    "transition":["↔️","Transition Play"],
    "goalkeeper":["🧤","Goalkeeper Performance"],
    "efficiency":["📈","Efficiency & Outcome"]
}

home_team = "home_team"
away_team = "away_team"
selected_stage = ["Group Stage", "Round of 16", "Quarter Finals", "Semi Finals", "Final"]
selected_match = ["Match 1", "Match 2", "Match 3", "Match 4", "Match 5"]