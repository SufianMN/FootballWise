import os
from app.ai.llm import get_sanitized_groq_key, is_llm_configured, load_server_env

load_server_env()


def safe_check():
    key = get_sanitized_groq_key()
    is_configured = is_llm_configured()

    if key and len(key) >= 4:
        prefix = f"{key[:4]}****"
    elif key:
        prefix = "****"
    else:
        prefix = "None"

    key_len = len(key) if key else 0
    provider = os.environ.get("LLM_PROVIDER", "groq")
    model = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
    base_url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    print(f"GROQ_API_KEY configured: {is_configured}")
    print(f"GROQ_API_KEY prefix: {prefix}")
    print(f"GROQ_API_KEY length: {key_len}")
    print(f"LLM Provider: {provider}")
    print(f"LLM Model: {model}")
    print(f"Groq Base URL: {base_url}")


if __name__ == "__main__":
    safe_check()

