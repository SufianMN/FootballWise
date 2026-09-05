import os
from typing import Any, Dict, List, Tuple
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from app.core.logger import get_logger

logger = get_logger(__name__)

# Free-tier token budget constants (Target: < 5500 input tokens to stay comfortably below 8000 TPM)
MAX_INPUT_TOKENS = int(os.environ.get("MAX_INPUT_TOKENS", 5500))
MAX_RAG_TOKENS = int(os.environ.get("MAX_RAG_TOKENS", 2000))
MAX_TOOL_OUTPUT_TOKENS = int(os.environ.get("MAX_TOOL_OUTPUT_TOKENS", 1500))
MAX_HISTORY_TOKENS = int(os.environ.get("MAX_HISTORY_TOKENS", 1000))
MAX_SYSTEM_TOKENS = int(os.environ.get("MAX_SYSTEM_TOKENS", 600))


def estimate_tokens(text: str) -> int:
    """Estimate token count for a text string using tiktoken or fallback heuristic."""
    if not text:
        return 0
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return int(len(text) / 3.8) + 1


def get_message_content(msg: BaseMessage) -> str:
    """Safely extract string content from any LangChain message."""
    if hasattr(msg, "content"):
        content = msg.content
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join([str(item) for item in content])
        return str(content)
    return str(msg)


def analyze_message_tokens(messages: List[BaseMessage]) -> Dict[str, int]:
    """Calculate token breakdown by category across all messages."""
    system_tokens = 0
    history_tokens = 0
    tool_tokens = 0
    rag_tokens = 0
    user_prompt_tokens = 0

    num_messages = len(messages)
    for i, msg in enumerate(messages):
        text = get_message_content(msg)
        toks = estimate_tokens(text)

        if isinstance(msg, SystemMessage):
            system_tokens += toks
        elif isinstance(msg, ToolMessage):
            tool_tokens += toks
            if "MATCH EVENT RECORD" in text or "RAG" in text or "match_history" in text:
                rag_tokens += toks
        elif i == num_messages - 1 and isinstance(msg, HumanMessage):
            user_prompt_tokens += toks
        else:
            history_tokens += toks

    total_tokens = system_tokens + history_tokens + tool_tokens + user_prompt_tokens

    return {
        "system_tokens": system_tokens,
        "history_tokens": history_tokens,
        "tool_tokens": tool_tokens,
        "rag_tokens": rag_tokens,
        "user_prompt_tokens": user_prompt_tokens,
        "total_tokens": total_tokens,
    }


def log_token_diagnostics(breakdown: Dict[str, int]) -> None:
    """Log structured token usage breakdown before LLM request (never logging secrets)."""
    logger.info(
        f"Token Breakdown -> Estimated input tokens: {breakdown['total_tokens']} | "
        f"RAG tokens: {breakdown['rag_tokens']} | Tool tokens: {breakdown['tool_tokens']} | "
        f"History tokens: {breakdown['history_tokens']} | System tokens: {breakdown['system_tokens']} | "
        f"User tokens: {breakdown['user_prompt_tokens']} | "
        f"Estimated total: {breakdown['total_tokens']}"
    )


def trim_text_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text so its token count does not exceed max_tokens."""
    if estimate_tokens(text) <= max_tokens:
        return text

    # Approximate character cutoff
    target_chars = int(max_tokens * 3.5)
    truncated = text[:target_chars] + "\n...[Truncated to observe Groq Free Tier token limits]"
    return truncated


def guard_and_trim_messages(
    messages: List[BaseMessage], max_budget: int = MAX_INPUT_TOKENS
) -> List[BaseMessage]:
    """
    Final Token Guard: Inspect prompt messages and trim context if estimated total > max_budget.
    Trimming Order:
      1. Old conversation history
      2. Low-relevance / verbose RAG results
      3. Verbose tool output
    Never removes current user question or system instructions.
    """
    breakdown = analyze_message_tokens(messages)
    log_token_diagnostics(breakdown)

    if breakdown["total_tokens"] <= max_budget:
        return messages

    logger.warning(
        f"Estimated total tokens ({breakdown['total_tokens']}) exceeds free-tier budget ({max_budget}). Applying context reduction..."
    )

    trimmed_messages = list(messages)

    # 1. Trim conversation history if present (keep system prompt + last 2 messages)
    if breakdown["history_tokens"] > MAX_HISTORY_TOKENS and len(trimmed_messages) > 3:
        logger.info("Trimming old conversation history...")
        system_msg = trimmed_messages[0] if isinstance(trimmed_messages[0], SystemMessage) else None
        recent_msgs = trimmed_messages[-3:]
        if system_msg and system_msg not in recent_msgs:
            trimmed_messages = [system_msg] + recent_msgs
        else:
            trimmed_messages = recent_msgs

    # Re-evaluate
    breakdown = analyze_message_tokens(trimmed_messages)
    if breakdown["total_tokens"] <= max_budget:
        log_token_diagnostics(breakdown)
        return trimmed_messages

    # 2. Trim ToolMessage contents (RAG and verbose tool outputs)
    for i, msg in enumerate(trimmed_messages):
        if isinstance(msg, ToolMessage):
            content = get_message_content(msg)
            if estimate_tokens(content) > MAX_TOOL_OUTPUT_TOKENS:
                logger.info(f"Trimming ToolMessage #{i} output to max {MAX_TOOL_OUTPUT_TOKENS} tokens...")
                new_content = trim_text_to_tokens(content, MAX_TOOL_OUTPUT_TOKENS)
                trimmed_messages[i] = ToolMessage(
                    content=new_content, tool_call_id=getattr(msg, "tool_call_id", "")
                )

    # Final re-evaluate
    final_breakdown = analyze_message_tokens(trimmed_messages)
    log_token_diagnostics(final_breakdown)
    return trimmed_messages
