"""
preprocessing.py

Downloads StatsBomb Open Data competitions, matches, and events.
Cleans the data and extracts match-level statistics for each team.
"""

import os
import pandas as pd
from statsbombpy import sb
from .config import TARGET_COMPETITIONS, RAW_DIR, PROCESSED_DIR
from .utils import save_raw_json, load_raw_json, clean_column_names

def download_data():
    print("Downloading StatsBomb Open Data...")
    all_matches = []
    
    for comp_id, seasons in TARGET_COMPETITIONS.items():
        for season_id in seasons:
            print(f"Fetching matches for competition {comp_id}, season {season_id}...")
            matches = sb.matches(competition_id=comp_id, season_id=season_id, fmt='dict')
            if matches:
                matches_list = list(matches.values())
                all_matches.extend(matches_list)
                save_raw_json(matches_list, f"matches_{comp_id}_{season_id}.json")
            
            for match_id in matches.keys():
                events_file = f"events_{match_id}.json"
                if not os.path.exists(os.path.join(RAW_DIR, events_file)):
                    try:
                        events = sb.events(match_id=match_id, fmt='dict')
                        if events:
                            save_raw_json(list(events.values()), events_file)
                    except Exception as e:
                        print(f"Failed to fetch events for match {match_id}: {e}")
                        
    print("Download complete.")

def process_data():
    print("Processing raw JSON into structured Pandas DataFrames...")
    all_matches = []
    for comp_id, seasons in TARGET_COMPETITIONS.items():
        for season_id in seasons:
            matches = load_raw_json(f"matches_{comp_id}_{season_id}.json")
            if matches:
                all_matches.extend(matches)
                
    if not all_matches:
        print("No matches found.")
        return
        
    df_matches = pd.DataFrame(all_matches)
    df_matches = clean_column_names(df_matches)
    
    # Extract structural match info
    df_matches['home_team_id'] = df_matches['home_team'].apply(lambda x: x.get('home_team_id') if isinstance(x, dict) else None)
    df_matches['home_team_name'] = df_matches['home_team'].apply(lambda x: x.get('home_team_name') if isinstance(x, dict) else None)
    df_matches['away_team_id'] = df_matches['away_team'].apply(lambda x: x.get('away_team_id') if isinstance(x, dict) else None)
    df_matches['away_team_name'] = df_matches['away_team'].apply(lambda x: x.get('away_team_name') if isinstance(x, dict) else None)
    df_matches['home_score'] = df_matches['home_score'].fillna(0)
    df_matches['away_score'] = df_matches['away_score'].fillna(0)
    df_matches['match_date'] = pd.to_datetime(df_matches['match_date'])
    
    df_matches.to_csv(os.path.join(PROCESSED_DIR, "processed_matches.csv"), index=False)
    
    team_stats = []
    for match_id in df_matches['match_id'].dropna().unique():
        events = load_raw_json(f"events_{match_id}.json")
        if not events:
            continue
            
        df_events = pd.DataFrame(events)
        df_events = clean_column_names(df_events)
        
        # 1. Clean: Deduplicate events
        df_events = df_events.drop_duplicates(subset=['id'])
        
        # 2. Clean: Filter valid timestamps (has minute and second)
        df_events = df_events.dropna(subset=['minute', 'second'])
        
        # 3. Clean: Drop events missing team info
        df_events = df_events.dropna(subset=['team'])
        
        df_events['team_id'] = df_events['team'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
        df_events = df_events.dropna(subset=['team_id'])
        
        for team_id in df_events['team_id'].unique():
            team_events = df_events[df_events['team_id'] == team_id]
            
            # xG and Shots
            xg = 0.0
            total_shots = 0
            shots_on_target = 0
            if 'shot' in team_events.columns:
                shots = team_events.dropna(subset=['shot'])
                xg = shots['shot'].apply(lambda x: x.get('statsbomb_xg', 0.0) if isinstance(x, dict) else 0.0).sum()
                total_shots = len(shots)
                shots_on_target = len(shots[shots['shot'].apply(lambda x: x.get('outcome', {}).get('name') in ['Goal', 'Saved'] if isinstance(x, dict) else False)])
                
            # Passes and Possession metric proxy
            total_passes = 0
            completed_passes = 0
            corners = 0
            if 'pass' in team_events.columns:
                passes = team_events.dropna(subset=['pass'])
                total_passes = len(passes)
                completed_passes = len(passes[passes['pass'].apply(lambda x: 'outcome' not in x if isinstance(x, dict) else False)])
                corners = len(passes[passes['pass'].apply(lambda x: x.get('type', {}).get('name') == 'Corner' if isinstance(x, dict) else False)])
                
            pass_accuracy = (completed_passes / total_passes) if total_passes > 0 else 0
            
            # Cards
            yellow_cards = 0
            red_cards = 0
            if 'foul_committed' in team_events.columns:
                fouls = team_events.dropna(subset=['foul_committed'])
                yellow_cards = len(fouls[fouls['foul_committed'].apply(lambda x: x.get('card', {}).get('name') == 'Yellow Card' if isinstance(x, dict) else False)])
                red_cards = len(fouls[fouls['foul_committed'].apply(lambda x: x.get('card', {}).get('name') == 'Red Card' if isinstance(x, dict) else False)])
                
            if 'bad_behaviour' in team_events.columns:
                bb = team_events.dropna(subset=['bad_behaviour'])
                yellow_cards += len(bb[bb['bad_behaviour'].apply(lambda x: x.get('card', {}).get('name') == 'Yellow Card' if isinstance(x, dict) else False)])
                red_cards += len(bb[bb['bad_behaviour'].apply(lambda x: x.get('card', {}).get('name') == 'Red Card' if isinstance(x, dict) else False)])

            team_stats.append({
                'match_id': match_id,
                'team_id': team_id,
                'xg': xg,
                'shots': total_shots,
                'shots_on_target': shots_on_target,
                'total_passes': total_passes,
                'completed_passes': completed_passes,
                'pass_accuracy': pass_accuracy,
                'yellow_cards': yellow_cards,
                'red_cards': red_cards,
                'corners': corners
            })
            
    df_stats = pd.DataFrame(team_stats)
    df_stats.to_csv(os.path.join(PROCESSED_DIR, "team_match_stats.csv"), index=False)
    print("Processing complete. Summaries saved.")

if __name__ == "__main__":
    download_data()
    process_data()
