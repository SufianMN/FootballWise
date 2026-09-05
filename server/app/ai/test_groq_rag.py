import os
from app.ai.llm import is_llm_configured, get_llm
from app.ai.rag import search_match_history_context

def test_groq_setup():
    print(f"Is LLM Configured: {is_llm_configured()}")
    print(f"LLM Provider: {os.environ.get('LLM_PROVIDER', 'groq')}")
    print(f"LLM Model: {os.environ.get('LLM_MODEL', 'llama-3.3-70b-versatile')}")

    # Test RAG retrieval tool
    query = "Barcelona vs Real Madrid"
    context = search_match_history_context(query)
    print("\n--- RAG Retrieval Test Result ---")
    print(context[:300] + "...\n")

if __name__ == "__main__":
    test_groq_setup()
