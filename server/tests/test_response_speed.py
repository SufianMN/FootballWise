import sys
import time
import unittest
from app.services.feature_builder_service import feature_builder_service
from app.services.prediction_service import prediction_service
from app.services.team_service import team_service
from app.services.player_service import player_service
from app.ai.graph import run_football_agent


class TestSpeedAndFormatting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.stdout.reconfigure(encoding="utf-8")
        team_service.load_data()
        player_service.load_data()
        feature_builder_service.load_data()
        prediction_service.load_model()

    def tearDown(self):
        # Pause 2s between rapid automated queries to observe Groq free tier RPM limits
        time.sleep(2.0)

    def test_query_1_predict(self):
        print("\n--- TEST 1: PREDICT (Arsenal vs Chelsea) ---")
        res = run_football_agent("Predict Arsenal vs Chelsea")
        print(f"Total Time: {res.get('total_ms')} ms")
        print(f"Tool Calls: {res.get('tool_calls')}")
        print(f"Response Snippet:\n{res.get('response')[:250]}")
        self.assertNotIn("search_match_history", res.get("tool_calls", []))
        self.assertIn("predict_match", res.get("tool_calls", []))

    def test_query_2_historical(self):
        print("\n--- TEST 2: HISTORICAL MATCHES (Barcelona vs Real Madrid) ---")
        res = run_football_agent("Show me Barcelona vs Real Madrid")
        print(f"Total Time: {res.get('total_ms')} ms")
        print(f"Tool Calls: {res.get('tool_calls')}")
        print(f"Response Snippet:\n{res.get('response')[:250]}")

    def test_query_3_player_compare(self):
        print("\n--- TEST 3: PLAYER COMPARE (Messi vs Busquets) ---")
        res = run_football_agent("Compare Lionel Messi and Sergio Busquets stats")
        print(f"Total Time: {res.get('total_ms')} ms")
        print(f"Tool Calls: {res.get('tool_calls')}")
        print(f"Response Snippet:\n{res.get('response')[:250]}")
        self.assertIn("compare_players_tool", res.get("tool_calls", []))

    def test_query_4_rag(self):
        print("\n--- TEST 4: RAG SPECIFIC EVENT (Who scored in Barcelona vs Real Madrid in 2018?) ---")
        res = run_football_agent("Who scored in Barcelona vs Real Madrid in 2018?")
        print(f"Total Time: {res.get('total_ms')} ms")
        print(f"Tool Calls: {res.get('tool_calls')}")
        print(f"Response Snippet:\n{res.get('response')[:250]}")
        self.assertIn("search_match_history", res.get("tool_calls", []))

    def test_query_5_followup(self):
        print("\n--- TEST 5: FOLLOW-UP (What was Barcelona's xG?) ---")
        res = run_football_agent("What was Barcelona's xG?")
        print(f"Total Time: {res.get('total_ms')} ms")
        print(f"Tool Calls: {res.get('tool_calls')}")
        print(f"Response Snippet:\n{res.get('response')[:250]}")
        self.assertIn("get_team_stats", res.get("tool_calls", []))


if __name__ == "__main__":
    unittest.main()
