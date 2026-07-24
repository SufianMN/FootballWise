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

def get_target_competitions():
    if TARGET_COMPETITIONS == 'ALL':
        print("Fetching list of ALL available competitions...")
        import time
        for attempt in range(5):
            try:
                comps_df = sb.competitions()
                break
            except Exception as e:
                print(f"Network error fetching competitions (attempt {attempt+1}): {e}")
                time.sleep(2)
        else:
            raise Exception("Failed to fetch competitions after 5 attempts.")
            
        targets = {}
        for _, row in comps_df.iterrows():
            cid = row['competition_id']
            sid = row['season_id']
            if cid not in targets:
                targets[cid] = []
            targets[cid].append(sid)
        return targets
    return TARGET_COMPETITIONS

def download_data():
    print("Downloading StatsBomb Open Data...")
    targets = get_target_competitions()
    
    total_matches_downloaded = 0
    total_events_downloaded = 0
    
    for comp_id, seasons in targets.items():
        for season_id in seasons:
            match_cache_file = f"matches_{comp_id}_{season_id}.json"
            
            matches = {}
            if os.path.exists(os.path.join(RAW_DIR, match_cache_file)):
                print(f"Loading cached matches for comp {comp_id}, season {season_id}...")
                matches_list = load_raw_json(match_cache_file)
                if matches_list:
                    # Convert list back to dictionary with match_id as key for iteration
                    matches = {str(m.get('match_id', '')): m for m in matches_list if 'match_id' in m}
            else:
                print(f"Fetching matches for competition {comp_id}, season {season_id}...")
                try:
                    matches = sb.matches(competition_id=comp_id, season_id=season_id, fmt='dict')
                    if matches:
                        matches_list = list(matches.values())
                        save_raw_json(matches_list, match_cache_file)
                        total_matches_downloaded += len(matches_list)
                except Exception as e:
                    print(f"Failed to fetch matches for comp {comp_id}, season {season_id}: {e}")
                    continue
            
            # Fetch events for each match
            for match_id in matches.keys():
                events_file = f"events_{match_id}.json"
                if not os.path.exists(os.path.join(RAW_DIR, events_file)):
                    try:
                        events = sb.events(match_id=match_id, fmt='dict')
                        if events:
                            save_raw_json(list(events.values()), events_file)
                            total_events_downloaded += 1
                    except Exception as e:
                        print(f"Failed to fetch events for match {match_id}: {e}")
                        
    print(f"Download complete. Fetched {total_matches_downloaded} new matches and {total_events_downloaded} new event logs.")

def process_data():
    print("Processing raw JSON into structured Pandas DataFrames...")
    
    all_matches = []
    # Scan RAW_DIR for all matches_*.json files instead of relying on the API
    for filename in os.listdir(RAW_DIR):
        if filename.startswith("matches_") and filename.endswith(".json"):
            matches = load_raw_json(filename)
            if matches:
                all_matches.extend(matches)
                
    if not all_matches:
        print("No matches found in cache.")
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
    
    # Deduplicate matches just in case
    df_matches = df_matches.drop_duplicates(subset=['match_id'])
    
    df_matches.to_csv(os.path.join(PROCESSED_DIR, "processed_matches.csv"), index=False)
    
    team_stats = []
    total_processed = 0
    total_matches_df = len(df_matches)
    
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
            
        total_processed += 1
        if total_processed % 100 == 0:
            print(f"Processed {total_processed}/{total_matches_df} matches...")
            
    df_stats = pd.DataFrame(team_stats)
    df_stats.to_csv(os.path.join(PROCESSED_DIR, "team_match_stats.csv"), index=False)
    print("Processing complete. Summaries saved.")

if __name__ == "__main__":
    download_data()
    process_data()
