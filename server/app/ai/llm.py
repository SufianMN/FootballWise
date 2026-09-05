import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from app.core.logger import get_logger

logger = get_logger(__name__)


def load_server_env() -> Path:
    """Ensure server/.env is loaded into environment variables with override=True."""
    current_file = Path(__file__).resolve()
    server_dir = current_file.parent.parent.parent  # server/
    env_file = server_dir / ".env"

    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)
        return env_file
    else:
        found = find_dotenv()
        if found:
            load_dotenv(dotenv_path=found, override=True)
            return Path(found)
        else:
            load_dotenv(override=True)
            return server_dir / ".env"


# Load env immediately on module import
loaded_env_path = load_server_env()


def get_sanitized_groq_key() -> str:
    """Retrieve and clean GROQ_API_KEY from environment variables."""
    load_server_env()
    raw_key = os.environ.get("GROQ_API_KEY") or os.environ.get("LLM_API_KEY") or ""
    clean_key = raw_key.strip().strip('"').strip("'").strip()
    if clean_key:
        os.environ["GROQ_API_KEY"] = clean_key
    return clean_key


def is_llm_configured() -> bool:
    """Check if an API key for the configured LLM provider is available."""
    provider = os.environ.get("LLM_PROVIDER", "groq").lower()
    if provider == "groq":
        api_key = get_sanitized_groq_key()
        return bool(api_key and api_key != "your_groq_api_key")
    if provider == "openai":
        api_key = (
            (os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY") or "")
            .strip()
            .strip('"')
            .strip("'")
        )
        return bool(api_key and api_key != "your_openai_api_key")
    return False


def get_llm(model_name: Optional[str] = None, temperature: float = 0.2):
    """
    Get a configured LangChain Chat Model instance for Groq (OpenAI-compatible) or OpenAI.
    Returns None if no API key is provided.
    Strictly uses the configured LLM_MODEL without silent model substitution.
    """
    if not is_llm_configured():
        logger.warning("GROQ_API_KEY is not configured or is invalid.")
        return None

    provider = os.environ.get("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        model = model_name or os.environ.get(
            "LLM_MODEL", "llama-3.3-70b-versatile"
        )
        api_key = get_sanitized_groq_key()
        base_url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

        max_output_tokens = int(os.environ.get("MAX_OUTPUT_TOKENS", 800))
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url,
                max_tokens=max_output_tokens,
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI for Groq with model '{model}': {e}")
            return None

    if provider == "openai":
        model = model_name or os.environ.get("LLM_MODEL", "gpt-4o-mini")
        api_key = (
            (os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY") or "")
            .strip()
            .strip('"')
            .strip("'")
        )
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI for OpenAI: {e}")
            return None

    logger.warning(f"Unsupported LLM provider: {provider}")
    return None



