import os
import pandas as pd
import numpy as np
import ast
import json
from ..utils.helpers import convert_numpy_types

class MatchService:
    def __init__(self):
        self.df_matches = None
        self.raw_dir = None

    def load_data(self):
        print("Loading match explorer data...")
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml"))
        processed_dir = os.path.join(base_dir, "data/processed")
        self.raw_dir = os.path.join(base_dir, "data/raw")
        
        matches_path = os.path.join(processed_dir, "processed_matches.csv")
        stats_path = os.path.join(processed_dir, "team_match_stats.csv")
        
        if not os.path.exists(matches_path) or not os.path.exists(stats_path):
            print("Match data missing!")
            return
            
        df_m = pd.read_csv(matches_path)
        df_stats = pd.read_csv(stats_path)
        
        # Parse Competition and Season from string representations
        parsed_comps = []
        parsed_seasons = []
        for idx, row in df_m.iterrows():
            comp_dict = ast.literal_eval(row['competition']) if pd.notnull(row['competition']) else {}
            season_dict = ast.literal_eval(row['season']) if pd.notnull(row['season']) else {}
            
            comp_name = comp_dict.get('competition_name', 'Unknown')
            season_name = season_dict.get('season_name', 'Unknown')
            
            parsed_comps.append(comp_name)
            parsed_seasons.append(season_name)
            
        df_m['comp_name'] = parsed_comps
        df_m['season_name'] = parsed_seasons
        
        # Merge stats
        home_stats = df_stats.copy()
        home_stats = home_stats.rename(columns=lambda x: f"home_{x}" if x not in ['match_id', 'team_id'] else x)
        home_stats = home_stats.rename(columns={'team_id': 'home_team_id'})
        
        away_stats = df_stats.copy()
        away_stats = away_stats.rename(columns=lambda x: f"away_{x}" if x not in ['match_id', 'team_id'] else x)
        away_stats = away_stats.rename(columns={'team_id': 'away_team_id'})
        
        df = df_m.merge(home_stats, on=['match_id', 'home_team_id'], how='left')
        df = df.merge(away_stats, on=['match_id', 'away_team_id'], how='left')
        
        df['match_date'] = pd.to_datetime(df['match_date']).dt.strftime('%Y-%m-%d')
        
        self.df_matches = df.fillna(0)
        print("Match Explorer data successfully cached.")

    def search_matches(self, competition: str = None, season: str = None, team: str = None, date: str = None, page: int = 1, page_size: int = 20, sort: str = "desc"):
        if self.df_matches is None:
            return {"total": 0, "page": page, "page_size": page_size, "matches": []}
            
        df = self.df_matches.copy()
        
        if competition:
            df = df[df['comp_name'].str.contains(competition, case=False, na=False)]
        if season:
            df = df[df['season_name'].str.contains(season, case=False, na=False)]
        if team:
            df = df[(df['home_team_name'].str.contains(team, case=False, na=False)) | (df['away_team_name'].str.contains(team, case=False, na=False))]
        if date:
            df = df[df['match_date'] == date]
            
        if sort == "desc":
            df = df.sort_values(by='match_date', ascending=False)
        else:
            df = df.sort_values(by='match_date', ascending=True)
            
        total = len(df)
        start = (page - 1) * page_size
        end = start + page_size
        
        df_page = df.iloc[start:end]
        
        matches = []
        for _, row in df_page.iterrows():
            winner = None
            if row['home_score'] > row['away_score']: winner = row['home_team_name']
            elif row['away_score'] > row['home_score']: winner = row['away_team_name']
            else: winner = "Draw"
            
            matches.append({
                "match_id": row['match_id'],
                "date": row['match_date'],
                "competition": row['comp_name'],
                "season": row['season_name'],
                "home_team": row['home_team_name'],
                "away_team": row['away_team_name'],
                "score": f"{int(row['home_score'])} - {int(row['away_score'])}",
                "home_xg": round(float(row.get('home_xg', 0)), 2),
                "away_xg": round(float(row.get('away_xg', 0)), 2),
                "winner": winner
            })
            
        return convert_numpy_types({
            "total": total,
            "page": page,
            "page_size": page_size,
            "matches": matches
        })

    def get_match_details(self, match_id: int):
        if self.df_matches is None:
            return None
            
        matches = self.df_matches[self.df_matches['match_id'] == match_id]
        if len(matches) == 0:
            return None
            
        row = matches.iloc[0]
        
        # Load events
        events = []
        events_file = os.path.join(self.raw_dir, f"events_{match_id}.json")
        if os.path.exists(events_file):
            try:
                with open(events_file, 'r', encoding='utf-8') as f:
                    raw_events = json.load(f)
                    for ev in raw_events:
                        ev_type = ev.get('type', {}).get('name', '')
                        
                        # Goals & Own Goals
                        if ev_type == 'Shot' and ev.get('shot', {}).get('outcome', {}).get('name') == 'Goal':
                            desc = 'Goal'
                            if ev.get('shot', {}).get('type', {}).get('name') == 'Penalty':
                                desc = 'Penalty Goal'
                            events.append({
                                'minute': ev.get('minute', 0),
                                'team': ev.get('team', {}).get('name', 'Unknown'),
                                'player': ev.get('player', {}).get('name', 'Unknown'),
                                'type': desc,
                                'description': desc
                            })
                        elif ev_type == 'Shot' and ev.get('shot', {}).get('outcome', {}).get('name') in ['Saved', 'Off T', 'Post', 'Wayward'] and ev.get('shot', {}).get('type', {}).get('name') == 'Penalty':
                            events.append({
                                'minute': ev.get('minute', 0),
                                'team': ev.get('team', {}).get('name', 'Unknown'),
                                'player': ev.get('player', {}).get('name', 'Unknown'),
                                'type': 'Missed Penalty',
                                'description': 'Missed Penalty'
                            })
                        elif ev_type == 'Own Goal For' or ev_type == 'Own Goal Against':
                            # Statsbomb handles own goals weirdly, let's just catch Bad Behaviour/Foul with cards
                            pass
                            
                        # Cards
                        if 'foul_committed' in ev and 'card' in ev['foul_committed']:
                            card_type = ev['foul_committed']['card']['name']
                            events.append({
                                'minute': ev.get('minute', 0),
                                'team': ev.get('team', {}).get('name', 'Unknown'),
                                'player': ev.get('player', {}).get('name', 'Unknown'),
                                'type': card_type,
                                'description': card_type
                            })
                        elif 'bad_behaviour' in ev and 'card' in ev['bad_behaviour']:
                            card_type = ev['bad_behaviour']['card']['name']
                            events.append({
                                'minute': ev.get('minute', 0),
                                'team': ev.get('team', {}).get('name', 'Unknown'),
                                'player': ev.get('player', {}).get('name', 'Unknown'),
                                'type': card_type,
                                'description': card_type
                            })
                            
                        # Substitutions
                        if ev_type == 'Substitution':
                            sub_out = ev.get('player', {}).get('name', 'Unknown')
                            sub_in = ev.get('substitution', {}).get('replacement', {}).get('name', 'Unknown')
                            events.append({
                                'minute': ev.get('minute', 0),
                                'team': ev.get('team', {}).get('name', 'Unknown'),
                                'player': sub_in,
                                'type': 'Substitution',
                                'description': f"In: {sub_in}, Out: {sub_out}"
                            })
                            
            except Exception as e:
                print(f"Error parsing events for match {match_id}: {e}")
                
        # Sort events
        events = sorted(events, key=lambda x: x['minute'])
        
        home_passes = row.get('home_total_passes', 0)
        away_passes = row.get('away_total_passes', 0)
        total_passes = home_passes + away_passes
        home_poss = round((home_passes / total_passes * 100) if total_passes > 0 else 50, 1)
        away_poss = round((away_passes / total_passes * 100) if total_passes > 0 else 50, 1)
        
        home_xg = round(float(row.get('home_xg', 0)), 2)
        away_xg = round(float(row.get('away_xg', 0)), 2)
        home_shots = int(row.get('home_shots', 0))
        away_shots = int(row.get('away_shots', 0))
        
        # Summary Generator
        summary_sentences = []
        if home_poss > 60:
            summary_sentences.append(f"{row['home_team_name']} dominated possession ({home_poss}%).")
        elif away_poss > 60:
            summary_sentences.append(f"{row['away_team_name']} dominated possession ({away_poss}%).")
        else:
            summary_sentences.append(f"Possession was evenly contested ({home_poss}% - {away_poss}%).")
            
        if home_xg > away_xg and row['home_score'] <= row['away_score']:
            summary_sentences.append(f"{row['home_team_name']} generated more expected goals ({home_xg} xG) but failed to secure the win.")
        elif away_xg > home_xg and row['away_score'] <= row['home_score']:
            summary_sentences.append(f"{row['away_team_name']} generated more expected goals ({away_xg} xG) but failed to secure the win.")
        
        if (home_xg + away_xg) > 3.5:
            summary_sentences.append("Both teams created numerous high-quality chances in an open game.")
        elif (home_xg + away_xg) < 1.5:
            summary_sentences.append("It was a tight, defensive affair with few clear-cut opportunities.")
            
        if len(summary_sentences) == 1:
            summary_sentences.append(f"The match ended {int(row['home_score'])}-{int(row['away_score'])}.")
            
        summary = " ".join(summary_sentences)
        
        result = {
            "match_id": match_id,
            "competition": row['comp_name'],
            "season": row['season_name'],
            "date": row['match_date'],
            "home_team": row['home_team_name'],
            "away_team": row['away_team_name'],
            "score": {
                "home": int(row['home_score']),
                "away": int(row['away_score'])
            },
            "statistics": {
                "home": {
                    "goals": int(row['home_score']),
                    "xg": home_xg,
                    "shots": home_shots,
                    "shots_on_target": int(row.get('home_shots_on_target', 0)),
                    "possession": home_poss,
                    "pass_accuracy": round(float(row.get('home_pass_accuracy', 0)), 1),
                    "corners": int(row.get('home_corners', 0)),
                    "yellow_cards": int(row.get('home_yellow_cards', 0)),
                    "red_cards": int(row.get('home_red_cards', 0)),
                },
                "away": {
                    "goals": int(row['away_score']),
                    "xg": away_xg,
                    "shots": away_shots,
                    "shots_on_target": int(row.get('away_shots_on_target', 0)),
                    "possession": away_poss,
                    "pass_accuracy": round(float(row.get('away_pass_accuracy', 0)), 1),
                    "corners": int(row.get('away_corners', 0)),
                    "yellow_cards": int(row.get('away_yellow_cards', 0)),
                    "red_cards": int(row.get('away_red_cards', 0)),
                }
            },
            "events": events,
            "summary": summary
        }
        return convert_numpy_types(result)

match_service = MatchService()
