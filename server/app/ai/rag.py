import os
from pathlib import Path
from typing import Optional
from app.core.logger import get_logger

logger = get_logger(__name__)


def get_chroma_db_dir() -> Path:
    """Get the path to persistent ChromaDB storage."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    return base_dir / "data" / "chroma_db"


def is_rag_index_available() -> bool:
    """Check if ChromaDB index directory exists and has persistent data."""
    chroma_dir = get_chroma_db_dir()
    return chroma_dir.exists() and any(chroma_dir.iterdir())


def search_match_history_context(query: str, team_filter: Optional[str] = None, k: int = 3) -> str:
    """
    Search ChromaDB for historical match events and timeline narratives matching the user query.
    Enforces Groq Free Plan constraints (top_k=3, max 2000 context tokens).
    """
    if not is_rag_index_available():
        return (
            "RAG match event database is not built yet. "
            "Please run 'python -m app.ai.build_rag_index' to generate the vector index."
        )

    chroma_dir = str(get_chroma_db_dir())
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_openai import OpenAIEmbeddings

        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
        if api_key:
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
        else:
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            except Exception:
                from langchain_community.embeddings import FakeEmbeddings
                embeddings = FakeEmbeddings(size=384)

        db = Chroma(
            persist_directory=chroma_dir,
            embedding_function=embeddings,
            collection_name="footballwise_events",
        )

        filter_dict = None
        if team_filter:
            filter_dict = {"$or": [{"home_team": team_filter}, {"away_team": team_filter}]}

        # Strictly retrieve top_k = 3
        docs = db.similarity_search(query, k=k, filter=filter_dict)
        if not docs:
            docs = db.similarity_search(query, k=k)

        if not docs:
            return "No relevant historical match event records found in the database."

        formatted_chunks = []
        for i, d in enumerate(docs, 1):
            meta = d.metadata
            match_title = f"{meta.get('home_team', '')} vs {meta.get('away_team', '')} ({meta.get('season', '')})"
            # Truncate content snippet to 600 chars max per document to observe free tier limits
            content_snippet = d.page_content[:600]
            if len(d.page_content) > 600:
                content_snippet += "..."
            formatted_chunks.append(f"--- MATCH EVENT SUMMARY #{i} ({match_title}) ---\n{content_snippet}")

        rag_result = "\n\n".join(formatted_chunks)

        # Enforce maximum RAG context limit (~2000 tokens ~ 7500 chars)
        if len(rag_result) > 7500:
            rag_result = rag_result[:7500] + "\n...[RAG Context capped at 2000 tokens]"

        return rag_result
    except Exception as e:
        logger.error(f"Error during RAG similarity search: {e}", exc_info=True)
        return f"Error retrieving match event history: {str(e)}"
