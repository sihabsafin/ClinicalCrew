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
    "✨ Gemini 2.5 Flash": {
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

# Phase keys for per-phase model selection
PHASE_MODEL_KEYS = {
    "phase1": "model_phase1",
    "phase2": "model_phase2",
    "phase3": "model_phase3",
    "phase4": "model_phase4",
}


def _secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        return val if val else os.getenv(key, default)
    except Exception:
        return os.getenv(key, default)


def get_model_names() -> list:
    """Return all model display names."""
    return list(AVAILABLE_MODELS.keys())


def get_phase_model(phase_key: str) -> str | None:
    """
    Get selected model name for a given phase.
    Returns None if user hasn't selected yet.
    phase_key: 'phase1' | 'phase2' | 'phase3' | 'phase4'
    """
    try:
        import streamlit as st
        session_key = PHASE_MODEL_KEYS.get(phase_key, "model_phase1")
        return st.session_state.get(session_key, None)
    except Exception:
        return None


def get_llm(temperature: float = 0.3, phase_key: str = "phase1"):
    """
    Get LLM instance for a specific phase.
    phase_key: 'phase1' | 'phase2' | 'phase3' | 'phase4'
    Raises clear error if no model selected or no API key.
    """
    from crewai import LLM

    # Load all keys
    groq_key       = _secret("GROQ_API_KEY")
    gemini_key     = _secret("GEMINI_API_KEY")
    openrouter_key = _secret("OPENROUTER_API_KEY")

    # Set env vars for litellm routing
    if groq_key:
        os.environ["GROQ_API_KEY"]       = groq_key
    if gemini_key:
        os.environ["GEMINI_API_KEY"]     = gemini_key
    if openrouter_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_key

    # Get model selected for this phase
    model_name = get_phase_model(phase_key)

    if not model_name:
        raise ValueError(
            f"❌ No model selected for this phase. "
            f"Please select a model from the panel above before running."
        )

    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model: {model_name}")

    cfg      = AVAILABLE_MODELS[model_name]
    provider = cfg["provider"]
    model    = cfg["model"]

    # ── Gemini ────────────────────────────────────────────────
    if provider == "gemini":
        if not gemini_key:
            raise ValueError(
                "❌ GEMINI_API_KEY not found. "
                "Add it to Streamlit secrets or .streamlit/secrets.toml"
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
                "❌ GROQ_API_KEY not found. "
                "Add it to Streamlit secrets or .streamlit/secrets.toml"
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
                "❌ OPENROUTER_API_KEY not found. "
                "Add it to Streamlit secrets or .streamlit/secrets.toml"
            )
        return LLM(
            model=model,
            api_key=openrouter_key,
            temperature=temperature,
        )

    raise ValueError(f"Unknown provider: {provider}")
