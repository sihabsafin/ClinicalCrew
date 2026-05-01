import os

# ── Available Models Registry ──────────────────────────────────────────────────
AVAILABLE_MODELS = {
    "LLaMA 3.3 70B (Groq)": {
        "provider":   "groq",
        "model":      "groq/llama-3.3-70b-versatile",
        "tpm_limit":  "6,000 TPM",
        "best_for":   "Speed & general tasks",
    },
    "Gemini 2.0 Flash (Google)": {
        "provider":   "gemini",
        "model":      "gemini/gemini-2.0-flash",
        "tpm_limit":  "1M TPM",
        "best_for":   "Long reports & best quality",
    },
    "Gemini 2.5 Flash (Google)": {
        "provider":   "gemini",
        "model":      "gemini/gemini-2.5-flash-preview-04-17",
        "tpm_limit":  "1M TPM",
        "best_for":   "Best results (recommended)",
    },
}

DEFAULT_MODEL = "Gemini 2.5 Flash (Google)"

# ── Secret Helper ──────────────────────────────────────────────────────────────
def _secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        return val if val else os.getenv(key, default)
    except Exception:
        return os.getenv(key, default)


# ── Dynamic LLM Factory ────────────────────────────────────────────────────────
def get_llm(temperature: float = 0.3):
    """
    Returns a CrewAI LLM instance based on the model selected in the sidebar.
    Falls back to Groq → Gemini 2.0 Flash if no session state is available.
    """
    from crewai import LLM

    groq_key   = _secret("GROQ_API_KEY")
    gemini_key = _secret("GEMINI_API_KEY")

    if groq_key:
        os.environ["GROQ_API_KEY"]   = groq_key
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key

    # ── Read selected model from Streamlit session state ───────────────────────
    selected_model_name = None
    try:
        import streamlit as st
        selected_model_name = st.session_state.get("selected_model", DEFAULT_MODEL)
    except Exception:
        pass

    cfg = AVAILABLE_MODELS.get(selected_model_name or DEFAULT_MODEL)

    if cfg:
        provider = cfg["provider"]
        model    = cfg["model"]

        if provider == "groq" and groq_key:
            return LLM(model=model, api_key=groq_key, temperature=temperature)

        if provider == "gemini" and gemini_key:
            return LLM(model=model, api_key=gemini_key, temperature=temperature)

    # ── Fallback: Groq first, then Gemini 2.0 Flash ───────────────────────────
    if groq_key:
        try:
            return LLM(
                model="groq/llama-3.3-70b-versatile",
                api_key=groq_key,
                temperature=temperature,
            )
        except Exception:
            pass

    if gemini_key:
        return LLM(
            model="gemini/gemini-2.0-flash",
            api_key=gemini_key,
            temperature=temperature,
        )

    raise ValueError(
        "No API key found. Add GROQ_API_KEY or GEMINI_API_KEY to Streamlit secrets."
    )
