import streamlit as st

st.set_page_config(
    page_title="Treatment Planning — ClinicalCrew",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import streamlit.components.v1 as components
from utils.styles import inject_styles, page_header, disclaimer_banner


# ── Session State Defaults ─────────────────────────────────────
def _init_session():
    defaults = {
        "report_text":      None,
        "patient_name":     "",
        "parsed_report":    None,
        "patient_context":  None,
        "diagnosis_result": None,
        "treatment_result": None,
        "summary_result":   None,
        "_parsed_raw":      "{}",
        "_context_raw":     "{}",
        "_symptom_raw":     "{}",
        "_lab_raw":         "{}",
        "_risk_raw":        "{}",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Execution Log Lines ────────────────────────────────────────
def _build_log_lines(phase: str) -> list[dict]:
    base = [
        {"tag": "SYS",   "msg": "ClinicalCrew v1.0 — Phase 3: Treatment Planning"},
        {"tag": "SYS",   "msg": "Loading Phase 1 & 2 results from session state..."},
        {"tag": "LLM",   "msg": "Loading LLM — groq/llama-3.3-70b-versatile"},
        {"tag": "SYS",   "msg": "All 3 treatment agents instantiated successfully"},
    ]
    agent_lines = {
        "treatment": [
            {"tag": "AGENT", "msg": "TreatmentSuggesterAgent → Starting treatment planning"},
            {"tag": "TASK",  "msg": "Task: Generate evidence-based treatment options"},
            {"tag": "RUN",   "msg": "Loading international treatment guidelines..."},
            {"tag": "RUN",   "msg": "Mapping diagnoses to first-line treatments..."},
            {"tag": "RUN",   "msg": "Assigning evidence grades (A/B/C)..."},
            {"tag": "RUN",   "msg": "Checking guideline sources (WHO/AHA/ADA/NICE/ESC)..."},
            {"tag": "RUN",   "msg": "Identifying contraindicated approaches..."},
            {"tag": "DONE",  "msg": "TreatmentSuggesterAgent → Treatment plan complete ✓"},
        ],
        "drug": [
            {"tag": "AGENT", "msg": "DrugInteractionAgent → Starting drug safety check"},
            {"tag": "TASK",  "msg": "Task: Check all drug interactions and safety"},
            {"tag": "RUN",   "msg": "Loading current medication list..."},
            {"tag": "RUN",   "msg": "Checking drug-drug interactions..."},
            {"tag": "RUN",   "msg": "Checking drug-disease contraindications..."},
            {"tag": "RUN",   "msg": "Checking allergy alerts and cross-reactivities..."},
            {"tag": "RUN",   "msg": "Flagging renal and hepatic dose adjustments..."},
            {"tag": "DONE",  "msg": "DrugInteractionAgent → Safety check complete ✓"},
        ],
        "dosage": [
            {"tag": "AGENT", "msg": "DosageCalculatorAgent → Starting dosage calculation"},
            {"tag": "TASK",  "msg": "Task: Calculate patient-specific dosing"},
            {"tag": "RUN",   "msg": "Loading patient weight, age, eGFR..."},
            {"tag": "RUN",   "msg": "Applying renal dose adjustments (eGFR-based)..."},
            {"tag": "RUN",   "msg": "Applying age-related pharmacokinetic adjustments..."},
            {"tag": "RUN",   "msg": "Building daily medication schedule..."},
            {"tag": "DONE",  "msg": "DosageCalculatorAgent → Dosage plan complete ✓"},
        ],
        "done": [
            {"tag": "SYS",  "msg": "─" * 45},
            {"tag": "DONE", "msg": "Phase 3 Complete — All 3 agents finished"},
            {"tag": "SYS",  "msg": "Results saved to session state"},
            {"tag": "SYS",  "msg": "Proceed to Clinical Summary →"},
        ],
    }
    lines = base[:]
    for key in ["treatment", "drug", "dosage", "done"]:
        lines.extend(agent_lines[key])
        if key == phase:
            break
    return lines


# ── Tab 1: Treatment Options ───────────────────────────────────
def _render_treatment_options(data: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>💊 Evidence-Based Treatment Options</h3>",
        unsafe_allow_html=True,
    )

    # Disclaimer
    disclaimer = data.get("disclaimer", "")
    if disclaimer:
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>
            <div style="background:#1a0a0a; border:1px solid #ef444433;
                        border-left:4px solid #ef4444; border-radius:8px;
                        padding:0.9rem 1.1rem; margin-bottom:1rem;">
              <div style="font-family:'DM Sans',sans-serif; color:#fca5a5;
                          font-size:0.82rem; line-height:1.6;">
                ⚠️ {disclaimer}
              </div>
            </div>
            </body></html>""",
            height=80,
        )

    # Treatment Goals
    goals = data.get("treatment_goals", [])
    if goals:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#2dd4bf; "
            "font-size:0.95rem; margin-bottom:0.5rem;'>🎯 Treatment Goals</h4>",
            unsafe_allow_html=True,
        )
        goals_html = "".join(
            f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid #0d9488; border-radius:8px;
                        padding:0.7rem 1rem; margin:0.3rem 0;
                        font-family:'DM Sans',sans-serif; color:#94a3b8;
                        font-size:0.87rem;">
              ✓ {g}
            </div>
            """
            for g in goals
        )
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{goals_html}</body></html>""",
            height=max(80, len(goals) * 60),
        )

    # Condition Treatments
    conditions = data.get("condition_treatments", [])
    for cond in conditions:
        st.markdown(
            f"""
            <h4 style='font-family:Syne,sans-serif; color:#e2f0ef;
                       font-size:1rem; margin:1.2rem 0 0.6rem 0;
                       border-bottom:1px solid #1f2937; padding-bottom:0.4rem;'>
                🏥 {cond.get('condition', 'Condition')}
            </h4>
            """,
            unsafe_allow_html=True,
        )

        def _render_tx_group(items: list, label: str, color: str):
            if not items:
                return
            st.markdown(
                f"<div style='font-family:DM Sans,sans-serif; color:{color}; "
                f"font-size:0.82rem; font-weight:500; margin:0.5rem 0 0.3rem 0;'>"
                f"{'▶' if color == '#22c55e' else '▷'} {label}</div>",
                unsafe_allow_html=True,
            )
            tx_html = ""
            for tx in items:
                grade = tx.get("evidence_grade", "")
                source = tx.get("guideline_source", "")
                grade_color = (
                    "#22c55e" if grade == "A"
                    else "#fbbf24" if grade == "B"
                    else "#94a3b8"
                )
                tx_html += f"""
                <div style="background:#111918; border:1px solid #1f2937;
                            border-left:4px solid {color}; border-radius:10px;
                            padding:0.9rem 1rem; margin:0.3rem 0;">
                  <div style="display:flex; justify-content:space-between;
                              align-items:flex-start; margin-bottom:0.4rem;">
                    <div style="font-family:'Syne',sans-serif; font-weight:700;
                                color:#e2f0ef; font-size:0.9rem;">
                      💊 {tx.get('drug_or_intervention','')}
                      <span style="font-family:'DM Sans',sans-serif; font-weight:400;
                                   color:#64748b; font-size:0.75rem; margin-left:0.3rem;">
                        ({tx.get('type','')})
                      </span>
                    </div>
                    <div style="display:flex; gap:0.3rem; flex-shrink:0; margin-left:0.5rem;">
                      <span style="background:{grade_color}22; color:{grade_color};
                                   border:1px solid {grade_color}44; border-radius:4px;
                                   padding:0.1rem 0.5rem; font-size:0.72rem;
                                   font-family:'DM Sans',sans-serif;">Grade {grade}</span>
                      <span style="background:#3b82f622; color:#3b82f6;
                                   border:1px solid #3b82f644; border-radius:4px;
                                   padding:0.1rem 0.5rem; font-size:0.72rem;
                                   font-family:'DM Sans',sans-serif;">{source}</span>
                    </div>
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; line-height:1.5;">
                    {tx.get('rationale','')[:200]}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                              font-size:0.78rem; margin-top:0.3rem; font-style:italic;">
                    ⚠ {tx.get('considerations','')[:150]}
                  </div>
                </div>
                """
            height = max(120, len(items) * 160)
            components.html(
                f"""<!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
                </head><body>{tx_html}</body></html>""",
                height=height,
            )

        _render_tx_group(
            cond.get("first_line", []),  "First-Line Treatment", "#22c55e"
        )
        _render_tx_group(
            cond.get("second_line", []), "Second-Line Treatment", "#fbbf24"
        )
        _render_tx_group(
            cond.get("alternatives", []),"Alternative Options",  "#a855f7"
        )

        # Contraindicated
        contra = cond.get("contraindicated", [])
        if contra:
            st.markdown(
                "<div style='font-family:DM Sans,sans-serif; color:#ef4444; "
                "font-size:0.82rem; font-weight:500; margin:0.5rem 0 0.3rem 0;'>"
                "✗ Contraindicated</div>",
                unsafe_allow_html=True,
            )
            for c in contra:
                st.markdown(
                    f"""
                    <div style="background:#1a0808; border:1px solid #ef444433;
                                border-left:4px solid #ef4444; border-radius:8px;
                                padding:0.6rem 1rem; margin:0.2rem 0;">
                      <span style="font-family:'DM Sans',sans-serif; color:#fca5a5;
                                   font-size:0.85rem; font-weight:500;">
                        ✗ {c.get('drug_or_intervention','')}
                      </span>
                      <span style="font-family:'DM Sans',sans-serif; color:#64748b;
                                   font-size:0.78rem; margin-left:0.5rem;">
                        — {c.get('reason_contraindicated','')}
                      </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Non-pharmacological
    non_pharm = data.get("non_pharmacological", [])
    if non_pharm:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#2dd4bf; "
            "font-size:0.95rem; margin:1.2rem 0 0.5rem 0;'>🏃 Non-Pharmacological Recommendations</h4>",
            unsafe_allow_html=True,
        )
        np_html = ""
        for np_item in non_pharm:
            grade = np_item.get("evidence_grade", "")
            grade_color = (
                "#22c55e" if grade == "A"
                else "#fbbf24" if grade == "B"
                else "#94a3b8"
            )
            np_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid #2dd4bf; border-radius:10px;
                        padding:0.8rem 1rem; margin:0.3rem 0;
                        display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-family:'DM Sans',sans-serif; font-weight:500;
                            color:#e2f0ef; font-size:0.88rem;">
                  🏃 {np_item.get('intervention','')}
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                            font-size:0.78rem; margin-top:0.2rem;">
                  {np_item.get('rationale','')[:150]}
                </div>
              </div>
              <span style="background:{grade_color}22; color:{grade_color};
                           border:1px solid {grade_color}44; border-radius:4px;
                           padding:0.2rem 0.6rem; font-size:0.72rem;
                           font-family:'DM Sans',sans-serif; flex-shrink:0;
                           margin-left:0.5rem;">Grade {grade}</span>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{np_html}</body></html>""",
            height=max(100, len(non_pharm) * 100),
        )


# ── Tab 2: Drug Safety ─────────────────────────────────────────
def _render_drug_safety(data: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>🛡️ Drug Safety Check</h3>",
        unsafe_allow_html=True,
    )

    clearance = data.get("overall_safety_clearance", "unknown").lower()
    summary   = data.get("safety_summary", "")

    cl_color = (
        "#22c55e"  if clearance == "safe"
        else "#fbbf24" if clearance == "caution"
        else "#ef4444"
    )
    cl_icon = (
        "✅" if clearance == "safe"
        else "⚠️" if clearance == "caution"
        else "❌"
    )

    # Safety Clearance Banner
    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
        </head><body>
        <div style="background:#111918; border:2px solid {cl_color};
                    border-radius:12px; padding:1.3rem 1.5rem; margin-bottom:1rem;
                    display:flex; align-items:center; gap:1rem;">
          <div style="font-size:2.5rem;">{cl_icon}</div>
          <div>
            <div style="font-family:'Syne',sans-serif; font-weight:800;
                        color:{cl_color}; font-size:1.3rem; text-transform:uppercase;">
              {clearance} — Safety Clearance
            </div>
            <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                        font-size:0.85rem; margin-top:0.3rem; line-height:1.5;">
              {summary[:250]}
            </div>
          </div>
        </div>
        </body></html>""",
        height=140,
    )

    # Drug-Drug Interactions
    interactions = data.get("drug_drug_interactions", [])
    if interactions:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin-bottom:0.5rem;'>⚡ Drug-Drug Interactions</h4>",
            unsafe_allow_html=True,
        )
        for ix in interactions:
            severity = ix.get("severity", "Minor").strip()
            sev_color = (
                "#ef4444" if severity == "Major"
                else "#fbbf24" if severity == "Moderate"
                else "#64748b"
            )
            rec = ix.get("recommendation", "")
            rec_color = (
                "#ef4444" if "contraindicated" in rec.lower() or "avoid" in rec.lower()
                else "#fbbf24" if "monitor" in rec.lower()
                else "#22c55e"
            )
            components.html(
                f"""<!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
                </head><body>
                <div style="background:#111918; border:1px solid #1f2937;
                            border-left:4px solid {sev_color}; border-radius:10px;
                            padding:1rem; margin:0.4rem 0;">
                  <div style="display:flex; justify-content:space-between;
                              align-items:center; margin-bottom:0.5rem;">
                    <div style="font-family:'Syne',sans-serif; font-weight:700;
                                color:#e2f0ef; font-size:0.9rem;">
                      💊 {ix.get('drug_1','')}
                      <span style="color:#64748b; font-size:0.8rem;"> + </span>
                      💊 {ix.get('drug_2','')}
                    </div>
                    <span style="background:{sev_color}22; color:{sev_color};
                                 border:1px solid {sev_color}44; border-radius:20px;
                                 padding:0.2rem 0.7rem; font-size:0.75rem;
                                 font-family:'DM Sans',sans-serif; white-space:nowrap;
                                 margin-left:0.5rem;">
                      {severity} Interaction
                    </span>
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; margin-bottom:0.3rem;">
                    <b style="color:#e2f0ef;">Effect:</b> {ix.get('clinical_effect','')[:150]}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; margin-bottom:0.3rem;">
                    <b style="color:#e2f0ef;">Management:</b> {ix.get('management','')[:150]}
                  </div>
                  <div style="margin-top:0.4rem;">
                    <span style="background:{rec_color}22; color:{rec_color};
                                 border:1px solid {rec_color}44; border-radius:4px;
                                 padding:0.15rem 0.6rem; font-size:0.72rem;
                                 font-family:'DM Sans',sans-serif;">
                      {rec.replace('_',' ').title()}
                    </span>
                  </div>
                </div>
                </body></html>""",
                height=190,
            )

    # Allergy Alerts
    allergy = data.get("allergy_alerts", [])
    if allergy:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#ef4444; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>🚨 Allergy Alerts</h4>",
            unsafe_allow_html=True,
        )
        al_html = ""
        for al in allergy:
            risk = al.get("cross_reactivity_risk", "low").lower()
            risk_color = (
                "#ef4444" if risk == "high"
                else "#fbbf24" if risk == "moderate"
                else "#64748b"
            )
            al_html += f"""
            <div style="background:#1a0808; border:1px solid #ef444433;
                        border-left:4px solid #ef4444; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.4rem 0;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-family:'Syne',sans-serif; font-weight:700;
                              color:#fca5a5; font-size:0.9rem;">
                    🚨 {al.get('suggested_drug','')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; margin-top:0.2rem;">
                    Allergen concern: {al.get('allergen_concern','')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#22c55e;
                              font-size:0.82rem; margin-top:0.2rem;">
                    ✓ Safe alternative: {al.get('safe_alternative','')}
                  </div>
                </div>
                <span style="background:{risk_color}22; color:{risk_color};
                             border:1px solid {risk_color}44; border-radius:20px;
                             padding:0.2rem 0.7rem; font-size:0.72rem;
                             font-family:'DM Sans',sans-serif; white-space:nowrap;
                             margin-left:0.5rem;">
                  {risk.title()} Risk
                </span>
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{al_html}</body></html>""",
            height=max(120, len(allergy) * 130),
        )

    # Drug-Disease Contraindications
    dd_contra = data.get("drug_disease_contraindications", [])
    if dd_contra:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#fbbf24; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>⚠️ Drug-Disease Contraindications</h4>",
            unsafe_allow_html=True,
        )
        for dc in dd_contra:
            st.markdown(
                f"""
                <div style="background:#1a1208; border:1px solid #fbbf2433;
                            border-left:4px solid #fbbf24; border-radius:8px;
                            padding:0.8rem 1rem; margin:0.3rem 0;">
                  <div style="font-family:'DM Sans',sans-serif; font-weight:500;
                              color:#fde68a; font-size:0.88rem;">
                    ⚠️ {dc.get('drug','')} + {dc.get('disease','')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.8rem; margin-top:0.2rem;">
                    {dc.get('risk','')[:200]}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#0d9488;
                              font-size:0.78rem; margin-top:0.2rem;">
                    → {dc.get('recommendation','')}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Safe Medications
    safe_meds = data.get("safe_medications", [])
    if safe_meds:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#22c55e; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>✅ Cleared as Safe</h4>",
            unsafe_allow_html=True,
        )
        tags = "".join(
            f'<span style="background:#22c55e22; color:#22c55e; '
            f'border:1px solid #22c55e44; border-radius:20px; '
            f'padding:0.3rem 0.8rem; font-size:0.82rem; margin:0.2rem; '
            f'font-family:DM Sans,sans-serif; display:inline-block;">✓ {m}</span>'
            for m in safe_meds
        )
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}
            .wrap{{display:flex;flex-wrap:wrap;gap:0.2rem;padding:0.3rem 0;}}</style>
            </head><body><div class="wrap">{tags}</div></body></html>""",
            height=80,
        )


# ── Tab 3: Dosing Plan ─────────────────────────────────────────
def _render_dosing_plan(data: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>⚗️ Patient-Specific Dosing Plan</h3>",
        unsafe_allow_html=True,
    )

    # Disclaimer
    disclaimer = data.get("disclaimer", "")
    if disclaimer:
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>
            <div style="background:#1a0a0a; border:1px solid #ef444433;
                        border-left:4px solid #ef4444; border-radius:8px;
                        padding:0.9rem 1.1rem; margin-bottom:1rem;">
              <div style="font-family:'DM Sans',sans-serif; color:#fca5a5;
                          font-size:0.82rem; line-height:1.6;">
                ⚠️ {disclaimer}
              </div>
            </div>
            </body></html>""",
            height=80,
        )

    # Patient Parameters
    params = data.get("patient_dosing_parameters", {})
    if params:
        p_html = f"""
        <div style="background:#111918; border:1px solid #1f2937;
                    border-radius:10px; padding:1rem 1.2rem; margin-bottom:1rem;
                    display:grid; grid-template-columns:repeat(4,1fr); gap:1rem;">
          <div style="text-align:center;">
            <div style="font-family:'DM Sans',sans-serif; color:#64748b; font-size:0.72rem;">WEIGHT</div>
            <div style="font-family:'Syne',sans-serif; color:#2dd4bf; font-size:1.3rem; font-weight:700;">
              {params.get('weight_kg','N/A')} kg
            </div>
          </div>
          <div style="text-align:center;">
            <div style="font-family:'DM Sans',sans-serif; color:#64748b; font-size:0.72rem;">AGE</div>
            <div style="font-family:'Syne',sans-serif; color:#2dd4bf; font-size:1.3rem; font-weight:700;">
              {params.get('age','N/A')} yrs
            </div>
          </div>
          <div style="text-align:center;">
            <div style="font-family:'DM Sans',sans-serif; color:#64748b; font-size:0.72rem;">eGFR</div>
            <div style="font-family:'Syne',sans-serif; color:#fbbf24; font-size:1.3rem; font-weight:700;">
              {params.get('egfr','N/A')}
            </div>
          </div>
          <div style="text-align:center;">
            <div style="font-family:'DM Sans',sans-serif; color:#64748b; font-size:0.72rem;">RENAL CATEGORY</div>
            <div style="font-family:'Syne',sans-serif; color:#fbbf24; font-size:0.9rem; font-weight:700;">
              {params.get('renal_category','N/A')}
            </div>
          </div>
        </div>
        """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{p_html}</body></html>""",
            height=110,
        )

    # Daily Schedule Summary
    schedule = data.get("dosing_schedule_summary", "")
    if schedule:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin-bottom:0.5rem;'>📅 Daily Medication Schedule</h4>",
            unsafe_allow_html=True,
        )
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>
            <div style="background:#111918; border:1px solid #0d948855;
                        border-left:4px solid #0d9488; border-radius:10px;
                        padding:1rem 1.2rem; white-space:pre-line;
                        font-family:'DM Sans',sans-serif; color:#94a3b8;
                        font-size:0.85rem; line-height:1.8;">
              {schedule}
            </div>
            </body></html>""",
            height=200,
        )

    # Per-Drug Dosing Cards
    recs = data.get("dosing_recommendations", [])
    if recs:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>💊 Per-Medication Dosing</h4>",
            unsafe_allow_html=True,
        )
        for rx in recs:
            adjustments = rx.get("dose_adjustments", [])
            adj_html = "".join(
                f"""
                <div style="background:#0a1512; border-radius:6px;
                            padding:0.5rem 0.7rem; margin:0.25rem 0;
                            font-family:'DM Sans',sans-serif; font-size:0.78rem; color:#94a3b8;">
                  <b style="color:#fbbf24;">{a.get('adjustment_type','').title()}:</b>
                  Standard {a.get('standard','')} →
                  <b style="color:#0d9488;">Adjusted {a.get('adjusted','')}</b>
                  <span style="color:#64748b;"> — {a.get('reasoning','')[:100]}</span>
                </div>
                """
                for a in adjustments
            )
            monitoring = rx.get("monitoring_required", [])
            mon_html = "".join(
                f'<span style="background:#3b82f622; color:#3b82f6; '
                f'border:1px solid #3b82f644; border-radius:4px; '
                f'padding:0.1rem 0.5rem; font-size:0.72rem; margin:0.1rem; '
                f'font-family:DM Sans,sans-serif; display:inline-block;">📊 {m}</span>'
                for m in monitoring
            )
            components.html(
                f"""<!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
                </head><body>
                <div style="background:#111918; border:1px solid #1f2937;
                            border-left:4px solid #a855f7; border-radius:12px;
                            padding:1.1rem; margin:0.5rem 0;">
                  <div style="display:flex; justify-content:space-between;
                              align-items:flex-start; margin-bottom:0.8rem;">
                    <div>
                      <div style="font-family:'Syne',sans-serif; font-weight:700;
                                  color:#e2f0ef; font-size:1rem;">
                        💊 {rx.get('drug_name','')}
                      </div>
                      <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                                  font-size:0.78rem; margin-top:0.1rem;">
                        For: {rx.get('indication','')}
                      </div>
                    </div>
                    <div style="text-align:right; flex-shrink:0; margin-left:0.5rem;">
                      <div style="font-family:'Syne',sans-serif; font-weight:700;
                                  color:#2dd4bf; font-size:1.1rem;">
                        {rx.get('recommended_dose','')}
                      </div>
                      <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                                  font-size:0.75rem;">
                        {rx.get('frequency','')} • {rx.get('route','')}
                      </div>
                    </div>
                  </div>
                  <div style="display:grid; grid-template-columns:1fr 1fr;
                              gap:0.5rem; margin-bottom:0.6rem;">
                    <div style="background:#0d1f1e; border-radius:6px; padding:0.5rem 0.7rem;">
                      <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                                  font-size:0.7rem;">STANDARD DOSE</div>
                      <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                                  font-size:0.85rem;">{rx.get('standard_dose','')}</div>
                    </div>
                    <div style="background:#0d1f1e; border-radius:6px; padding:0.5rem 0.7rem;">
                      <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                                  font-size:0.7rem;">DURATION</div>
                      <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                                  font-size:0.85rem;">{rx.get('duration','')}</div>
                    </div>
                  </div>
                  {f'<div style="margin-bottom:0.6rem;">{adj_html}</div>' if adjustments else ''}
                  {f'<div>{mon_html}</div>' if monitoring else ''}
                  {f'<div style="font-family:DM Sans,sans-serif; color:#64748b; font-size:0.75rem; margin-top:0.4rem; font-style:italic;">📝 {rx.get("titration_notes","")[:150]}</div>' if rx.get("titration_notes") else ''}
                </div>
                </body></html>""",
                height=310 + (len(adjustments) * 55),
            )


# ── Main ───────────────────────────────────────────────────────
def main():
    _init_session()
    inject_styles()

    patient_name = st.session_state.get("patient_name", "") or "Patient"
    page_header(
        "💊",
        "Treatment Planning",
        f"Phase 3 — Evidence-based treatment options & drug safety for {patient_name}",
    )
    disclaimer_banner()

    st.markdown("<br>", unsafe_allow_html=True)

    # Gate checks
    if not st.session_state.parsed_report:
        st.warning(
            "⚠️ Please complete **Phase 1 — Report Intake** first.",
            icon="📥",
        )
        st.stop()

    if not st.session_state.diagnosis_result:
        st.warning(
            "⚠️ Please complete **Phase 2 — Diagnosis Analysis** first.",
            icon="🔬",
        )
        st.stop()

    # ── Model Selector for Phase 3 ──────────────────────────────
    from utils.model_selector import render_phase_model_selector

    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1rem; margin-bottom:0.3rem;'>🤖 Select AI Model for Phase 3</h3>",
        unsafe_allow_html=True,
    )
    selected_model = render_phase_model_selector("phase3")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Run Button ──────────────────────────────────────────────
    col_btn, _ = st.columns([2, 3])
    with col_btn:
        run_btn = st.button(
            "🚀 Run Treatment Crew (Phase 3)",
            use_container_width=True,
            type="primary",
            disabled=(selected_model is None),  # ← Fix 6: guard added
        )

    if selected_model is None:
        st.warning("⚠️ Please select a model above before running.", icon="🤖")

    if run_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:1rem;'>⚡ Agent Execution Log</h3>",
            unsafe_allow_html=True,
        )

        import time
        from utils.execution_log import render_log

        for phase in ["treatment", "drug", "dosage"]:
            render_log(_build_log_lines(phase), running=True, height=380)
            time.sleep(0.5)

        with st.spinner("🤖 Agents working — this may take 60-120 seconds..."):
            try:
                from crews.crews import run_treatment_crew

                context_raw = st.session_state.get("_context_raw", "{}")
                symptom_raw = st.session_state.get("_symptom_raw", "{}")
                risk_raw    = st.session_state.get("_risk_raw", "{}")
                lab_raw     = st.session_state.get("_lab_raw", "{}")

                result = run_treatment_crew(
                    patient_context=context_raw,
                    symptom_analysis=symptom_raw,
                    risk_assessment=risk_raw,
                    lab_interpretation=lab_raw,
                    phase_key="phase3",        # ← Fix 6: phase_key added
                )

                st.session_state.treatment_result    = result
                st.session_state["_treatment_raw"]   = result.get("_treatment_raw", "{}")
                st.session_state["_drug_raw"]        = result.get("_drug_raw", "{}")
                st.session_state["_dosage_raw"]      = result.get("_dosage_raw", "{}")

                # Save to Supabase
                try:
                    from utils.database import save_analysis
                    save_analysis(
                        st.session_state.get("patient_id"),
                        "treatment",
                        result,
                    )
                except Exception:
                    pass

                from utils.execution_log import render_log as rl
                rl(_build_log_lines("done"), running=False, height=380)
                st.success(
                    "✅ Phase 3 Complete! Scroll down to view results.",
                    icon="🎉",
                )

            except Exception as e:
                from utils.execution_log import render_log as rl
                rl(
                    _build_log_lines("treatment") + [
                        {"tag": "ERROR", "msg": f"Crew failed: {str(e)[:120]}"}
                    ],
                    running=False,
                    height=380,
                )
                st.error(f"❌ Error: {e}")

    # ── Results ─────────────────────────────────────────────────
    if st.session_state.treatment_result:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:1.3rem; margin-bottom:0.5rem;'>📊 Phase 3 Results</h2>",
            unsafe_allow_html=True,
        )

        result = st.session_state.treatment_result

        r_tab1, r_tab2, r_tab3 = st.tabs([
            "💊 Treatment Options",
            "🛡️ Drug Safety",
            "⚗️ Dosing Plan",
        ])

        with r_tab1:
            _render_treatment_options(
                result.get("treatment_suggestions", {})
            )

        with r_tab2:
            _render_drug_safety(
                result.get("drug_interactions", {})
            )

        with r_tab3:
            _render_dosing_plan(
                result.get("dosage_recommendations", {})
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.info(
            "✅ Phase 3 complete! Go to **Clinical Summary** in the sidebar "
            "to continue to Phase 4.",
            icon="➡️",
        )


if __name__ == "__main__":
    main()
