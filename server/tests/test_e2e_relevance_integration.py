import sys
import time
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


class TestE2ERelevanceIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.stdout.reconfigure(encoding="utf-8")
        cls.client = TestClient(app)

    # 1. Verification of Unrelated Queries & Standalone Math through FastAPI API Endpoint
    @patch("app.ai.graph.build_football_graph")
    def test_e2e_unrelated_queries_rejected_with_zero_calls(self, mock_build_graph):
        unrelated_queries = [
            "Write a Python program.",
            "What's the weather today?",
            "Help me write my resume.",
            "Explain quantum mechanics.",
            "What is 10 + 20?",
            "Calculate 25% of 400.",
            "Solve x^2 + 5x + 6 = 0.",
            "What is the derivative of x^2?",
            "Integrate x^2.",
            "What is 12345 divided by 67?",
            "Solve this equation.",
            "What is 15% of 800?",
        ]

        for q in unrelated_queries:
            t0 = time.time()
            response = self.client.post("/api/ai/chat", json={"message": q})
            latency_ms = (time.time() - t0) * 1000

            # Verify API returns HTTP 200
            self.assertEqual(response.status_code, 200, f"API failed for query: '{q}'")
            data = response.json()

            print(f"\n[REJECTED E2E TEST] Query: '{q}'")
            print(f"  HTTP Status: {response.status_code}")
            print(f"  Response: {data.get('response')}")
            print(f"  Tool Calls: {data.get('tool_calls')}")
            print(f"  Latency: {latency_ms:.2f} ms")

            # 1. Exact rejection message
            self.assertEqual(data.get("response"), "⚽ Please ask something related to football.")

            # 2. Zero tool calls returned
            self.assertEqual(data.get("tool_calls"), [])

            # 3. Latency is virtually instantaneous (< 50 ms)
            self.assertLess(latency_ms, 50.0)

        # 4. Verify LangGraph / Groq / LLM was NEVER built or called for any of the rejected queries
        mock_build_graph.assert_not_called()

    # 2. Verification of Football Math Queries Accepted into Pipeline
    def test_e2e_football_math_queries_accepted(self):
        football_math_queries = [
            "What is Arsenal's average goals per game?",
            "Calculate the xG difference between Arsenal and Chelsea.",
            "What percentage of possession did Arsenal have?",
            "What is the team's win rate?",
        ]

        for q in football_math_queries:
            t0 = time.time()
            response = self.client.post("/api/ai/chat", json={"message": q})
            latency_ms = (time.time() - t0) * 1000

            self.assertEqual(response.status_code, 200, f"API failed for query: '{q}'")
            data = response.json()

            print(f"\n[ACCEPTED FOOTBALL MATH E2E TEST] Query: '{q}'")
            print(f"  HTTP Status: {response.status_code}")
            print(f"  Tool Calls: {data.get('tool_calls')}")
            print(f"  Response Snippet: {data.get('response', '')[:150]}...")
            print(f"  Latency: {latency_ms:.2f} ms")

            # Verify response is NOT the rejection message
            self.assertNotEqual(data.get("response"), "⚽ Please ask something related to football.")
            self.assertTrue(len(data.get("response", "")) > 10)

    # 3. Verification of General Football Queries (Not in Dataset) Entered Pipeline
    def test_e2e_general_football_queries_accepted(self):
        general_football_queries = [
            "What is the offside rule?",
            "Who won the 1966 World Cup?",
            "What is a false nine?",
            "What is gegenpressing?",
            "Who is the greatest football player ever?",
        ]

        for q in general_football_queries:
            t0 = time.time()
            response = self.client.post("/api/ai/chat", json={"message": q})
            latency_ms = (time.time() - t0) * 1000

            self.assertEqual(response.status_code, 200, f"API failed for query: '{q}'")
            data = response.json()

            print(f"\n[ACCEPTED GENERAL FOOTBALL E2E TEST] Query: '{q}'")
            print(f"  HTTP Status: {response.status_code}")
            print(f"  Tool Calls: {data.get('tool_calls')}")
            print(f"  Response Snippet: {data.get('response', '')[:150]}...")
            print(f"  Latency: {latency_ms:.2f} ms")

            # Verify response is NOT the rejection message
            self.assertNotEqual(data.get("response"), "⚽ Please ask something related to football.")
            self.assertTrue(len(data.get("response", "")) > 10)

    # 4. Verification of Football Queries with Dataset Available
    def test_e2e_dataset_available_queries_accepted(self):
        dataset_queries = [
            "Predict Arsenal vs Chelsea",
            "Compare Lionel Messi and Sergio Busquets stats",
        ]

        for q in dataset_queries:
            t0 = time.time()
            response = self.client.post("/api/ai/chat", json={"message": q})
            latency_ms = (time.time() - t0) * 1000

            self.assertEqual(response.status_code, 200, f"API failed for query: '{q}'")
            data = response.json()

            print(f"\n[ACCEPTED DATASET FOOTBALL E2E TEST] Query: '{q}'")
            print(f"  HTTP Status: {response.status_code}")
            print(f"  Tool Calls Executed: {data.get('tool_calls')}")
            print(f"  Response Snippet: {data.get('response', '')[:150]}...")
            print(f"  Latency: {latency_ms:.2f} ms")

            self.assertNotEqual(data.get("response"), "⚽ Please ask something related to football.")
            self.assertTrue(len(data.get("tool_calls", [])) > 0)


if __name__ == "__main__":
    unittest.main()

