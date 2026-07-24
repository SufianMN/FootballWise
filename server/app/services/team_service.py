import pandas as pd
import os
import joblib

class TeamService:
    def __init__(self):
        self.teams_df = None
        self.matches_df = None
        self.stats_df = None
        self.team_names = {}

    def load_data(self):
        # Paths to ML artifacts
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml"))
        processed_dir = os.path.join(base_dir, "data/processed")
        features_dir = os.path.join(base_dir, "data/features")
        
        matches_path = os.path.join(processed_dir, "processed_matches.csv")
        dataset_path = os.path.join(features_dir, "match_dataset.csv")
        
        if os.path.exists(matches_path):
            self.matches_df = pd.read_csv(matches_path)
            # Create team ID to name mapping
            home_teams = self.matches_df[['home_team_id', 'home_team_name']].drop_duplicates()
            away_teams = self.matches_df[['away_team_id', 'away_team_name']].drop_duplicates()
            
            for _, row in home_teams.iterrows():
                if not pd.isna(row['home_team_id']):
                    self.team_names[str(int(row['home_team_id']))] = row['home_team_name']
            for _, row in away_teams.iterrows():
                if not pd.isna(row['away_team_id']):
                    self.team_names[str(int(row['away_team_id']))] = row['away_team_name']

        if os.path.exists(dataset_path):
            self.dataset_df = pd.read_csv(dataset_path)

    def get_all_teams(self):
        teams = [{"id": k, "name": v} for k, v in self.team_names.items()]
        # Sort alphabetically
        return sorted(teams, key=lambda x: x["name"])

    

    def get_team_stats(self, team_id: str):
        if not self.dataset_df is not None:
            return None
            
        tid = float(team_id)
        # Find latest matches for this team
        team_home = self.dataset_df[self.dataset_df['home_team_id'] == tid]
        team_away = self.dataset_df[self.dataset_df['away_team_id'] == tid]
        
        if len(team_home) == 0 and len(team_away) == 0:
            return None
            
        # Get the most recent match for this team (as home)
        latest_home = None
        latest_away = None
        
        if not team_home.empty:
            latest_home = team_home.sort_values(by='match_date', ascending=False).iloc[0]
        if not team_away.empty:
            latest_away = team_away.sort_values(by='match_date', ascending=False).iloc[0]
            
        # Determine the absolute most recent match to pull features from
        latest_row = None
        is_home = True
        
        if latest_home is not None and latest_away is not None:
            if latest_home['match_date'] >= latest_away['match_date']:
                latest_row = latest_home
                is_home = True
            else:
                latest_row = latest_away
                is_home = False
        elif latest_home is not None:
            latest_row = latest_home
            is_home = True
        else:
            latest_row = latest_away
            is_home = False
            
        prefix = "home_" if is_home else "away_"
        
        # Build the stats payload
        stats = {
            "id": team_id,
            "name": self.team_names.get(team_id, "Unknown"),
            "goals": round(latest_row[f"{prefix}avg_goals_scored_l5"], 2) if f"{prefix}avg_goals_scored_l5" in latest_row else 0,
            "xg": round(latest_row[f"{prefix}avg_xg_l5"], 2) if f"{prefix}avg_xg_l5" in latest_row else 0,
            "possession": round(latest_row[f"{prefix}possession_l5"], 2) if f"{prefix}possession_l5" in latest_row else 0,
            "passing_accuracy": round(latest_row[f"{prefix}pass_accuracy_l5"], 2) if f"{prefix}pass_accuracy_l5" in latest_row else 0,
            "defensive_rating": round(latest_row[f"{prefix}avg_goals_conceded_l5"], 2) if f"{prefix}avg_goals_conceded_l5" in latest_row else 0,
            "win_rate": round(latest_row[f"{prefix}win_rate_l5"], 2) if f"{prefix}win_rate_l5" in latest_row else 0,
            "clean_sheets": round(latest_row[f"{prefix}clean_sheets_l5"], 2) if f"{prefix}clean_sheets_l5" in latest_row else 0,
            "shots": round(latest_row[f"{prefix}shots_per_game_l5"], 2) if f"{prefix}shots_per_game_l5" in latest_row else 0,
            "recent_form": []  # We won't compute W/D/L array strictly for now, the win_rate handles this conceptually
        }
        
        return stats

team_service = TeamService()
