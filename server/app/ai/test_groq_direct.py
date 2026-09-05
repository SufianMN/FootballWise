import os
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.ai.llm import get_sanitized_groq_key, load_server_env, loaded_env_path


def run_groq_diagnostic():
    print("=" * 60)
    print("GROQ CONNECTIVITY & DIAGNOSTIC TEST")
    print("=" * 60)

    # Step 1: Check .env file path
    env_file = load_server_env()
    print(f"Loaded environment file: {env_file}")

    if not env_file.exists():
        print("\n[DIAGNOSTIC FAILURE: A]")
        print("Reason: server/.env file is missing or not found.")
        return False

    # Step 2: Retrieve raw and sanitized key
    raw_key = os.environ.get("GROQ_API_KEY") or os.environ.get("LLM_API_KEY") or ""
    clean_key = get_sanitized_groq_key()

    if not raw_key:
        print("\n[DIAGNOSTIC FAILURE: A]")
        print("Reason: GROQ_API_KEY is not set in server/.env or environment.")
        return False

    if raw_key == "your_groq_api_key":
        print("\n[DIAGNOSTIC FAILURE: A]")
        print("Reason: GROQ_API_KEY is still set to placeholder 'your_groq_api_key'.")
        return False

    # Check for quotes/spaces in raw_key vs clean_key
    if len(raw_key) != len(clean_key) or raw_key != clean_key:
        print("\n[DIAGNOSTIC WARNING: B]")
        print("Detected accidental surrounding quotes or whitespace in loaded key.")
        print(f"Raw length: {len(raw_key)}, Cleaned length: {len(clean_key)}")
        print("Key has been sanitized automatically.")

    prefix = f"{clean_key[:4]}****" if len(clean_key) >= 4 else "****"
    print(f"Sanitized GROQ_API_KEY Prefix: {prefix}")
    print(f"Sanitized GROQ_API_KEY Length: {len(clean_key)}")

    # Step 3: Check configuration parameters
    provider = os.environ.get("LLM_PROVIDER", "groq").lower()
    model = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
    base_url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    print(f"LLM Provider: {provider}")
    print(f"LLM Model: {model}")
    print(f"Base URL: {base_url}")

    if provider != "groq":
        print("\n[DIAGNOSTIC FAILURE: C]")
        print(f"Reason: LLM_PROVIDER is set to '{provider}', expected 'groq'.")
        return False

    if "groq.com" not in base_url:
        print("\n[DIAGNOSTIC FAILURE: C]")
        print(f"Reason: Groq request configuration base URL is incorrect: {base_url}")
        return False

    # Step 4: Attempt minimal live Groq LLM call using get_llm()
    print("\nSending minimal request to Groq API (Prompt: 'Respond with OK')...")
    try:
        from app.ai.llm import get_llm
        llm = get_llm(temperature=0.0)
        if llm is None:
            print("\n[DIAGNOSTIC FAILURE: C]")
            print("Reason: get_llm() returned None. Check LLM configuration.")
            return False

        print(f"Active Resolved Model: {getattr(llm, 'model_name', model)}")
        response = llm.invoke([HumanMessage(content="Respond with OK.")])
        content = response.content.strip()
        print(f"Groq API Response: '{content}'")
        print("\n[DIAGNOSTIC SUCCESS]")
        print("Groq API key and ChatOpenAI configuration are working perfectly!")
        return True

    except Exception as e:
        err_str = str(e)
        # Mask any potential key leak in exception string
        if clean_key and clean_key in err_str:
            err_str = err_str.replace(clean_key, "*****")

        if "401" in err_str or "invalid_api_key" in err_str.lower() or "AuthenticationError" in type(e).__name__:
            print("\n[DIAGNOSTIC FAILURE: D]")
            print("Reason: Groq API rejected the key (401 Unauthorized / Invalid API Key).")
            print(f"Details: {err_str}")
        else:
            print("\n[DIAGNOSTIC FAILURE: C/D]")
            print(f"Reason: Groq API call failed: {type(e).__name__} - {err_str}")
        return False



if __name__ == "__main__":
    success = run_groq_diagnostic()
    sys.exit(0 if success else 1)
