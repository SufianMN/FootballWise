from app.ai.rag import search_match_history_context

def test_queries():
    queries = [
        "Barcelona vs Real Madrid",
        "Goal by Lionel Andrés Messi Cuccittini",
        "Red card or yellow card fouls",
    ]

    for q in queries:
        print(f"\n==================== QUERY: '{q}' ====================")
        result = search_match_history_context(q, k=2)
        print(result[:400] + "..." if len(result) > 400 else result)

if __name__ == "__main__":
    test_queries()
