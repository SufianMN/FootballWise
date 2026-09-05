import unittest
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage

from app.ai.token_guard import (
    MAX_INPUT_TOKENS,
    MAX_RAG_TOKENS,
    MAX_TOOL_OUTPUT_TOKENS,
    analyze_message_tokens,
    estimate_tokens,
    guard_and_trim_messages,
)
from app.ai.tools import (
    explain_match_prediction,
    get_player_stats,
    get_team_stats,
    predict_match,
    search_match_history,
)


class TestTokenGuard(unittest.TestCase):
    def test_estimate_tokens(self):
        text = "Hello world, FootballWise AI Analyst test."
        toks = estimate_tokens(text)
        self.assertGreater(toks, 0)
        self.assertLess(toks, 20)

    def test_oversized_rag_context_trimming(self):
        huge_rag = "MATCH EVENT RECORD #1 Barcelona vs Real Madrid\n" + ("Shot by Messi in 45th minute. " * 300)
        tool_msg = ToolMessage(content=huge_rag, tool_call_id="call_rag_1")
        messages = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="What happened in El Clasico?"),
            tool_msg,
        ]
        trimmed = guard_and_trim_messages(messages, max_budget=2000)
        breakdown = analyze_message_tokens(trimmed)
        self.assertLessEqual(breakdown["total_tokens"], 2000)

    def test_oversized_tool_output_trimming(self):
        huge_tool = "Tool output: " + ("data " * 1000)
        tool_msg = ToolMessage(content=huge_tool, tool_call_id="call_tool_1")
        messages = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="Analyze team stats"),
            tool_msg,
        ]
        trimmed = guard_and_trim_messages(messages, max_budget=1500)
        breakdown = analyze_message_tokens(trimmed)
        self.assertLessEqual(breakdown["total_tokens"], 1500)

    def test_long_conversation_history_trimming(self):
        messages = [SystemMessage(content="System prompt")]
        for i in range(20):
            messages.append(HumanMessage(content=f"Question {i} " + ("word " * 50)))
            messages.append(AIMessage(content=f"Answer {i} " + ("word " * 50)))
        messages.append(HumanMessage(content="Latest user prompt?"))

        trimmed = guard_and_trim_messages(messages, max_budget=1500)
        breakdown = analyze_message_tokens(trimmed)
        self.assertLessEqual(breakdown["total_tokens"], 1500)
        # Ensure latest user prompt is never removed
        self.assertEqual(trimmed[-1].content, "Latest user prompt?")

    def test_normal_prediction_request_token_budget(self):
        res = predict_match.invoke({"home_team": "Arsenal", "away_team": "Chelsea"})
        tool_msg = ToolMessage(content=str(res), tool_call_id="call_pred")
        messages = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="Predict Arsenal vs Chelsea"),
            tool_msg,
        ]
        breakdown = analyze_message_tokens(messages)
        self.assertLessEqual(breakdown["total_tokens"], MAX_INPUT_TOKENS)

    def test_prediction_and_shap_request_token_budget(self):
        res_pred = predict_match.invoke({"home_team": "Arsenal", "away_team": "Chelsea"})
        res_shap = explain_match_prediction.invoke({"home_team": "Arsenal", "away_team": "Chelsea"})
        messages = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="Predict Arsenal vs Chelsea and explain why"),
            ToolMessage(content=str(res_pred), tool_call_id="call_1"),
            ToolMessage(content=str(res_shap), tool_call_id="call_2"),
        ]
        breakdown = analyze_message_tokens(messages)
        self.assertLessEqual(breakdown["total_tokens"], MAX_INPUT_TOKENS)

    def test_rag_request_token_budget(self):
        rag_res = search_match_history.invoke({"query": "Arsenal goals"})
        messages = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="Search Arsenal goals"),
            ToolMessage(content=str(rag_res), tool_call_id="call_rag"),
        ]
        breakdown = analyze_message_tokens(messages)
        self.assertLessEqual(breakdown["total_tokens"], MAX_INPUT_TOKENS)


if __name__ == "__main__":
    unittest.main()
