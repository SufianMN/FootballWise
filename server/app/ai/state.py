from typing import Annotated, Any, Dict, List, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    messages: Annotated[List[Any], add_messages]
    user_query: str
    tool_results: List[Dict[str, Any]]
    final_response: str
