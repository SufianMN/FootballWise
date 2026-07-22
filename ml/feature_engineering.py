"""
feature_engineering.py

Constructs historical rolling features for machine learning using a strict sliding window.
Ensures no future data leakage.
"""

import os
import pandas as pd
import numpy as np
from .config import PROCESSED_DIR, FEATURES_DIR

def prepare_team_match_logs(df_matches, df_stats):
    """
    Transforms match-level and stats data into a team-match log.
    Each row represents a team's performance in a single match.
    """
    # Merge home stats
    home_stats = df_stats.copy()
    home_stats = home_stats.rename(columns=lambda x: f"home_{x}" if x not in ['match_id', 'team_id'] else x)
    home_stats = home_stats.rename(columns={'team_id': 'home_team_id'})
    
    # Merge away stats
    away_stats = df_stats.copy()
    away_stats = away_stats.rename(columns=lambda x: f"away_{x}" if x not in ['match_id', 'team_id'] else x)
    away_stats = away_stats.rename(columns={'team_id': 'away_team_id'})
    
    df = df_matches.merge(home_stats, on=['match_id', 'home_team_id'], how='left')
    df = df.merge(away_stats, on=['match_id', 'away_team_id'], how='left')
    
    df['match_date'] = pd.to_datetime(df['match_date'])
    df = df.sort_values('match_date')
    
    team_logs = []
    for _, row in df.iterrows():
        # Home team perspective
        home_passes = row['home_total_passes'] if pd.notnull(row['home_total_passes']) else 0
        away_passes = row['away_total_passes'] if pd.notnull(row['away_total_passes']) else 0
        total_match_passes = home_passes + away_passes
        
        home_possession = (home_passes / total_match_passes * 100) if total_match_passes > 0 else 50.0
        away_possession = (away_passes / total_match_passes * 100) if total_match_passes > 0 else 50.0
        
        home_win = 1 if row['home_score'] > row['away_score'] else 0
        draw = 1 if row['home_score'] == row['away_score'] else 0
        away_win = 1 if row['away_score'] > row['home_score'] else 0
        
        btts = 1 if (row['home_score'] > 0 and row['away_score'] > 0) else 0
        
        team_logs.append({
            'match_id': row['match_id'],
            'match_date': row['match_date'],
            'team_id': row['home_team_id'],
            'is_home': 1,
            'opponent_id': row['away_team_id'],
            'goals_scored': row['home_score'],
            'goals_conceded': row['away_score'],
            'xg': row['home_xg'],
            'xga': row['away_xg'],
            'shots': row['home_shots'],
            'shots_on_target': row['home_shots_on_target'],
            'possession': home_possession,
            'pass_accuracy': row['home_pass_accuracy'],
            'corners': row['home_corners'],
            'yellow_cards': row['home_yellow_cards'],
            'red_cards': row['home_red_cards'],
            'win': home_win,
            'draw': draw,
            'loss': away_win,
            'clean_sheet': 1 if row['away_score'] == 0 else 0,
            'btts': btts
        })
        
        # Away team perspective
        team_logs.append({
            'match_id': row['match_id'],
            'match_date': row['match_date'],
            'team_id': row['away_team_id'],
            'is_home': 0,
            'opponent_id': row['home_team_id'],
            'goals_scored': row['away_score'],
            'goals_conceded': row['home_score'],
            'xg': row['away_xg'],
            'xga': row['home_xg'],
            'shots': row['away_shots'],
            'shots_on_target': row['away_shots_on_target'],
            'possession': away_possession,
            'pass_accuracy': row['away_pass_accuracy'],
            'corners': row['away_corners'],
            'yellow_cards': row['away_yellow_cards'],
            'red_cards': row['away_red_cards'],
            'win': away_win,
            'draw': draw,
            'loss': home_win,
            'clean_sheet': 1 if row['home_score'] == 0 else 0,
            'btts': btts
        })
        
    df_logs = pd.DataFrame(team_logs)
    df_logs = df_logs.sort_values('match_date')
    return df, df_logs

def get_team_features(team_id, current_date, df_logs, prefix=""):
    past_matches = df_logs[(df_logs['team_id'] == team_id) & (df_logs['match_date'] < current_date)]
    if len(past_matches) == 0:
        # Default values if no history
        return {f"{prefix}avg_goals_scored_l5": 0, f"{prefix}avg_goals_conceded_l5": 0, f"{prefix}win_rate_l5": 0}
        
    last_5 = past_matches.tail(5)
    
    features = {}
    features[f"{prefix}avg_goals_scored_l5"] = last_5['goals_scored'].mean()
    features[f"{prefix}avg_goals_conceded_l5"] = last_5['goals_conceded'].mean()
    features[f"{prefix}avg_xg_l5"] = last_5['xg'].mean()
    features[f"{prefix}avg_xga_l5"] = last_5['xga'].mean()
    features[f"{prefix}shots_per_game_l5"] = last_5['shots'].mean()
    features[f"{prefix}shots_on_target_l5"] = last_5['shots_on_target'].mean()
    features[f"{prefix}possession_l5"] = last_5['possession'].mean()
    features[f"{prefix}pass_accuracy_l5"] = last_5['pass_accuracy'].mean()
    features[f"{prefix}corners_l5"] = last_5['corners'].mean()
    features[f"{prefix}yellow_cards_l5"] = last_5['yellow_cards'].mean()
    features[f"{prefix}red_cards_l5"] = last_5['red_cards'].mean()
    
    features[f"{prefix}win_rate_l5"] = last_5['win'].mean()
    features[f"{prefix}clean_sheets_l5"] = last_5['clean_sheet'].sum()
    features[f"{prefix}btts_pct_l5"] = last_5['btts'].mean()
    
    # Form Streaks
    wins = list(past_matches['win'])
    winning_streak = 0
    for w in reversed(wins):
        if w == 1: winning_streak += 1
        else: break
    features[f"{prefix}winning_streak"] = winning_streak
    
    losses = list(past_matches['loss'])
    losing_streak = 0
    for l in reversed(losses):
        if l == 1: losing_streak += 1
        else: break
    features[f"{prefix}losing_streak"] = losing_streak
    
    unbeaten = list(past_matches['loss'])
    unbeaten_streak = 0
    for l in reversed(unbeaten):
        if l == 0: unbeaten_streak += 1
        else: break
    features[f"{prefix}unbeaten_streak"] = unbeaten_streak
    
    # Home/Away specific form
    past_home = past_matches[past_matches['is_home'] == 1]
    past_away = past_matches[past_matches['is_home'] == 0]
    
    features[f"{prefix}home_win_rate"] = past_home['win'].mean() if len(past_home) > 0 else 0
    features[f"{prefix}away_win_rate"] = past_away['win'].mean() if len(past_away) > 0 else 0
    
    # Rest Features
    days_since = (current_date - past_matches.iloc[-1]['match_date']).days
    features[f"{prefix}days_since_last_match"] = days_since
    
    last_14_days = current_date - pd.Timedelta(days=14)
    matches_in_14_days = len(past_matches[past_matches['match_date'] >= last_14_days])
    features[f"{prefix}matches_in_14_days"] = matches_in_14_days
    
    return features

def get_h2h_features(home_team_id, away_team_id, current_date, df_matches):
    past = df_matches[
        (df_matches['match_date'] < current_date) & 
        (
            ((df_matches['home_team_id'] == home_team_id) & (df_matches['away_team_id'] == away_team_id)) |
            ((df_matches['home_team_id'] == away_team_id) & (df_matches['away_team_id'] == home_team_id))
        )
    ]
    
    if len(past) == 0:
        return {'h2h_home_wins': 0, 'h2h_away_wins': 0, 'h2h_avg_goals': 0, 'h2h_avg_xg': 0}
        
    home_wins = 0
    away_wins = 0
    total_goals = 0
    total_xg = 0
    
    for _, row in past.iterrows():
        total_goals += row['home_score'] + row['away_score']
        total_xg += (row.get('home_xg', 0) + row.get('away_xg', 0))
        
        if row['home_team_id'] == home_team_id:
            if row['home_score'] > row['away_score']: home_wins += 1
            elif row['away_score'] > row['home_score']: away_wins += 1
        else:
            if row['home_score'] > row['away_score']: away_wins += 1
            elif row['away_score'] > row['home_score']: home_wins += 1
            
    features = {
        'h2h_home_wins': home_wins,
        'h2h_away_wins': away_wins,
        'h2h_avg_goals': total_goals / len(past),
        'h2h_avg_xg': total_xg / len(past)
    }
    return features

def engineer_features():
    print("Engineering features...")
    df_matches = pd.read_csv(os.path.join(PROCESSED_DIR, "processed_matches.csv"))
    df_stats = pd.read_csv(os.path.join(PROCESSED_DIR, "team_match_stats.csv"))
    
    df_matches['match_date'] = pd.to_datetime(df_matches['match_date'])
    df_full, df_logs = prepare_team_match_logs(df_matches, df_stats)
    
    dataset = []
    
    for _, row in df_full.iterrows():
        match_id = row['match_id']
        date = row['match_date']
        home_id = row['home_team_id']
        away_id = row['away_team_id']
        
        # Target Label
        if row['home_score'] > row['away_score']: label = 'Home Win'
        elif row['home_score'] == row['away_score']: label = 'Draw'
        else: label = 'Away Win'
        
        # Features
        home_features = get_team_features(home_id, date, df_logs, prefix="home_")
        away_features = get_team_features(away_id, date, df_logs, prefix="away_")
        h2h_features = get_h2h_features(home_id, away_id, date, df_full)
        
        record = {
            'match_id': match_id,
            'match_date': date,
            'home_team_id': home_id,
            'away_team_id': away_id,
            'competition_id': row.get('competition_id', None),
            'season_id': row.get('season_id', None)
        }
        record.update(home_features)
        record.update(away_features)
        record.update(h2h_features)
        record['result'] = label
        
        dataset.append(record)
        
    df_dataset = pd.DataFrame(dataset)
    df_dataset = df_dataset.fillna(0) # Fill nan generated by mean() of empty slices
    
    # Save
    df_dataset.to_csv(os.path.join(FEATURES_DIR, "match_dataset.csv"), index=False)
    print("Feature engineering complete. Dataset saved.")

if __name__ == "__main__":
    engineer_features()
