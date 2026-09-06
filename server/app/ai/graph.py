import time
from typing import Any, Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.core.logger import get_logger
from .llm import get_llm, is_llm_configured
from .prompts import FOOTBALLWISE_SYSTEM_PROMPT
from .state import AgentState
from .token_guard import MAX_INPUT_TOKENS, guard_and_trim_messages
from .tools import (
    compare_players_tool,
    explain_match_prediction,
    get_player_stats,
    get_team_stats,
    predict_match,
    search_match_history,
)

logger = get_logger(__name__)

# List of available FootballWise tools
ALL_TOOLS = [
    predict_match,
    explain_match_prediction,
    get_team_stats,
    get_player_stats,
    compare_players_tool,
    search_match_history,
]


def build_football_graph(timing_records: List[Dict[str, Any]]):
    """Build and compile the LangGraph agent graph with precise timing diagnostics."""
    llm = get_llm()
    if llm is None:
        return None

    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    llm_call_counter = {"count": 0}

    def agent_node(state: AgentState):
        messages = state.get("messages", [])
        # Ensure system prompt is present
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=FOOTBALLWISE_SYSTEM_PROMPT)] + messages

        # Apply Token Guard to observe Groq Free Plan constraints (< 5500 tokens)
        guarded_messages = guard_and_trim_messages(messages, max_budget=MAX_INPUT_TOKENS)

        llm_call_counter["count"] += 1
        call_num = llm_call_counter["count"]

        t0 = time.time()
        response = llm_with_tools.invoke(guarded_messages)
        duration_ms = int((time.time() - t0) * 1000)

        timing_records.append({
            "step": f"LLM call {call_num}",
            "duration_ms": duration_ms,
        })

        return {"messages": [response]}

    tool_node = ToolNode(ALL_TOOLS)

    def timed_tool_node(state: AgentState):
        t0 = time.time()
        result = tool_node.invoke(state)
        duration_ms = int((time.time() - t0) * 1000)

        messages = state.get("messages", [])
        if messages and hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
            for tc in messages[-1].tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", str(tc))
                timing_records.append({
                    "step": f"tool:{name}",
                    "duration_ms": duration_ms,
                })

        return result

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", timed_tool_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")

    return builder.compile()


def run_football_agent(user_message: str) -> Dict[str, Any]:
    """
    Execute the FootballWise LangGraph agent workflow for a given user prompt.
    Returns structured response containing final_response, tool_calls, and timing logs.
    """
    if not is_llm_configured():
        return {
            "response": (
                "AI analyst is running in unconfigured mode because no GROQ_API_KEY is configured. "
                "Please set GROQ_API_KEY in server/.env."
            ),
            "tool_calls": [],
            "unconfigured": True,
        }

    t_start = time.time()
    timing_records: List[Dict[str, Any]] = []

    graph = build_football_graph(timing_records)
    if graph is None:
        return {
            "response": "Failed to initialize LLM for FootballWise AI Agent.",
            "tool_calls": [],
            "error": True,
        }

    try:
        initial_state = {
            "messages": [
                SystemMessage(content=FOOTBALLWISE_SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]
        }

        final_state = graph.invoke(initial_state)
        messages = final_state.get("messages", [])

        # Extract tool calls executed during graph trajectory
        tool_calls_executed = []
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", str(tc))
                    if name and name not in tool_calls_executed:
                        tool_calls_executed.append(name)

        final_content = ""
        if messages:
            final_content = str(messages[-1].content)

        total_ms = int((time.time() - t_start) * 1000)

        # Log AI Timing diagnostics cleanly without secrets
        log_lines = ["AI Timing:"]
        for rec in timing_records:
            log_lines.append(f"  {rec['step']}: {rec['duration_ms']} ms")
        log_lines.append(f"  Total: {total_ms} ms")
        logger.info("\n".join(log_lines))

        return {
            "response": final_content,
            "tool_calls": tool_calls_executed,
            "timing": timing_records,
            "total_ms": total_ms,
            "unconfigured": False,
        }
    except Exception as e:
        logger.error(f"Error executing FootballWise agent graph: {e}", exc_info=True)
        return {
            "response": f"An error occurred while processing your request: {str(e)}",
            "tool_calls": [],
            "error": True,
        }
