import os
import json
import pandas as pd
from collections import defaultdict
import glob

def build_dataset():
    print("Starting player dataset compilation...")

    base_dir = os.path.abspath(os.path.dirname(__file__))
    events_dir = os.path.join(base_dir, 'data', 'raw')
    matches_csv = os.path.join(base_dir, 'data', 'processed', 'processed_matches.csv')
    
    if not os.path.exists(matches_csv):
        raise FileNotFoundError(
            f"Required processed dataset missing: {matches_csv}\n"
            "Please ensure that the raw StatsBomb data has been processed "
            "by the preprocessing pipeline."
        )

    matches_df = pd.read_csv(matches_csv)
    match_meta = {}
    for _, row in matches_df.iterrows():
        match_meta[row['match_id']] = {
            'competition': row['competition'],
            'season': row['season']
        }

    player_stats = defaultdict(lambda: {
        'matches': 0, 'minutes_played': 0,
        'goals': 0, 'xg': 0.0, 'shots': 0, 'shots_on_target': 0,
        'assists': 0, 'xa': 0.0, 'key_passes': 0,
        'passes': 0, 'completed_passes': 0, 'progressive_passes': 0,
        'dribbles': 0, 'successful_dribbles': 0,
        'tackles': 0, 'interceptions': 0, 'clearances': 0,
        'yellow_cards': 0, 'red_cards': 0, 'fouls': 0,
        'positions': {} 
    })

    files = glob.glob(os.path.join(events_dir, 'events_*.json'))
    total = len(files)

    for idx, file_path in enumerate(files):
        if idx % 100 == 0:
            print(f"Processing {idx}/{total}")
        match_id = int(os.path.basename(file_path).split('_')[1].split('.')[0])
        meta = match_meta.get(match_id)
        if not meta:
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            events = json.load(f)
            
        seen_in_match = set()

        for e in events:
            player_info = e.get('player')
            if not player_info:
                continue
                
            team_name = e.get('team', {}).get('name', 'Unknown')
            player_id = player_info.get('id')
            player_name = player_info.get('name')
            comp = meta['competition']
            season = meta['season']
            
            key = (player_id, player_name, team_name, comp, season)
            stats = player_stats[key]
            
            if key not in seen_in_match:
                stats['matches'] += 1
                seen_in_match.add(key)
                
            pos = e.get('position', {}).get('name')
            if pos:
                stats['positions'][pos] = stats['positions'].get(pos, 0) + 1
                
            e_type = e.get('type', {}).get('name')
            
            if e_type == 'Pass':
                stats['passes'] += 1
                pass_info = e.get('pass', {})
                outcome = pass_info.get('outcome', {}).get('name')
                if not outcome:
                    stats['completed_passes'] += 1
                
                if pass_info.get('shot_assist'):
                    stats['key_passes'] += 1
                if pass_info.get('goal_assist'):
                    stats['assists'] += 1
                    
            elif e_type == 'Shot':
                stats['shots'] += 1
                shot_info = e.get('shot', {})
                stats['xg'] += shot_info.get('statsbomb_xg', 0.0)
                
                outcome = shot_info.get('outcome', {}).get('name')
                if outcome == 'Goal':
                    stats['goals'] += 1
                    stats['shots_on_target'] += 1
                elif outcome in ['Saved', 'Saved to Post', 'Saved Twice']:
                    stats['shots_on_target'] += 1
                    
            elif e_type == 'Dribble':
                stats['dribbles'] += 1
                outcome = e.get('dribble', {}).get('outcome', {}).get('name')
                if outcome == 'Complete':
                    stats['successful_dribbles'] += 1
                    
            elif e_type == 'Duel':
                duel_type = e.get('duel', {}).get('type', {}).get('name')
                outcome = e.get('duel', {}).get('outcome', {}).get('name')
                if duel_type == 'Tackle':
                    if outcome in ['Won', 'Success In Play', 'Success']:
                        stats['tackles'] += 1
                        
            elif e_type == 'Interception':
                outcome = e.get('interception', {}).get('outcome', {}).get('name')
                if outcome in ['Won', 'Success In Play', 'Success']:
                    stats['interceptions'] += 1
                    
            elif e_type == 'Clearance':
                stats['clearances'] += 1
                
            elif e_type == 'Foul Committed':
                stats['fouls'] += 1
                card = e.get('foul_committed', {}).get('card', {}).get('name')
                if card:
                    if 'Yellow' in card:
                        stats['yellow_cards'] += 1
                    elif 'Red' in card:
                        stats['red_cards'] += 1
                        
            elif e_type == 'Bad Behaviour':
                card = e.get('bad_behaviour', {}).get('card', {}).get('name')
                if card:
                    if 'Yellow' in card:
                        stats['yellow_cards'] += 1
                    elif 'Red' in card:
                        stats['red_cards'] += 1

    rows = []
    for (player_id, player_name, team_name, comp, season), stats in player_stats.items():
        pos = 'Unknown'
        if stats['positions']:
            pos = max(stats['positions'], key=stats['positions'].get)
            
        row = {
            'player_id': player_id,
            'player_name': player_name,
            'team_name': team_name,
            'competition': comp,
            'season': season,
            'position': pos,
            'matches': stats['matches'],
            'goals': stats['goals'],
            'xg': round(stats['xg'], 2),
            'shots': stats['shots'],
            'shots_on_target': stats['shots_on_target'],
            'assists': stats['assists'],
            'key_passes': stats['key_passes'],
            'passes': stats['passes'],
            'completed_passes': stats['completed_passes'],
            'dribbles': stats['dribbles'],
            'successful_dribbles': stats['successful_dribbles'],
            'tackles': stats['tackles'],
            'interceptions': stats['interceptions'],
            'clearances': stats['clearances'],
            'yellow_cards': stats['yellow_cards'],
            'red_cards': stats['red_cards'],
            'fouls': stats['fouls']
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    out_path = os.path.join(base_dir, 'data', 'processed', 'player_stats.csv')
    df.to_csv(out_path, index=False)
    print(f"Finished saving to {out_path}. Total rows: {len(df)}")

if __name__ == "__main__":
    build_dataset()
