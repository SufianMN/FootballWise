import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.ai.tools import (
    predict_match,
    explain_match_prediction,
    get_team_stats,
    get_player_stats,
    compare_players_tool,
    search_match_history,
)
from app.ai.graph import run_football_agent


class TestFootballWiseAI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app.services.team_service import team_service
        from app.services.player_service import player_service
        from app.services.feature_builder_service import feature_builder_service
        from app.services.prediction_service import prediction_service
        from app.services.explainability_service import explainability_service

        team_service.load_data()
        player_service.load_data()
        feature_builder_service.load_data()
        prediction_service.load_model()
        if prediction_service.model is not None:
            explainability_service.initialize(prediction_service.model)

    def setUp(self):
        self.client = TestClient(app)


    # 1. Existing Endpoints Non-Breaking Test
    def test_existing_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")

    def test_existing_teams_endpoint(self):
        response = self.client.get("/teams")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)

    # 2. Tool Unit Tests
    def test_predict_match_tool(self):
        res = predict_match.invoke({"home_team": "Barcelona", "away_team": "Real Madrid"})
        self.assertIsInstance(res, dict)
        if "error" not in res:
            self.assertIn("predicted_result", res)
            self.assertIn("confidence", res)

    def test_explain_match_prediction_tool(self):
        res = explain_match_prediction.invoke({"home_team": "Barcelona", "away_team": "Real Madrid"})
        self.assertIsInstance(res, dict)
        if "error" not in res:
            self.assertIn("top_shap_features", res)
            self.assertIn("tactical_insights", res)

    def test_get_team_stats_tool(self):
        res = get_team_stats.invoke({"team_name": "Barcelona"})
        self.assertIsInstance(res, dict)

    def test_get_player_stats_tool(self):
        res = get_player_stats.invoke({"player_name": "Messi"})
        self.assertIsInstance(res, dict)

    def test_compare_players_tool(self):
        res = compare_players_tool.invoke({"player1_name": "Messi", "player2_name": "Busquets"})
        self.assertIsInstance(res, dict)

    def test_search_match_history_tool(self):
        res = search_match_history.invoke({"query": "Barcelona goals"})
        self.assertIsInstance(res, str)

    # 3. LangGraph Workflow Unconfigured / Mock Test
    def test_agent_unconfigured_mode(self):
        with patch("app.ai.graph.is_llm_configured", return_value=False):
            res = run_football_agent("Predict Barcelona vs Real Madrid")
            self.assertTrue(res.get("unconfigured"))
            self.assertIn("unconfigured mode", res.get("response", ""))

    # 4. FastAPI AI Route Endpoint Test
    def test_ai_chat_endpoint_empty_prompt(self):
        response = self.client.post("/api/ai/chat", json={"message": ""})
        self.assertEqual(response.status_code, 400)

    def test_ai_chat_endpoint_unconfigured(self):
        with patch("app.ai.graph.is_llm_configured", return_value=False):
            response = self.client.post("/api/ai/chat", json={"message": "Predict Barcelona vs Real Madrid"})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("response", data)
            self.assertTrue(data.get("unconfigured"))


if __name__ == "__main__":
    unittest.main()
