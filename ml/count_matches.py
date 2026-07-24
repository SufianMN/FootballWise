from statsbombpy import sb

comps = sb.competitions()
print("Total competitions:", len(comps))
total_matches = 0
for _, row in comps.iterrows():
    try:
        matches = sb.matches(competition_id=row['competition_id'], season_id=row['season_id'])
        total_matches += len(matches)
    except Exception as e:
        print(f"Error fetching matches for comp {row['competition_id']}, season {row['season_id']}")

print("Total matches:", total_matches)
