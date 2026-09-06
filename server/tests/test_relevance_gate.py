import unittest
from unittest.mock import patch
from app.ai.relevance_gate import is_football_query
from app.ai.graph import run_football_agent


class TestRelevanceGate(unittest.TestCase):
    # 1. General Football Questions (Not in Dataset) -> ACCEPT
    def test_general_football_questions_accept(self):
        general_football_queries = [
            "What is the offside rule?",
            "Explain what a false nine is.",
            "Who won the 1966 World Cup?",
            "What is gegenpressing?",
            "Who is the greatest football player ever?",
            "How does VAR work?",
            "What is the Ballon d'Or?",
            "Who has won the most Champions League titles?",
            "Explain the difference between 4-3-3 and 4-2-3-1.",
            "What is a low block?",
            "How does the transfer window work?",
            "Why do teams use zonal marking?",
        ]
        for q in general_football_queries:
            with self.subTest(query=q):
                self.assertTrue(is_football_query(q), f"Failed to ACCEPT general football query: '{q}'")

    # 2. Football Questions Involving Unknown Teams / Players / Years -> ACCEPT
    def test_unknown_teams_players_years_accept(self):
        unknown_queries = [
            "Who won the 1930 World Cup?",
            "Tell me about Santos FC history.",
            "Who is the manager of Al Hilal?",
            "How many goals did Ferenc Puskás score?",
            "Who won the African Cup of Nations in 2022?",
        ]
        for q in unknown_queries:
            with self.subTest(query=q):
                self.assertTrue(is_football_query(q), f"Failed to ACCEPT query with unknown entity: '{q}'")

    # 3. Conversational Follow-ups & Short Ambiguous Questions -> ACCEPT
    def test_conversational_followups_and_ambiguous_accept(self):
        followups = [
            "Tell me about Arsenal.",
            "Why?",
            "What about Chelsea?",
            "Who is their best midfielder?",
            "Who is the GOAT?",
            "How many goals?",
            "Who won?",
        ]
        for q in followups:
            with self.subTest(query=q):
                self.assertTrue(is_football_query(q), f"Failed to ACCEPT follow-up/ambiguous query: '{q}'")

    # 4. Standalone Pure Mathematics Questions -> REJECT
    def test_standalone_math_queries_reject(self):
        standalone_math_queries = [
            "What is 10 + 20?",
            "Calculate 25% of 400.",
            "Solve x^2 + 5x + 6 = 0.",
            "What is the derivative of x^2?",
            "Integrate x^2.",
            "What is 12345 divided by 67?",
            "Solve this equation.",
            "What is 15% of 800?",
            "What is 100 divided by 4?",
            "Solve 2x + 5 = 15.",
            "What is the square root of 144?",
            "Calculate the average of 10, 20, and 30.",
        ]
        for q in standalone_math_queries:
            with self.subTest(query=q):
                self.assertFalse(is_football_query(q), f"Failed to REJECT standalone math query: '{q}'")

    # 5. Football Mathematics & Contextual Queries -> ACCEPT
    def test_football_math_queries_accept(self):
        football_math_queries = [
            "What is Arsenal's average goals per game?",
            "Calculate the xG difference between Arsenal and Chelsea.",
            "What percentage of possession did Arsenal have?",
            "What is the team's win rate?",
            "Calculate the goal difference.",
            "How is xG calculated?",
            "What is the average number of shots per match?",
            "What is the average goals per match?",
            "What is a team's win rate?",
            "What does 30% possession mean?",
            "If a team scores 2 goals from 10 shots, what is its scoring rate?",
            "What is Chelsea's win percentage?",
        ]
        for q in football_math_queries:
            with self.subTest(query=q):
                self.assertTrue(is_football_query(q), f"Failed to ACCEPT football math query: '{q}'")

    # 6. Clearly Unrelated Questions -> REJECT
    def test_unrelated_questions_reject(self):
        unrelated_queries = [
            "Write a Python program.",
            "What's the weather?",
            "Explain quantum mechanics.",
            "Help me write my resume.",
            "What's the capital of India?",
            "Tell me a joke.",
            "How to bake a chocolate cake?",
            "What is the stock price of Apple?",
        ]
        for q in unrelated_queries:
            with self.subTest(query=q):
                self.assertFalse(is_football_query(q), f"Failed to REJECT unrelated query: '{q}'")

    # 7. Verify Zero Groq / LLM / RAG / Tool Calls on Math Rejection
    @patch("app.ai.graph.build_football_graph")
    def test_math_rejection_consumes_zero_llm_or_tool_calls(self, mock_build_graph):
        res = run_football_agent("Calculate 25% of 400.")

        self.assertEqual(res.get("response"), "⚽ Please ask something related to football.")
        self.assertEqual(res.get("tool_calls"), [])
        self.assertTrue(res.get("rejected"))
        self.assertEqual(res.get("total_ms"), 0)

        # Confirm that the LangGraph graph was NEVER built or invoked
        mock_build_graph.assert_not_called()


if __name__ == "__main__":
    unittest.main()

