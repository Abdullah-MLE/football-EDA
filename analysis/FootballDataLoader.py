# analysis/data_loader.py

from typing import Optional, Dict, Any
from statsbombpy import sb
import pandas as pd
import os


class FootballDataLoader:
    def __init__(self):
        """Initialize the FootballDataLoader with competitions data."""
        self.competitions = sb.competitions()

    def get_matches_data(self, competition_name: str, season: str) -> Optional[pd.DataFrame]:
        """
        Get matches data for a specific competition and season.
        
        Args:
            competition_name (str): Name of the competition
            season (str): Season name (e.g., "2020/2021")
            
        Returns:
            Optional[pd.DataFrame]: Matches dataframe or None if not found
        """
        try:
            # Find competition and season IDs
            mask = (
                self.competitions['competition_name'].str.contains(competition_name, case=False, na=False) &
                (self.competitions['season_name'] == season)
            )
            filtered = self.competitions[mask]
            
            if filtered.empty:
                print(f"No data found for {competition_name} - {season}")
                return None
            
            row = filtered.iloc[0]
            matches = sb.matches(competition_id=row['competition_id'], season_id=row['season_id'])
            
            return matches if not matches.empty else None
        
        except Exception as e:
            print(f"Error getting matches data: {e}")
            return None

    def get_events_data(self, match_id: int) -> Optional[pd.DataFrame]:
        """
        Get events data for a specific match.
        
        Args:
            match_id (int): Match ID
            
        Returns:
            Optional[pd.DataFrame]: Events dataframe or None if not found
        """
        try:
            events = sb.events(match_id=match_id)
            return events if not events.empty else None
        
        except Exception as e:
            print(f"Error getting events data for match {match_id}: {e}")
            return None

    def get_lineups_data(self, match_id: int) -> Optional[pd.DataFrame]:
        """
        Get lineups data for a specific match.
        
        Args:
            match_id (int): Match ID
            
        Returns:
            Optional[pd.DataFrame]: Lineups dataframe or None if not found
        """
        try:
            lineups = sb.lineups(match_id=match_id)
            return lineups if not lineups.empty else None
        
        except Exception as e:
            print(f"Error getting lineups data for match {match_id}: {e}")
            return None

    def get_360_data(self, match_id: int) -> Optional[pd.DataFrame]:
        """
        Get 360 tracking data for a specific match.
        
        Args:
            match_id (int): Match ID
            
        Returns:
            Optional[pd.DataFrame]: 360 data or None if not available
        """
        try:
            data_360 = sb.frames(match_id=match_id)
            return data_360 if not data_360.empty else None
        
        except Exception as e:
            print(f"Error getting 360 data for match {match_id}: {e}")
            return None

    def get_matches_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics about available data.
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        try:
            return {
                'total_competition_seasons': len(self.competitions),
                'unique_competitions': self.competitions['competition_name'].nunique(),
                'unique_seasons': self.competitions['season_name'].nunique(),
                'competitions': sorted(self.competitions['competition_name'].unique().tolist()),
                'seasons': sorted(self.competitions['season_name'].unique().tolist())
            }
        
        except Exception as e:
            print(f"Error getting summary stats: {e}")
            return {}

    def generate_matches_index_csv(self, output_path: str = "data/matches_index.csv") -> bool:
        """
        Generate CSV file with all matches from all competitions and seasons.
        
        Args:
            output_path (str): Output file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("Generating matches index CSV...")
            
            # Create output directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            all_matches = []
            total_rows = len(self.competitions)
            
            # Process each competition-season combination
            for idx, row in self.competitions.iterrows():
                comp_name = row['competition_name']
                season_name = row['season_name']
                
                print(f"Processing ({idx+1}/{total_rows}): {comp_name} - {season_name}")
                
                try:
                    matches = sb.matches(
                        competition_id=row['competition_id'], 
                        season_id=row['season_id']
                    )
                    
                    if not matches.empty:
                        for _, match in matches.iterrows():
                            all_matches.append({
                                'match_id': match['match_id'],
                                'competition': comp_name,
                                'season': season_name,
                                'team1': match['home_team'],
                                'team2': match['away_team'],
                                'match_date': match.get('match_date', ''),
                                'home_score': match.get('home_score', ''),
                                'away_score': match.get('away_score', ''),
                                'competition_stage': match.get('competition_stage', ''),
                                'match_week': match.get('match_week', '')
                            })
                        
                        print(f"  Added {len(matches)} matches")
                    
                except Exception as e:
                    print(f"  Error: {e}")
                    continue
            
            # Save to CSV
            if all_matches:
                df = pd.DataFrame(all_matches)
                df = df.sort_values(['competition', 'season', 'match_date']).reset_index(drop=True)
                df.to_csv(output_path, index=False)
                
                print(f"\n✅ CSV generated successfully!")
                print(f"📁 Saved to: {output_path}")
                print(f"📊 Total matches: {len(df)}")
                print(f"🏆 Competitions: {df['competition'].nunique()}")
                
                return True
            else:
                print("❌ No matches found")
                return False
        
        except Exception as e:
            print(f"❌ Error generating CSV: {e}")
            return False

    def generate_matches_index_csv_first_competition_for_test(self, output_path: str = "data/matches_index.csv") -> bool:
        """
        Generate a CSV file with all matches from the FIRST competition only.
        This is a faster implementation for quick testing.
        """
        try:
            print("Generating matches index CSV for the first competition...")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            all_matches = []
            
            # Get the first competition only (index 0)
            row = self.competitions.iloc[0]
            
            try:
                # Get all matches for the first competition
                matches = sb.matches(
                    competition_id=row['competition_id'], 
                    season_id=row['season_id']
                )
                
                if not matches.empty:
                    batch_matches = []
                    for _, match in matches.iterrows():
                        batch_matches.append({
                            'match_id': match['match_id'],
                            'competition': row['competition_name'],
                            'season': row['season_name'],
                            'home_team': match['home_team'],
                            'away_team': match['away_team'],
                            'home_score': match.get('home_score', ''),
                            'away_score': match.get('away_score', ''),
                            'match_date': match.get('match_date', '')
                        })
                    all_matches.extend(batch_matches)
                
            except Exception as e:
                # If there's an error getting matches for this competition, print it and return False
                print(f"❌ Error getting matches for the first competition: {e}")
                return False
            
            # Save and summarize
            if all_matches:
                df = pd.DataFrame(all_matches)
                df.to_csv(output_path, index=False)
                print(f"✅ Done! {len(df)} matches saved to {output_path}")
                return True
            else:
                print("❌ No matches found for the first competition.")
                return False
        
        except Exception as e:
            print(f"❌ A major error occurred: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize loader
    loader = FootballDataLoader()

    df = loader.get_360_data(3890264)
    df.to_csv("data/360_test.csv", index=False)
    
    # # Generate matches index CSV
    # loader.generate_matches_index_csv()
    
    # # Get summary stats
    # stats = loader.get_matches_summary_stats()
    # print(f"\nSummary: {stats}")
    
    # # Example: Get specific match data
    # matches = loader.get_matches_data("Premier League", "2020/2021")
    # if matches is not None:
    #     print(f"\nPremier League 2020/2021: {len(matches)} matches")
        
    #     # Get events for first match
    #     first_match_id = matches.iloc[0]['match_id']
    #     events = loader.get_events_data(first_match_id)
    #     lineups = loader.get_lineups_data(first_match_id)
    #     data_360 = loader.get_360_data(first_match_id)
        
    #     print(f"Match {first_match_id}:")
    #     print(f"  Events: {len(events) if events is not None else 'None'}")
    #     print(f"  Lineups: {len(lineups) if lineups is not None else 'None'}")
    #     print(f"  360 Data: {len(data_360) if data_360 is not None else 'None'}")