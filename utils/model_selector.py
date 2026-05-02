import streamlit as st
import streamlit.components.v1 as components
from config import AVAILABLE_MODELS, PHASE_MODEL_KEYS


PROVIDER_COLORS = {
    "groq":       "#f97316",
    "gemini":     "#3b82f6",
    "openrouter": "#a855f7",
}

PHASE_INFO = {
    "phase1": {
        "label": "Phase 1 — Report Intake",
        "icon":  "📥",
        "desc":  "Parses report, builds patient profile, validates data",
        "agents": "ReportParser + ContextBuilder + Validator",
    },
    "phase2": {
        "label": "Phase 2 — Diagnosis Analysis",
        "icon":  "🔬",
        "desc":  "Symptom analysis, lab interpretation, risk scoring",
        "agents": "SymptomAnalyzer + LabInterpreter + RiskAssessor",
    },
    "phase3": {
        "label": "Phase 3 — Treatment Planning",
        "icon":  "💊",
        "desc":  "Evidence-based treatments, drug safety, dosing",
        "agents": "TreatmentSuggester + DrugChecker + DosageCalc",
    },
    "phase4": {
        "label": "Phase 4 — Clinical Summary",
        "icon":  "📄",
        "desc":  "SOAP report, patient summary, follow-up plan",
        "agents": "ReportWriter + PatientExplainer + FollowUpPlanner",
    },
}


def render_phase_model_selector(phase_key: str) -> str | None:
    """
    Render a model selector for a specific phase.
    Returns selected model name or None.
    """
    session_key = PHASE_MODEL_KEYS[phase_key]
    phase_info  = PHASE_INFO[phase_key]

    model_names  = list(AVAILABLE_MODELS.keys())
    # Add empty option as first — no default
    options      = ["— Select a model —"] + model_names

    current = st.session_state.get(session_key, None)
    current_idx = (
        options.index(current)
        if current and current in options
        else 0
    )

    # ── Selector Card ────────────────────────────────────────
    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
        </head><body>
        <div style="background:#111918; border:1px solid #1f2937;
                    border-left:4px solid #0d9488; border-radius:10px;
                    padding:0.9rem 1.1rem; margin-bottom:0.5rem;">
          <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.3rem;">
            <span style="font-size:1.2rem;">{phase_info['icon']}</span>
            <span style="font-family:'Syne',sans-serif; font-weight:700;
                         color:#e2f0ef; font-size:0.9rem;">
              {phase_info['label']}
            </span>
          </div>
          <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                      font-size:0.78rem; margin-bottom:0.2rem;">
            🤖 {phase_info['agents']}
          </div>
          <div style="font-family:'DM Sans',sans-serif; color:#475569;
                      font-size:0.75rem;">
            {phase_info['desc']}
          </div>
        </div>
        </body></html>""",
        height=110,
    )

    selected = st.selectbox(
        f"Select model for {phase_info['label']}",
        options=options,
        index=current_idx,
        key=f"selectbox_{session_key}",
        label_visibility="collapsed",
    )

    # Save to session state
    if selected != "— Select a model —":
        st.session_state[session_key] = selected
        _render_model_info_badge(selected)
        return selected
    else:
        # Clear if deselected
        st.session_state[session_key] = None
        st.caption("⚠️ Please select a model to run this phase.")
        return None


def _render_model_info_badge(model_name: str):
    if model_name not in AVAILABLE_MODELS:
        return
    cfg      = AVAILABLE_MODELS[model_name]
    provider = cfg["provider"]
    color    = PROVIDER_COLORS.get(provider, "#0d9488")
    status   = cfg.get("status", "")
    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
        </head><body>
        <div style="background:#0a1512; border:1px solid {color}33;
                    border-radius:8px; padding:0.6rem 0.9rem; margin-top:0.3rem;">
          <div style="display:flex; align-items:center; gap:0.6rem; flex-wrap:wrap;">
            <span style="background:{color}22; color:{color};
                         border:1px solid {color}44; border-radius:20px;
                         padding:0.2rem 0.7rem; font-size:0.72rem;
                         font-family:'DM Sans',sans-serif; white-space:nowrap;">
              {provider.title()}
            </span>
            <span style="background:#22c55e22; color:#22c55e;
                         border:1px solid #22c55e44; border-radius:20px;
                         padding:0.2rem 0.7rem; font-size:0.72rem;
                         font-family:'DM Sans',sans-serif; white-space:nowrap;">
              {status}
            </span>
            <span style="font-family:'DM Sans',sans-serif; color:#64748b;
                         font-size:0.72rem;">
              {cfg['tpm_limit']} | {cfg['best_for']}
            </span>
          </div>
        </div>
        </body></html>""",
        height=55,
    )


def render_all_phase_selectors():
    """
    Render model selectors for ALL 4 phases at once.
    Used in sidebar or dashboard overview.
    """
    st.markdown(
        """
        <div style="font-family:'Syne',sans-serif; font-weight:700;
                    color:#2dd4bf; font-size:0.95rem; margin-bottom:0.8rem;">
            🤖 Model Selection — All Phases
        </div>
        <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                    font-size:0.78rem; margin-bottom:1rem; line-height:1.5;">
            Select a different model for each phase.<br>
            No default — you must choose before running.
        </div>
        """,
        unsafe_allow_html=True,
    )
    for phase_key in ["phase1", "phase2", "phase3", "phase4"]:
        render_phase_model_selector(phase_key)
        st.markdown("<br>", unsafe_allow_html=True)


def get_phase_selection_summary() -> dict:
    """Return current model selections for all phases."""
    return {
        phase_key: st.session_state.get(session_key, None)
        for phase_key, session_key in PHASE_MODEL_KEYS.items()
    }


def render_selection_status_bar():
    """
    Show a compact status bar of model selections.
    Use at top of each page.
    """
    summary = get_phase_selection_summary()
    phase_labels = {
        "phase1": "P1 Intake",
        "phase2": "P2 Diagnosis",
        "phase3": "P3 Treatment",
        "phase4": "P4 Summary",
    }
    cards_html = ""
    for pk, label in phase_labels.items():
        model = summary.get(pk)
        if model:
            cfg   = AVAILABLE_MODELS.get(model, {})
            prov  = cfg.get("provider", "")
            color = PROVIDER_COLORS.get(prov, "#0d9488")
            # Short display name
            short = (
                model.split("—")[-1].strip()
                if "—" in model
                else model.split(" ", 1)[-1][:20]
            )
            cards_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-top:2px solid {color}; border-radius:8px;
                        padding:0.5rem 0.7rem; text-align:center; flex:1;">
              <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                          font-size:0.68rem;">{label}</div>
              <div style="font-family:'DM Sans',sans-serif; color:{color};
                          font-size:0.72rem; font-weight:500; margin-top:0.1rem;">
                ✓ {short[:22]}
              </div>
            </div>
            """
        else:
            cards_html += f"""
            <div style="background:#111918; border:1px solid #ef444433;
                        border-top:2px solid #ef4444; border-radius:8px;
                        padding:0.5rem 0.7rem; text-align:center; flex:1;">
              <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                          font-size:0.68rem;">{label}</div>
              <div style="font-family:'DM Sans',sans-serif; color:#ef4444;
                          font-size:0.72rem; margin-top:0.1rem;">
                ✗ Not selected
              </div>
            </div>
            """

    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}
        .bar{{display:flex; gap:0.4rem;}}</style>
        </head><body>
        <div class="bar">{cards_html}</div>
        </body></html>""",
        height=75,
    )
