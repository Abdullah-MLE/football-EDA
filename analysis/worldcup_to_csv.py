

"""
Refactored World Cup 2022 extractor (StatsBomb events -> per-team CSV)

This is an updated, fully patched version that includes:
- Robust possession (weighted by number of events per possession)
- Orientation-aware passing calculations (infers team forward direction)
- Vectorized masks for progressive, final-third, penalty-area passes
- Prefer StatsBomb flags (pass_cross, pass_shot_assist) when available
- Possession-based counter-attack and press->attack calculations
- Safe handling of missing columns and conservative fallbacks
- **Shootout & post-120-minute shot exclusion** and **duplicate-shot deduplication** to prevent inflated shot/xG totals

Requirements:
    pip install statsbombpy pandas numpy

Usage examples:
- Process whole World Cup 2022 tournament and save CSV:
    extractor = RefactoredWorldCupExtractor()
    extractor.process_all_matches(save_csv='worldcup_2022_match_data.csv')

- Process a single match by match_id and save:
    extractor = RefactoredWorldCupExtractor()
    df = extractor.process_single_match(match_id=3869685, save_csv='final.csv')

Note: Running this script requires internet access if you use statsbombpy to fetch events.
If you prefer to provide event JSON/CSV files, modify `get_match_events` to load from disk.
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from statsbombpy import sb


class RefactoredWorldCupExtractor:
    def __init__(self, competition_id=43, season_id=106, pitch_length=120.0, pitch_width=80.0):
        self.competition_id = competition_id
        self.season_id = season_id
        self.pitch_length = float(pitch_length)
        self.pitch_width = float(pitch_width)

    # ----------------- Data fetching -----------------
    def get_matches(self):
        try:
            matches = sb.matches(competition_id=self.competition_id, season_id=self.season_id)
            print(f"Found {len(matches)} matches in competition={self.competition_id}, season={self.season_id}")
            return matches
        except Exception as e:
            print(f"Error fetching matches: {e}")
            return None

    def get_match_events(self, match_id):
        try:
            events = sb.events(match_id=match_id)
            events = events.reset_index(drop=True)
            return events
        except Exception as e:
            print(f"Error fetching events for match {match_id}: {e}")
            return None

    # ----------------- Helpers -----------------
    def safe_coord(self, coord, idx=0):
        if isinstance(coord, (list, tuple)) and len(coord) > idx:
            try:
                return float(coord[idx])
            except Exception:
                return np.nan
        return np.nan

    def infer_team_direction(self, events, team_name, min_samples=10):
        passes = events[(events['type'] == 'Pass') & (events['team'] == team_name)].copy()
        if 'location' not in passes.columns or 'pass_end_location' not in passes.columns:
            return 1
        valid = passes[passes['location'].apply(lambda c: isinstance(c, (list,tuple)) and len(c)>=2) &
                      passes['pass_end_location'].apply(lambda c: isinstance(c, (list,tuple)) and len(c)>=2)]
        if len(valid) < min_samples:
            return 1
        start_x = valid['location'].apply(lambda c: float(c[0]))
        end_x = valid['pass_end_location'].apply(lambda c: float(c[0]))
        mean_diff = (end_x - start_x).mean()
        return 1 if mean_diff >= 0 else -1

    # ----------------- Cleaning (shootout, duplicates) -----------------
    def clean_events(self, events):
        """Remove shootout/post-120 shot events and optionally deduplicate obvious duplicate shots.
        Returns a cleaned copy of events.
        """
        ev = events.copy()
        # Remove periods > 4 (some datasets mark shootout as period 5). Keep only regular + ET periods (1..4).
        if 'period' in ev.columns:
            ev = ev[ev['period'] <= 4].reset_index(drop=True)
        # Remove shot events after minute > 120 (likely shootout or bad rows)
        if 'minute' in ev.columns:
            # minute might be string or numeric
            ev = ev[~((ev['type'] == 'Shot') & (ev['minute'].astype(float) > 120))].reset_index(drop=True)
        # Deduplicate shot events that have identical (team, minute, period, location)
        if 'type' in ev.columns and 'location' in ev.columns and 'minute' in ev.columns and 'team' in ev.columns:
            shots = ev[ev['type'] == 'Shot']
            # create tuple key
            # shots['loc_key'] = shots.apply(lambda r: (r['team'], r['period'] if 'period' in r.index else None, r['minute'] if 'minute' in r.index else None, tuple(r['location']) if isinstance(r['location'], (list,tuple)) else None), axis=1)
            # dup_keys = shots['loc_key'][shots['loc_key'].duplicated(keep=False)].unique() if len(shots) > 0 else []
            # if len(dup_keys) > 0:
            #     # drop duplicated shot rows but keep the first occurrence
            #     to_drop_idx = []
            #     for key in dup_keys:
            #         idxs = shots[shots['loc_key'] == key].index.tolist()
            #         # keep first, drop others
            #         to_drop_idx.extend(idxs[1:])
            #     ev = ev.drop(index=to_drop_idx).reset_index(drop=True)

            # Fix: exclude 'location' from drop_duplicates subset because it's unhashable (list)
            subset_cols = ['team', 'minute']
            if 'period' in shots.columns:
                subset_cols.append('period')

            # Check if 'location' is present before attempting to use it (though we are excluding it)
            # If location is needed for deduplication, it would need to be converted to a hashable type (e.g., tuple or string)
            # For now, we rely on team, minute, and period being sufficient identifiers for duplicates.
            if 'location' in shots.columns:
                 # Convert location lists to tuples for potential future use or debugging, though not used in drop_duplicates subset below
                 shots['_location_tuple'] = shots['location'].apply(lambda x: tuple(x) if isinstance(x, (list,tuple)) else None)


            # Apply drop_duplicates excluding the problematic 'location' column from the subset
            # Using a combination of team, minute, and period should catch most identical duplicates
            if len(shots) > 0:
                 ev = ev.drop(shots.index[shots.drop(columns=['location'], errors='ignore').duplicated(subset=subset_cols, keep=False)])
                 ev = ev.reset_index(drop=True)


        return ev


    # ----------------- Possession -----------------
    def calculate_possession(self, events, home_team, away_team):
        if 'possession' not in events.columns:
            possession_events = events[events['type'].isin(['Pass','Carry','Dribble'])]
            h = possession_events[possession_events['team'] == home_team].shape[0]
            a = possession_events[possession_events['team'] == away_team].shape[0]
            total = h + a
            if total == 0:
                return {'home_team': {'possession_%': 50.0}, 'away_team': {'possession_%': 50.0}}
            return {'home_team': {'possession_%': round(h / total * 100, 1)},
                    'away_team': {'possession_%': round(a / total * 100, 1)}}
        poss = events.groupby('possession')
        owner = poss['team'].agg(lambda s: s.value_counts().idxmax())
        sizes = poss.size()
        owner_df = pd.DataFrame({'owner': owner, 'size': sizes})
        home_events = owner_df[owner_df['owner'] == home_team]['size'].sum()
        away_events = owner_df[owner_df['owner'] == away_team]['size'].sum()
        total = home_events + away_events
        if total == 0:
                return {'home_team': {'possession_%': 50.0}, 'away_team': {'possession_%': 50.0}}
        return {
            'home_team': {'possession_%': round(home_events / total * 100, 1)},
            'away_team': {'possession_%': round(away_events / total * 100, 1)}
        }

    # ----------------- Passing -----------------
    def compute_passing_breakdowns(self, events, team_name):
        team_passes = events[(events['type'] == 'Pass') & (events['team'] == team_name)].copy()
        total_passes = int(len(team_passes))
        completed_passes = int(team_passes['pass_outcome'].isna().sum()) if 'pass_outcome' in team_passes.columns else 0
        dir_sign = self.infer_team_direction(events, team_name)
        start_x = team_passes['location'].apply(lambda c: self.safe_coord(c, 0) if 'location' in team_passes.columns else np.nan)
        end_x = team_passes['pass_end_location'].apply(lambda c: self.safe_coord(c, 0) if 'pass_end_location' in team_passes.columns else np.nan)
        prog_mask = (end_x.notna()) & (start_x.notna()) & (((end_x - start_x) * dir_sign) >= 10)
        progressive_passes = int((team_passes['pass_outcome'].isna() & prog_mask).sum()) if 'pass_outcome' in team_passes.columns else int(prog_mask.sum())
        third_boundary = self.pitch_length * 2 / 3
        if dir_sign == 1:
            final_third_mask = start_x >= third_boundary
            penalty_area_mask = start_x >= (self.pitch_length - 18)
        else:
            final_third_mask = start_x <= (self.pitch_length / 3)
            penalty_area_mask = start_x <= 18
        final_third_passes = int(team_passes[final_third_mask].shape[0])
        penalty_area_passes = int(team_passes[penalty_area_mask].shape[0])
        crosses_attempted = 0
        crosses_completed = 0
        if 'pass_cross' in team_passes.columns:
            crosses = team_passes[team_passes['pass_cross'] == True]
            crosses_attempted = int(len(crosses))
            crosses_completed = int(crosses['pass_outcome'].isna().sum()) if 'pass_outcome' in crosses.columns else int(crosses.shape[0])
        else:
            wide_mask = team_passes['location'].apply(lambda x: isinstance(x, (list, tuple)) and len(x) >= 2 and (x[1] < 20 or x[1] > (self.pitch_width - 20))) if 'location' in team_passes.columns else pd.Series(False, index=team_passes.index)
            crosses_attempted = int(wide_mask.sum())
            crosses_completed = int((wide_mask & team_passes['pass_outcome'].isna()).sum()) if 'pass_outcome' in team_passes.columns else int(wide_mask.sum())
        cross_success_rate = round((crosses_completed / crosses_attempted * 100) if crosses_attempted > 0 else 0.0, 1)
        accuracy = round((completed_passes / total_passes * 100) if total_passes > 0 else 0.0, 1)
        return {
            'total_passes': total_passes,
            'completed_passes': completed_passes,
            'passing_accuracy': accuracy,
            'progressive_passes': progressive_passes,
            'final_third_passes': final_third_passes,
            'penalty_area_passes': penalty_area_passes,
            'crosses_attempted': crosses_attempted,
            'crosses_completed': crosses_completed,
            'cross_success_rate': cross_success_rate
        }

    # ----------------- Attacking / Shots (safe xG and dedup) -----------------
    def compute_shot_stats(self, events, team_name):
        ev = events.copy()
        # consider only main match periods
        # exclude shootout artifacts (clean_events will usually handle it if called earlier)
        team_shots = ev[(ev['type'] == 'Shot') & (ev['team'] == team_name)].copy()
        # exclude minute>120 if present
        if 'minute' in team_shots.columns:
            team_shots = team_shots[team_shots['minute'].astype(float) <= 120]
        # deduplicate obvious duplicates - exclude 'location' from subset as it contains lists
        if 'minute' in team_shots.columns and 'team' in team_shots.columns:
            subset_cols = ['team', 'minute']
            if 'period' in team_shots.columns:
                subset_cols.append('period')
            # Only deduplicate if there are shots and necessary columns are present
            if len(team_shots) > 0 and all(col in team_shots.columns for col in subset_cols):
                team_shots = team_shots.drop_duplicates(subset=subset_cols, keep='first')

        total_shots = int(team_shots.shape[0])
        shots_on_target = int(team_shots[team_shots['shot_outcome'].isin(['Saved','Goal'])].shape[0]) if 'shot_outcome' in team_shots.columns else 0
        shots_blocked = int(team_shots[team_shots['shot_outcome'] == 'Blocked'].shape[0]) if 'shot_outcome' in team_shots.columns else 0
        shots_off_target = int(team_shots[team_shots['shot_outcome'].isin(['Off T','Off Target','Wide'])].shape[0]) if 'shot_outcome' in team_shots.columns else 0
        xg_values = team_shots['shot_statsbomb_xg'] if 'shot_statsbomb_xg' in team_shots.columns else pd.Series(dtype=float)
        total_xg = float(xg_values.fillna(0).sum()) if len(xg_values) > 0 else 0.0
        avg_xg_per_shot = round((total_xg / total_shots) if total_shots > 0 else 0.0, 3)
        key_passes = 0
        if 'pass_shot_assist' in ev.columns:
            key_passes = int(ev[(ev['team'] == team_name) & (ev['type'] == 'Pass') & (ev['pass_shot_assist'] == True)].shape[0])
        else:
            if 'possession' in ev.columns:
                evi = ev.reset_index(drop=True)
                for i in range(len(evi)-1):
                    row = evi.loc[i]
                    nxt = evi.loc[i+1]
                    if row['team'] == team_name and row['type'] == 'Pass' and nxt['type'] == 'Shot' and nxt['team'] == team_name and row.get('possession') == nxt.get('possession'):
                        key_passes += 1
            else:
                key_passes = int(total_shots * 0.05)
        return {
            'total_shots': total_shots,
            'shots_on_target': shots_on_target,
            'shots_blocked': shots_blocked,
            'shots_off_target': shots_off_target,
            'xg': round(total_xg, 2),
            'avg_xg_per_shot': avg_xg_per_shot,
            'key_passes': key_passes
        }

    # ----------------- Defensive -----------------
    def compute_defensive(self, events, team_name):
        team_events = events[events['team'] == team_name].copy()
        pressures = int(team_events[team_events['type'] == 'Pressure'].shape[0])
        high_pressures = int(team_events[(team_events['type'] == 'Pressure') & (team_events['location'].apply(lambda x: isinstance(x, (list, tuple)) and len(x) >= 2 and x[0] > (self.pitch_length * 2 / 3) if 'location' in team_events.columns else False))].shape[0]) if 'type' in team_events.columns else 0
        tackles = int(team_events[team_events['type'] == 'Tackle'].shape[0])
        interceptions = int(team_events[team_events['type'] == 'Interception'].shape[0])
        ball_recoveries = int(team_events[team_events['type'] == 'Ball Recovery'].shape[0])
        blocks = int(team_events[team_events['type'] == 'Block'].shape[0])
        clearances = int(team_events[team_events['type'] == 'Clearance'].shape[0])
        opponent_shots = events[(events['type'] == 'Shot') & (events['team'] != team_name)]
        xga = float(opponent_shots['shot_statsbomb_xg'].fillna(0).sum()) if 'shot_statsbomb_xg' in opponent_shots.columns else 0.0
        pressing_success = 0.0
        if pressures > 0 and 'possession' in team_events.columns:
            poss = team_events.groupby('possession')
            successful = 0
            total = 0
            for pid, grp in poss:
                p_count = grp[grp['type'] == 'Pressure'].shape[0]
                if p_count > 0:
                    total += p_count
                    successful += grp[grp['type'] == 'Ball Recovery'].shape[0]
            if total > 0:
                pressing_success = min(successful / total * 100, 100.0)
        aerial_duels_won = 0
        if 'aerial_won' in team_events.columns:
            aerial_duels_won = int(team_events[team_events['aerial_won'] == True].shape[0])
        else:
            aerial_duels_won = int(team_events[team_events['type'] == 'Duel'].shape[0])
        fouls_committed = int(team_events[team_events['type'] == 'Foul Committed'].shape[0])
        yellow_cards = 0
        red_cards = 0
        if 'bad_behaviour_card' in team_events.columns:
            yellow_cards = int(team_events[team_events['bad_behaviour_card'] == 'Yellow Card'].shape[0])
            red_cards = int(team_events[team_events['bad_behaviour_card'] == 'Red Card'].shape[0])
        elif 'card' in team_events.columns:
            yellow_cards = int(team_events[team_events['card'] == 'Yellow Card'].shape[0])
            red_cards = int(team_events[team_events['card'] == 'Red Card'].shape[0])
        return {
            'pressures': pressures,
            'high_pressures': high_pressures,
            'tackles': tackles,
            'interceptions': interceptions,
            'ball_recoveries': ball_recoveries,
            'blocks': blocks,
            'clearances': clearances,
            'xga': round(xga, 2),
            'pressing_success': round(pressing_success, 1),
            'aerial_duels_won': aerial_duels_won,
            'fouls_committed': fouls_committed,
            'yellow_cards': yellow_cards,
            'red_cards': red_cards
        }

    # ----------------- Goalkeeper -----------------
    def compute_goalkeeper(self, events, team_name):
        opponent_shots = events[(events['type'] == 'Shot') & (events['team'] != team_name)].copy()
        shots_on_target = opponent_shots[opponent_shots['shot_outcome'].isin(['Saved', 'Goal'])] if 'shot_outcome' in opponent_shots.columns else opponent_shots
        shots_faced = int(shots_on_target.shape[0])
        saves = int(opponent_shots[opponent_shots.get('shot_outcome', '') == 'Saved'].shape[0]) if 'shot_outcome' in opponent_shots.columns else 0
        goals_conceded = int(opponent_shots[opponent_shots.get('shot_outcome', '') == 'Goal'].shape[0]) if 'shot_outcome' in opponent_shots.columns else 0
        clean_sheets = 1 if goals_conceded == 0 else 0
        xg_faced = float(shots_on_target['shot_statsbomb_xg'].fillna(0).sum()) if 'shot_statsbomb_xg' in shots_on_target.columns else 0.0
        goals_prevented = round(xg_faced - goals_conceded, 2)
        post_shot_xg = float(shots_on_target['shot_statsbomb_psxg'].fillna(0).sum()) if 'shot_statsbomb_psxg' in shots_on_target.columns else xg_faced
        psxg_plus_minus = round(goals_prevented, 2)

        sweeper_actions = 0
        try:
            if 'position' in events.columns:
                gk_events = events[(events['team'] == team_name) & events['position'].astype(str).str.contains('Goalkeeper', na=False)]
                sweeper_actions = int(gk_events[(gk_events['type'].isin(['Pressure', 'Tackle', 'Interception'])) & (gk_events['location'].apply(lambda x: isinstance(x, (list, tuple)) and len(x) >= 2 and x[0] < (self.pitch_length - 18) if 'location' in gk_events.columns else False))].shape[0])
        except Exception:
            sweeper_actions = 0
        return {
            'saves': saves,
            'shots_faced': shots_faced,
            'goals_conceded': goals_conceded,
            'clean_sheets': clean_sheets,
            'goals_prevented': round(goals_prevented, 2),
            'post_shot_xg_conceded': round(post_shot_xg, 2),
            'psxg_plus_minus': psxg_plus_minus,
            'sweeper_actions': sweeper_actions
        }

    # ----------------- Transition & Efficiency -----------------
    def compute_transition(self, events, team_name):
        counter_attacks = 0
        counter_attack_shots = 0
        press_to_attack = 0.0
        if 'possession' in events.columns:
            poss_groups = events.groupby('possession')
            dir_sign = self.infer_team_direction(events, team_name)
            for pid, grp in poss_groups:
                owner = grp['team'].mode().iat[0]
                if owner != team_name:
                    continue
                n_events = len(grp)
                start_x_val = grp.iloc[0].get('location', [np.nan, np.nan])
                start_x = start_x_val[0] if isinstance(start_x_val, list) and len(start_x_val) >= 1 else np.nan
                end_x_val = grp.iloc[-1].get('location', [np.nan, np.nan])
                end_x = end_x_val[0] if isinstance(end_x_val, list) and len(end_x_val) >= 1 else np.nan
                if pd.notna(start_x):
                    if dir_sign == 1:
                        defensive_third = start_x <= (self.pitch_length / 3)
                        opponent_final_third = pd.notna(end_x) and end_x >= (self.pitch_length * 2 / 3)
                    else:
                        defensive_third = start_x >= (self.pitch_length * 2 / 3)
                        opponent_final_third = pd.notna(end_x) and end_x <= (self.pitch_length / 3)
                else:
                    defensive_third = False
                    opponent_final_third = False
                if defensive_third and n_events <= 6:
                    if grp.iloc[-1]['type'] == 'Shot':
                        counter_attacks += 1
                        counter_attack_shots += 1
                    elif opponent_final_third:
                        counter_attacks += 1
            team_events = events[events['team'] == team_name]
            press_pos = team_events[team_events['type'] == 'Pressure']['possession'].dropna().unique()
            successful = 0
            for pid in press_pos:
                g = events[events['possession'] == pid]
                if any((g['team'] == team_name) & (g['type'] == 'Shot')):
                    successful += 1
            press_to_attack = round(min((successful / len(press_pos) * 100) if len(press_pos) > 0 else 0.0, 100.0), 1)
        return {
            'counter_attacks': int(counter_attacks),
            'counter_attack_shots': int(counter_attack_shots),
            'turnovers_to_shots': int(counter_attack_shots),
            'avg_attack_speed': 0.0,
            'press_to_attack_conversion': press_to_attack
        }

    def compute_efficiency(self, events, team_name, opponent_name):
        team_shots = events[(events['type'] == 'Shot') & (events['team'] == team_name)]
        opponent_shots = events[(events['type'] == 'Shot') & (events['team'] == opponent_name)]
        goals_scored = int(team_shots[team_shots.get('shot_outcome', '') == 'Goal'].shape[0]) if 'shot_outcome' in team_shots.columns else 0
        goals_conceded = int(opponent_shots[opponent_shots.get('shot_outcome', '') == 'Goal'].shape[0]) if 'shot_outcome' in opponent_shots.columns else 0
        total_shots = int(team_shots.shape[0])
        conversion_rate = round((goals_scored / total_shots * 100) if total_shots > 0 else 0.0, 1)
        team_xg = float(team_shots['shot_statsbomb_xg'].fillna(0).sum()) if 'shot_statsbomb_xg' in team_shots.columns else 0.0
        opponent_xg = float(opponent_shots['shot_statsbomb_xg'].fillna(0).sum()) if 'shot_statsbomb_xg' in opponent_shots.columns else 0.0
        xg_vs_goals_diff = round(goals_scored - team_xg, 2)
        xga_vs_conceded_diff = round(goals_conceded - opponent_xg, 2)
        return {
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'conversion_rate': conversion_rate,
            'xg_vs_goals_diff': xg_vs_goals_diff,
            'xga_vs_conceded_diff': xga_vs_conceded_diff
        }

    # ----------------- Extraction & flattening -----------------
    def extract_match_data(self, match_row, events):
        """Compute all metric groups for a single match.
        `match_row` can be a pandas Series or dict having keys: match_id, match_date, home_team, away_team.
        `events` must be the events DataFrame for that match.
        """
        match_id = match_row.get('match_id') if isinstance(match_row, dict) else match_row['match_id']
        match_date = match_row.get('match_date') if isinstance(match_row, dict) else match_row['match_date']
        home_team = match_row.get('home_team') if isinstance(match_row, dict) else match_row['home_team']
        away_team = match_row.get('away_team') if isinstance(match_row, dict) else match_row['away_team']

        print(f"Processing: {home_team} vs {away_team} (Match ID: {match_id})")

        # quick debug print of columns
        if not hasattr(self, '_columns_printed'):
            print("Event columns sample:", list(events.columns)[:40])
            print(f"Total events: {len(events)}")
            self._columns_printed = True

        possession = self.calculate_possession(events, home_team, away_team)
        passing = {
            'home_team': self.compute_passing_breakdowns(events, home_team),
            'away_team': self.compute_passing_breakdowns(events, away_team)
        }
        attacking = {
            'home_team': self.compute_shot_stats(events, home_team),
            'away_team': self.compute_shot_stats(events, away_team)
        }
        defensive = {
            'home_team': self.compute_defensive(events, home_team),
            'away_team': self.compute_defensive(events, away_team)
        }
        goalkeeper = {
            'home_team': self.compute_goalkeeper(events, home_team),
            'away_team': self.compute_goalkeeper(events, away_team)
        }
        transition = {
            'home_team': self.compute_transition(events, home_team),
            'away_team': self.compute_transition(events, away_team)
        }
        efficiency = {
            'home_team': self.compute_efficiency(events, home_team, away_team),
            'away_team': self.compute_efficiency(events, away_team, home_team)
        }

        match_data = {
            'match_id': match_id,
            'match_date': match_date,
            'home_team_name': home_team,
            'away_team_name': away_team,
            'possession': possession,
            'passing': passing,
            'attacking': attacking,
            'defensive': defensive,
            'goalkeeper': goalkeeper,
            'transition': transition,
            'efficiency': efficiency
        }
        return match_data

    def flatten_match_data(self, match_data):
        rows = []
        for team_type in ['home_team', 'away_team']:
            row = {
                'match_id': match_data['match_id'],
                'match_date': match_data['match_date'],
                'team_name': match_data[f'{team_type}_name'],
                'team_type': team_type,
                'opponent_name': match_data['away_team_name' if team_type == 'home_team' else 'home_team_name']
            }
            # possession is a top-level category with team keys
            row.update({f"possession_{k}": v for k, v in match_data['possession'][team_type].items()})

            for metric_category in ['passing', 'attacking', 'defensive', 'goalkeeper', 'transition', 'efficiency']:
                team_stats = match_data[metric_category][team_type]
                for stat_name, stat_value in team_stats.items():
                    row[f"{metric_category}_{stat_name}"] = stat_value
            rows.append(row)
        return rows

    # ----------------- Batch processing -----------------
    def process_all_matches(self, save_csv=None, only_group_stage=False, max_matches=None):
        """Process all matches in the configured competition/season and optionally save to CSV.
        - save_csv: path to CSV file to write (if None, will not save)
        - only_group_stage: if True, filter matches to group stage only (useful to limit scope)
        - max_matches: if set, process only the first N matches (useful for testing)
        Returns a DataFrame of flattened rows.
        """
        matches = self.get_matches()
        if matches is None:
            return None
        # optional filtering
        if only_group_stage and 'stage_name' in matches.columns:
            matches = matches[matches['stage_name'].str.contains('Group', na=False)]
        all_rows = []
        for idx, match_row in matches.iterrows():
            if max_matches is not None and idx >= max_matches:
                break
            try:
                match_id = match_row['match_id']
                events = self.get_match_events(match_id)
                if events is None:
                    continue
                # Clean events first (remove shootout/post-120, dedupe)
                cleaned = self.clean_events(events)
                match_data = self.extract_match_data(match_row, cleaned)
                rows = self.flatten_match_data(match_data)
                all_rows.extend(rows)
            except Exception as e:
                print(f"Error processing match {match_row.get('match_id')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        if not all_rows:
            print("No rows extracted.")
            return None
        df = pd.DataFrame(all_rows)
        if save_csv:
            df.to_csv(save_csv, index=False)
            print(f"Saved {len(df)} rows to {save_csv}")
        return df

    def process_single_match(self, match_id=None, match_row=None, save_csv=None):
        """Process a single match by match_id (or supply match_row dict/Series) and return DataFrame for two teams.
        If match_id provided, this will fetch events via statsbombpy.
        """
        if match_row is None:
            if match_id is None:
                raise ValueError("Provide match_id or match_row")
            matches = sb.matches(competition_id=self.competition_id, season_id=self.season_id)
            match_row = matches[matches['match_id'] == match_id].iloc[0].to_dict()
        events = self.get_match_events(match_row['match_id'])
        if events is None:
            return None
        # Clean events first (remove shootout/post-120, dedupe)
        cleaned = self.clean_events(events)
        match_data = self.extract_match_data(match_row, cleaned)
        rows = self.flatten_match_data(match_data)
        df = pd.DataFrame(rows)
        if save_csv:
            df.to_csv(save_csv, index=False)
            print(f"Saved {len(df)} rows to {save_csv}")
        return df


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Refactored StatsBomb World Cup extractor')
    parser.add_argument('--match-id', type=int, help='Process single match id (statsbomb match_id)')
    parser.add_argument('--save', type=str, help='CSV path to save results (optional)')
    parser.add_argument('--all', action='store_true', help='Process all matches in the configured competition/season')
    parser.add_argument('--max', type=int, default=None, help='Max matches to process (for testing)')
    # Check if running in Colab to handle potential system arguments
    if 'google.colab' in sys.modules:
        args = parser.parse_args([]) # Pass empty list to avoid parsing Colab args
    else:
        args = parser.parse_args()
    extractor = RefactoredWorldCupExtractor()
    if args.match_id:
        df = extractor.process_single_match(match_id=args.match_id, save_csv=args.save)
        if df is not None:
            print(df.head())
    elif args.all:
        df = extractor.process_all_matches(save_csv=args.save, max_matches=args.max)
        if df is not None:
            print(df.head())
    else:
        print('No action specified. Use --match-id MATCHID or --all to process.')

    # Instantiate the extractor
    extractor = RefactoredWorldCupExtractor()

    # Process all matches and save to CSV
    # The save_csv argument specifies the filename for the output CSV
    df_all_matches = extractor.process_all_matches(save_csv='worldcup_2022_match_data.csv')

    # Display the first few rows of the resulting DataFrame
    if df_all_matches is not None:
        print("\nDataFrame containing all match stats:")
        display(df_all_matches.head())
        print(f"\nData saved to worldcup_2022_match_data.csv")