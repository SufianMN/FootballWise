from .analytics_service import analytics_service


class MatchPreviewService:
    def generate_preview(self, home_team_id: str, away_team_id: str):
        # Ensure analytics data is loaded
        if analytics_service.df_logs is None:
            analytics_service.load_data()

        if analytics_service.df_logs is None:
            return {}

        tid1, tid2 = float(home_team_id), float(away_team_id)
        df_logs = analytics_service.df_logs

        home_df = df_logs[df_logs["team_id"] == tid1].sort_values("match_date")
        away_df = df_logs[df_logs["team_id"] == tid2].sort_values("match_date")

        # Get last 5 matches for each
        home_l5 = home_df.tail(5)
        away_l5 = away_df.tail(5)

        def _get_form_string(df_l5):
            form = ""
            for _, row in df_l5.iterrows():
                if row["win"] == 1:
                    form += "W"
                elif row["draw"] == 1:
                    form += "D"
                else:
                    form += "L"
            return form

        home_form = _get_form_string(home_l5)
        away_form = _get_form_string(away_l5)

        home_avg_goals = (
            round(float(home_l5["goals_scored"].mean()), 2) if len(home_l5) > 0 else 0
        )
        away_avg_goals = (
            round(float(away_l5["goals_scored"].mean()), 2) if len(away_l5) > 0 else 0
        )

        home_avg_xg = round(float(home_l5["xg"].mean()), 2) if len(home_l5) > 0 else 0
        away_avg_xg = round(float(away_l5["xg"].mean()), 2) if len(away_l5) > 0 else 0

        home_cs = int(home_l5["clean_sheet"].sum())
        away_cs = int(away_l5["clean_sheet"].sum())

        # Calculate H2H wins
        # A H2H match is where tid1 plays tid2. We can find this by checking matches where tid1 played and goals scored/conceded vs tid2.
        # Actually analytics_service.df_logs does not have opponent_team_id by default.
        # Let's check team_service.matches_df instead for H2H.
        from .team_service import team_service

        if team_service.matches_df is None:
            team_service.load_data()

        h2h_home_wins = 0
        h2h_away_wins = 0

        if team_service.matches_df is not None:
            matches = team_service.matches_df
            # Home team wins: (home_team == tid1 and home_score > away_score) OR (away_team == tid1 and away_score > home_score)
            h2h_matches = matches[
                ((matches["home_team_id"] == tid1) & (matches["away_team_id"] == tid2))
                | (
                    (matches["home_team_id"] == tid2)
                    & (matches["away_team_id"] == tid1)
                )
            ]

            for _, m in h2h_matches.iterrows():
                if m["home_score"] > m["away_score"]:
                    if m["home_team_id"] == tid1:
                        h2h_home_wins += 1
                    else:
                        h2h_away_wins += 1
                elif m["away_score"] > m["home_score"]:
                    if m["away_team_id"] == tid1:
                        h2h_home_wins += 1
                    else:
                        h2h_away_wins += 1

        return {
            "home_form": home_form,
            "away_form": away_form,
            "home_avg_goals": home_avg_goals,
            "away_avg_goals": away_avg_goals,
            "home_avg_xg": home_avg_xg,
            "away_avg_xg": away_avg_xg,
            "home_clean_sheets": home_cs,
            "away_clean_sheets": away_cs,
            "h2h_home_wins": h2h_home_wins,
            "h2h_away_wins": h2h_away_wins,
        }


match_preview_service = MatchPreviewService()
