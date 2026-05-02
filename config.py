import os

AVAILABLE_MODELS = {
    # ══════════════════════════════════════════════════════════
    # GROQ — Current Production Models (May 2026)
    # console.groq.com/docs/models
    # ══════════════════════════════════════════════════════════
    "🚀 Groq — LLaMA 3.3 70B": {
        "model":     "groq/llama-3.3-70b-versatile",
        "provider":  "groq",
        "key_name":  "GROQ_API_KEY",
        "tpm_limit": "12,000 TPM",
        "best_for":  "Best Groq model — fast + smart",
        "status":    "✅ Production",
    },
    "⚡ Groq — LLaMA 3.1 8B (Fastest)": {
        "model":     "groq/llama-3.1-8b-instant",
        "provider":  "groq",
        "key_name":  "GROQ_API_KEY",
        "tpm_limit": "20,000 TPM",
        "best_for":  "Fastest — good for simple tasks",
        "status":    "✅ Production",
    },
    "🧠 Groq — LLaMA 4 Scout 17B": {
        "model":     "groq/meta-llama/llama-4-scout-17b-16e-instruct",
        "provider":  "groq",
        "key_name":  "GROQ_API_KEY",
        "tpm_limit": "8,000 TPM",
        "best_for":  "Multimodal + latest LLaMA 4",
        "status":    "✅ Production",
    },
    "🔬 Groq — Qwen3 32B": {
        "model":     "groq/qwen/qwen3-32b",
        "provider":  "groq",
        "key_name":  "GROQ_API_KEY",
        "tpm_limit": "6,000 TPM",
        "best_for":  "Strong reasoning + medical",
        "status":    "✅ Production",
    },
    "🌙 Groq — GPT-OSS 120B": {
        "model":     "groq/openai/gpt-oss-120b",
        "provider":  "groq",
        "key_name":  "GROQ_API_KEY",
        "tpm_limit": "6,000 TPM",
        "best_for":  "Top reasoning performance",
        "status":    "✅ Production",
    },

    # ══════════════════════════════════════════════════════════
    # GOOGLE GEMINI — Free Tier
    # aistudio.google.com
    # ══════════════════════════════════════════════════════════
    "✨ Gemini 2.5 Flash (Best Free)": {
        "model":     "gemini/gemini-2.5-flash-preview-04-17",
        "provider":  "gemini",
        "key_name":  "GEMINI_API_KEY",
        "tpm_limit": "500 RPD free",
        "best_for":  "Best reasoning + accuracy",
        "status":    "✅ Recommended",
    },
    "💎 Gemini 2.5 Pro": {
        "model":     "gemini/gemini-2.5-pro-preview-05-06",
        "provider":  "gemini",
        "key_name":  "GEMINI_API_KEY",
        "tpm_limit": "50 RPD free",
        "best_for":  "Most powerful Gemini",
        "status":    "✅ Production",
    },
    "⚡ Gemini 2.0 Flash": {
        "model":     "gemini/gemini-2.0-flash",
        "provider":  "gemini",
        "key_name":  "GEMINI_API_KEY",
        "tpm_limit": "1,500 RPD free",
        "best_for":  "Fast + reliable",
        "status":    "✅ Production",
    },
    "🔵 Gemini 1.5 Flash": {
        "model":     "gemini/gemini-1.5-flash",
        "provider":  "gemini",
        "key_name":  "GEMINI_API_KEY",
        "tpm_limit": "1,500 RPD free",
        "best_for":  "Stable + well-tested",
        "status":    "✅ Production",
    },

    # ══════════════════════════════════════════════════════════
    # OPENROUTER — Currently Working Free Models (May 2026)
    # Verified from openrouter.ai/collections/free-models
    # ══════════════════════════════════════════════════════════
    "🌐 OR — Llama 3.3 70B (Free ✓)": {
        "model":     "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "Reliable + well-tested",
        "status":    "✅ Working",
    },
    "🌐 OR — Gemma 3 27B (Free ✓)": {
        "model":     "openrouter/google/gemma-3-27b-it:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "Google model — vision + text",
        "status":    "✅ Working",
    },
    "🌐 OR — Gemma 4 31B (Free ✓)": {
        "model":     "openrouter/google/gemma-4-31b-it:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "Latest Google Gemma",
        "status":    "✅ Working",
    },
    "🌐 OR — GPT-OSS 120B (Free ✓)": {
        "model":     "openrouter/openai/gpt-oss-120b:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "Top reasoning — OpenAI OSS",
        "status":    "✅ Working",
    },
    "🌐 OR — GPT-OSS 20B (Free ✓)": {
        "model":     "openrouter/openai/gpt-oss-20b:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "Lighter + fast OpenAI OSS",
        "status":    "✅ Working",
    },
    "🌐 OR — Qwen3 Coder (Free ✓)": {
        "model":     "openrouter/qwen/qwen3-coder:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "Structured output + logic",
        "status":    "✅ Working",
    },
    "🌐 OR — NVIDIA Nemotron 120B (Free ✓)": {
        "model":     "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "NVIDIA flagship — 262K ctx",
        "status":    "✅ Working",
    },
    "🌐 OR — MiniMax M2.5 (Free ✓)": {
        "model":     "openrouter/minimax/minimax-m2.5:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "Long context 197K — reports",
        "status":    "✅ Working",
    },
    "🌐 OR — Hermes 3 Llama 405B (Free ✓)": {
        "model":     "openrouter/nousresearch/hermes-3-llama-3.1-405b:free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200 req/day free",
        "best_for":  "Massive 405B — deep reasoning",
        "status":    "✅ Working",
    },
    "🌐 OR — OpenRouter Auto (Free ✓)": {
        "model":     "openrouter/openrouter/free",
        "provider":  "openrouter",
        "key_name":  "OPENROUTER_API_KEY",
        "tpm_limit": "200K ctx — auto best model",
        "best_for":  "Auto picks best available",
        "status":    "✅ Always works",
    },
}

# Phase keys
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
    return list(AVAILABLE_MODELS.keys())


def get_phase_model(phase_key: str) -> str | None:
    try:
        import streamlit as st
        session_key = PHASE_MODEL_KEYS.get(phase_key, "model_phase1")
        return st.session_state.get(session_key, None)
    except Exception:
        return None


def get_llm(temperature: float = 0.3, phase_key: str = "phase1"):
    from crewai import LLM

    groq_key       = _secret("GROQ_API_KEY")
    gemini_key     = _secret("GEMINI_API_KEY")
    openrouter_key = _secret("OPENROUTER_API_KEY")

    if groq_key:
        os.environ["GROQ_API_KEY"]       = groq_key
    if gemini_key:
        os.environ["GEMINI_API_KEY"]     = gemini_key
    if openrouter_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_key

    model_name = get_phase_model(phase_key)

    if not model_name:
        raise ValueError(
            "❌ No model selected. Please select a model above before running."
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
                "❌ GEMINI_API_KEY missing. "
                "Get free key: https://aistudio.google.com/apikey"
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
                "❌ GROQ_API_KEY missing. "
                "Get free key: https://console.groq.com"
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
                "❌ OPENROUTER_API_KEY missing. "
                "Get free key: https://openrouter.ai/keys"
            )
        # litellm routes openrouter/ prefix automatically
        # OPENROUTER_API_KEY env var must be set
        return LLM(
            model=model,
            api_key=openrouter_key,
            temperature=temperature,
        )

    raise ValueError(f"Unknown provider: {provider}")
