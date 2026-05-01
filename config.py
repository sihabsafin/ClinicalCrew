import os

AVAILABLE_MODELS = {
    # ── Groq Models ───────────────────────────────────────────
    "🚀 Groq — LLaMA 3.3 70B (Fast)": {
        "model":     "groq/llama-3.3-70b-versatile",
        "provider":  "groq",
        "key_name":  "GROQ_API_KEY",
        "tpm_limit": "12,000 TPM free",
        "best_for":  "Speed + reasoning",
    },
    "🧠 Groq — LLaMA 3.1 8B (Light)": {
        "model":     "groq/llama-3.1-8b-instant",
        "provider":  "groq",
        "key_name":  "GROQ_API_KEY",
        "tpm_limit": "20,000 TPM free",
        "best_for":  "Fast lightweight tasks",
    },
    "🔥 Groq — Mixtral 8x7B": {
        "model":     "groq/mixtral-8x7b-32768",
        "provider":  "groq",
        "key_name":  "GROQ_API_KEY",
        "tpm_limit": "5,000 TPM free",
        "best_for":  "Long context tasks",
    },

    # ── Google Gemini ─────────────────────────────────────────
    "✨ Gemini 2.5 Flash (Recommended)": {
        "model":     "gemini/gemini-2.5-flash-preview-04-17",
        "provider":  "gemini",
        "key_name":  "GEMINI_API_KEY",
        "tpm_limit": "1,500 RPD free",
        "best_for":  "Best reasoning + accuracy",
    },
    "⚡ Gemini 2.0 Flash": {
        "model":     "gemini/gemini-2.0-flash",
        "provider":  "gemini",
        "key_name":  "GEMINI_API_KEY",
        "tpm_limit": "1,500 RPD free",
        "best_for":  "Fast + accurate",
    },
    "💎 Gemini 1.5 Pro": {
        "model":     "gemini/gemini-1.5-pro",
        "provider":  "gemini",
        "key_name":  "GEMINI_API_KEY",
        "tpm_limit": "50 RPD free",
        "best_for":  "Complex analysis",
    },

    # ── OpenRouter Free Models ────────────────────────────────
    # litellm (used by CrewAI) routes "openrouter/..." prefix automatically
    # when OPENROUTER_API_KEY env var is set — no custom base_url needed
    "🌐 OpenRouter — DeepSeek R1 (Free)": {
        "model":     "openrouter/deepseek/deepseek-r1:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "Free tier",
        "best_for":  "Deep reasoning",
    },
    "🌐 OpenRouter — DeepSeek V3 (Free)": {
        "model":     "openrouter/deepseek/deepseek-chat-v3-0324:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "Free tier",
        "best_for":  "General tasks",
    },
    "🌐 OpenRouter — Qwen 2.5 72B (Free)": {
        "model":     "openrouter/qwen/qwen-2.5-72b-instruct:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "Free tier",
        "best_for":  "Medical knowledge",
    },
    "🌐 OpenRouter — Llama 3.3 70B (Free)": {
        "model":     "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "Free tier",
        "best_for":  "Balanced performance",
    },
    "🌐 OpenRouter — Mistral 7B (Free)": {
        "model":     "openrouter/mistralai/mistral-7b-instruct:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "Free tier",
        "best_for":  "Lightweight fast",
    },
}

# Default model
DEFAULT_MODEL = "✨ Gemini 2.5 Flash (Recommended)"


def _secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        return val if val else os.getenv(key, default)
    except Exception:
        return os.getenv(key, default)


def get_available_models() -> dict:
    """Return only models whose API key is configured."""
    available = {}
    for name, cfg in AVAILABLE_MODELS.items():
        key = _secret(cfg["key_name"])
        if key:
            available[name] = cfg
    # If nothing configured, return all (for UI display)
    return available if available else AVAILABLE_MODELS


def get_llm(temperature: float = 0.3, model_name: str = None):
    """
    Get LLM instance for selected model.
    Falls back through: Gemini → Groq → OpenRouter
    """
    from crewai import LLM

    # Load all keys
    groq_key       = _secret("GROQ_API_KEY")
    gemini_key     = _secret("GEMINI_API_KEY")
    openrouter_key = _secret("OPENROUTER_API_KEY")

    # Set env vars for litellm auto-routing
    if groq_key:
        os.environ["GROQ_API_KEY"]       = groq_key
    if gemini_key:
        os.environ["GEMINI_API_KEY"]     = gemini_key
    if openrouter_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_key

    # Get selected model from session state if not passed
    if model_name is None:
        try:
            import streamlit as st
            model_name = st.session_state.get("selected_model", DEFAULT_MODEL)
        except Exception:
            model_name = DEFAULT_MODEL

    cfg      = AVAILABLE_MODELS.get(model_name, AVAILABLE_MODELS[DEFAULT_MODEL])
    provider = cfg["provider"]
    model    = cfg["model"]

    # ── Gemini ────────────────────────────────────────────────
    if provider == "gemini":
        if not gemini_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Add it to Streamlit secrets."
            )
        return LLM(
            model=model,
            api_key=gemini_key,
            temperature=temperature,
        )

    # ── Groq ──────────────────────────────────────────────────
    if provider == "groq":
        if not groq_key:
            raise ValueError(
                "GROQ_API_KEY not found. Add it to Streamlit secrets."
            )
        return LLM(
            model=model,
            api_key=groq_key,
            temperature=temperature,
        )

    # ── OpenRouter ────────────────────────────────────────────
    if provider == "openrouter":
        if not openrouter_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found. Add it to Streamlit secrets."
            )
        return LLM(
            model=model,
            api_key=openrouter_key,
            temperature=temperature,
        )

    # ── Auto Fallback ─────────────────────────────────────────
    if gemini_key:
        return LLM(
            model="gemini/gemini-2.5-flash-preview-04-17",
            api_key=gemini_key,
            temperature=temperature,
        )
    if groq_key:
        return LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=groq_key,
            temperature=temperature,
        )
    if openrouter_key:
        return LLM(
            model="openrouter/deepseek/deepseek-r1:free",
            api_key=openrouter_key,
            temperature=temperature,
        )

    raise ValueError(
        "No API key found. Add GEMINI_API_KEY, GROQ_API_KEY, "
        "or OPENROUTER_API_KEY to Streamlit secrets."
    )
