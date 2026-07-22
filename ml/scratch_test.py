from statsbombpy import sb
import pandas as pd
events = sb.events(match_id=3795108, fmt='dict')
df = pd.DataFrame(list(events.values()))
print(df.columns)
if 'shot' in df.columns:
    shots = df.dropna(subset=['shot'])
    print("Shot example:", shots.iloc[0]['shot'])
if 'pass' in df.columns:
    passes = df.dropna(subset=['pass'])
    print("Pass example:", passes.iloc[0]['pass'])
