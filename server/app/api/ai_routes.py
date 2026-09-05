from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.ai.graph import run_football_agent
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Analyst"])


class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    response: str
    tool_calls: List[str] = []
    unconfigured: Optional[bool] = False


@router.post("/chat", response_model=AIChatResponse)
def ai_chat(request: AIChatRequest):
    """
    Process a natural language user query using FootballWise's LangGraph AI Analyst.
    Decides dynamically between prediction model, SHAP, team/player stats, and RAG event search.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message prompt cannot be empty.")

    try:
        res = run_football_agent(request.message.strip())
        return AIChatResponse(
            response=res.get("response", ""),
            tool_calls=res.get("tool_calls", []),
            unconfigured=res.get("unconfigured", False),
        )
    except Exception as e:
        logger.error(f"Exception in /api/ai/chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")
