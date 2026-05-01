import streamlit as st

st.set_page_config(
    page_title="Diagnosis Analysis — ClinicalCrew",
    page_icon="🔬",
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
        "validation":       None,
        "diagnosis_result": None,
        "treatment_result": None,
        "summary_result":   None,
        "_parsed_raw":      "{}",
        "_context_raw":     "{}",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Execution Log Lines ────────────────────────────────────────
def _build_log_lines(phase: str) -> list[dict]:
    base = [
        {"tag": "SYS",   "msg": "ClinicalCrew v1.0 — Phase 2: Diagnosis Analysis"},
        {"tag": "SYS",   "msg": "Loading Phase 1 results from session state..."},
        {"tag": "LLM",   "msg": "Loading LLM — groq/llama-3.3-70b-versatile"},
        {"tag": "SYS",   "msg": "All 3 diagnosis agents instantiated successfully"},
    ]
    agent_lines = {
        "symptoms": [
            {"tag": "AGENT", "msg": "SymptomAnalyzerAgent → Starting symptom analysis"},
            {"tag": "TASK",  "msg": "Task: Analyze symptoms and generate differential diagnosis"},
            {"tag": "RUN",   "msg": "Identifying symptom clusters and syndromes..."},
            {"tag": "RUN",   "msg": "Building differential diagnosis list..."},
            {"tag": "RUN",   "msg": "Assigning likelihood scores (high/medium/low)..."},
            {"tag": "RUN",   "msg": "Flagging red flag symptoms..."},
            {"tag": "DONE",  "msg": "SymptomAnalyzerAgent → Symptom analysis complete ✓"},
        ],
        "labs": [
            {"tag": "AGENT", "msg": "LabInterpreterAgent → Starting lab interpretation"},
            {"tag": "TASK",  "msg": "Task: Interpret laboratory and investigation results"},
            {"tag": "RUN",   "msg": "Checking all values against reference ranges..."},
            {"tag": "RUN",   "msg": "Flagging critical and abnormal values..."},
            {"tag": "RUN",   "msg": "Identifying lab patterns and syndromes..."},
            {"tag": "RUN",   "msg": "Noting missing important investigations..."},
            {"tag": "DONE",  "msg": "LabInterpreterAgent → Lab interpretation complete ✓"},
        ],
        "risk": [
            {"tag": "AGENT", "msg": "RiskAssessorAgent → Starting risk assessment"},
            {"tag": "TASK",  "msg": "Task: Calculate risk level and action priorities"},
            {"tag": "RUN",   "msg": "Calculating overall risk level..."},
            {"tag": "RUN",   "msg": "Applying validated clinical scoring tools..."},
            {"tag": "RUN",   "msg": "Generating urgent action list (within hours)..."},
            {"tag": "RUN",   "msg": "Generating important action list (within days)..."},
            {"tag": "DONE",  "msg": "RiskAssessorAgent → Risk assessment complete ✓"},
        ],
        "done": [
            {"tag": "SYS",  "msg": "─" * 45},
            {"tag": "DONE", "msg": "Phase 2 Complete — All 3 agents finished"},
            {"tag": "SYS",  "msg": "Results saved to session state"},
            {"tag": "SYS",  "msg": "Proceed to Treatment Planning →"},
        ],
    }
    lines = base[:]
    for key in ["symptoms", "labs", "risk", "done"]:
        lines.extend(agent_lines[key])
        if key == phase:
            break
    return lines


# ── Tab 1: Symptom Analysis ────────────────────────────────────
def _render_symptom_analysis(data: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>🧠 Symptom Analysis & Differential Diagnosis</h3>",
        unsafe_allow_html=True,
    )

    # Clinical Impression
    impression = data.get("clinical_impression", "No impression available.")
    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
        </head><body>
        <div style="background:#111918; border:1px solid #1f2937;
                    border-left:4px solid #0d9488; border-radius:10px;
                    padding:1.2rem; margin-bottom:1rem;">
          <div style="font-family:'Syne',sans-serif; font-size:0.8rem;
                      color:#0d9488; margin-bottom:0.4rem; letter-spacing:0.08em;">
            CLINICAL IMPRESSION
          </div>
          <div style="font-family:'DM Sans',sans-serif; color:#e2f0ef;
                      font-size:0.92rem; line-height:1.7;">{impression}</div>
        </div>
        </body></html>""",
        height=130,
    )

    # Red Flags
    red_flags = data.get("red_flags", [])
    if red_flags:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#ef4444; "
            "font-size:0.95rem; margin:0.8rem 0 0.4rem 0;'>🚨 Red Flags</h4>",
            unsafe_allow_html=True,
        )
        flags_html = ""
        for f in red_flags:
            timeframe = f.get("timeframe", "")
            tf_color = (
                "#ef4444" if "immediate" in timeframe.lower()
                else "#fbbf24" if "hours" in timeframe.lower()
                else "#94a3b8"
            )
            flags_html += f"""
            <div style="background:#1a0a0a; border:1px solid #ef444433;
                        border-left:4px solid #ef4444; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.4rem 0;">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <div style="font-family:'Syne',sans-serif; font-weight:700;
                              color:#ef4444; font-size:0.9rem;">
                    🚨 {f.get('finding', '')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; margin-top:0.3rem;">
                    <b style="color:#fca5a5;">Concern:</b> {f.get('concern', '')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; margin-top:0.2rem;">
                    <b style="color:#fca5a5;">Action:</b> {f.get('action_required', '')}
                  </div>
                </div>
                <span style="background:{tf_color}22; color:{tf_color};
                             border:1px solid {tf_color}44; border-radius:20px;
                             padding:0.2rem 0.7rem; font-size:0.72rem;
                             font-family:'DM Sans',sans-serif; white-space:nowrap;
                             margin-left:0.5rem;">
                  {timeframe}
                </span>
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{flags_html}</body></html>""",
            height=max(120, len(red_flags) * 140),
        )

    # Differential Diagnosis
    ddx = data.get("differential_diagnosis", [])
    if ddx:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>🔍 Differential Diagnosis</h4>",
            unsafe_allow_html=True,
        )
        for dx in ddx:
            likelihood = dx.get("likelihood", "low").lower()
            urgency    = dx.get("urgency", "non-urgent").lower()
            lh_color = (
                "#ef4444" if likelihood == "high"
                else "#fbbf24" if likelihood == "medium"
                else "#22c55e"
            )
            urg_color = (
                "#ef4444" if "emergent" in urgency
                else "#fbbf24" if "urgent" in urgency
                else "#64748b"
            )
            supporting = dx.get("supporting_evidence", [])
            against    = dx.get("against_evidence", [])
            sup_html = "".join(
                f'<span style="background:#22c55e22; color:#22c55e; '
                f'border:1px solid #22c55e44; border-radius:4px; '
                f'padding:0.1rem 0.5rem; font-size:0.72rem; margin:0.1rem; '
                f'display:inline-block;">✓ {s}</span>'
                for s in supporting[:4]
            )
            agt_html = "".join(
                f'<span style="background:#ef444422; color:#ef4444; '
                f'border:1px solid #ef444444; border-radius:4px; '
                f'padding:0.1rem 0.5rem; font-size:0.72rem; margin:0.1rem; '
                f'display:inline-block;">✗ {a}</span>'
                for a in against[:3]
            )
            components.html(
                f"""<!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
                </head><body>
                <div style="background:#111918; border:1px solid #1f2937;
                            border-left:4px solid {lh_color}; border-radius:10px;
                            padding:1rem; margin:0.4rem 0;">
                  <div style="display:flex; justify-content:space-between;
                              align-items:center; margin-bottom:0.5rem;">
                    <div style="font-family:'Syne',sans-serif; font-weight:700;
                                color:#e2f0ef; font-size:0.95rem;">
                      {dx.get('diagnosis','')}
                    </div>
                    <div style="display:flex; gap:0.4rem;">
                      <span style="background:{lh_color}22; color:{lh_color};
                                   border:1px solid {lh_color}44; border-radius:20px;
                                   padding:0.2rem 0.7rem; font-size:0.72rem;
                                   font-family:'DM Sans',sans-serif;">
                        {likelihood.title()} Likelihood
                      </span>
                      <span style="background:{urg_color}22; color:{urg_color};
                                   border:1px solid {urg_color}44; border-radius:20px;
                                   padding:0.2rem 0.7rem; font-size:0.72rem;
                                   font-family:'DM Sans',sans-serif;">
                        {urgency.title()}
                      </span>
                    </div>
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; line-height:1.6; margin-bottom:0.6rem;">
                    {dx.get('reasoning','')[:300]}
                  </div>
                  <div style="margin-bottom:0.3rem;">{sup_html}</div>
                  <div>{agt_html}</div>
                </div>
                </body></html>""",
                height=220,
            )

    # Disclaimer
    disclaimer = data.get("disclaimer", "")
    if disclaimer:
        st.info(f"ℹ️ {disclaimer}")


# ── Tab 2: Lab Interpretation ──────────────────────────────────
def _render_lab_interpretation(data: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>🧪 Laboratory Interpretation</h3>",
        unsafe_allow_html=True,
    )

    # Critical Values
    critical = data.get("critical_values", [])
    if critical:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#ef4444; "
            "font-size:0.95rem; margin-bottom:0.5rem;'>🚨 Critical Values</h4>",
            unsafe_allow_html=True,
        )
        crit_html = ""
        for cv in critical:
            crit_html += f"""
            <div style="background:#1a0808; border:1px solid #ef444455;
                        border-left:4px solid #ef4444; border-radius:10px;
                        padding:1rem; margin:0.4rem 0;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-family:'Syne',sans-serif; font-weight:700;
                              color:#ef4444; font-size:0.95rem;">
                    🚨 {cv.get('test_name','')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#fca5a5;
                              font-size:1.1rem; font-weight:600; margin-top:0.2rem;">
                    {cv.get('value','')}
                    <span style="font-size:0.75rem; color:#94a3b8;">
                      (Ref: {cv.get('reference_range','')})
                    </span>
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; margin-top:0.3rem;">
                    {cv.get('clinical_significance','')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#fbbf24;
                              font-size:0.8rem; margin-top:0.2rem;">
                    ⚡ Action: {cv.get('recommended_action','')}
                  </div>
                </div>
                <span style="background:#ef444422; color:#ef4444;
                             border:1px solid #ef444444; border-radius:20px;
                             padding:0.3rem 0.8rem; font-size:0.75rem;
                             font-family:'DM Sans',sans-serif; white-space:nowrap;
                             margin-left:0.5rem;">
                  {cv.get('urgency','').upper()}
                </span>
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{crit_html}</body></html>""",
            height=max(150, len(critical) * 180),
        )

    # Abnormal Values
    abnormal = data.get("abnormal_values", [])
    if abnormal:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#fbbf24; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>⚠️ Abnormal Values</h4>",
            unsafe_allow_html=True,
        )
        abn_html = ""
        for av in abnormal:
            flag = av.get("flag", "")
            urgency = av.get("urgency", "routine").lower()
            urg_color = (
                "#ef4444" if urgency == "urgent"
                else "#fbbf24" if urgency == "soon"
                else "#64748b"
            )
            flag_color = "#ef4444" if flag == "H" else "#3b82f6"
            abn_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid {urg_color}; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.3rem 0;
                        display:flex; justify-content:space-between; align-items:center;">
              <div style="flex:1;">
                <div style="display:flex; align-items:center; gap:0.5rem;">
                  <span style="font-family:'Syne',sans-serif; font-weight:700;
                               color:#e2f0ef; font-size:0.88rem;">
                    {av.get('test_name','')}
                  </span>
                  <span style="background:{flag_color}22; color:{flag_color};
                               border:1px solid {flag_color}44; border-radius:4px;
                               padding:0.1rem 0.4rem; font-size:0.7rem;
                               font-family:'DM Sans',sans-serif;">{flag}</span>
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#2dd4bf;
                            font-size:0.9rem; font-weight:500; margin-top:0.2rem;">
                  {av.get('value','')}
                  <span style="color:#64748b; font-size:0.75rem;">
                    (Ref: {av.get('reference_range','')})
                  </span>
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                            font-size:0.78rem; margin-top:0.2rem;">
                  {av.get('clinical_significance','')[:150]}
                </div>
              </div>
              <span style="background:{urg_color}22; color:{urg_color};
                           border:1px solid {urg_color}44; border-radius:20px;
                           padding:0.2rem 0.6rem; font-size:0.7rem;
                           font-family:'DM Sans',sans-serif; white-space:nowrap;
                           margin-left:0.8rem;">{urgency.title()}</span>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{abn_html}</body></html>""",
            height=max(150, len(abnormal) * 130),
        )

    # Lab Patterns
    patterns = data.get("lab_patterns", [])
    if patterns:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#a855f7; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>🔗 Lab Patterns Identified</h4>",
            unsafe_allow_html=True,
        )
        pat_html = ""
        for p in patterns:
            tests = ", ".join(p.get("contributing_tests", []))
            pat_html += f"""
            <div style="background:#111918; border:1px solid #a855f733;
                        border-left:4px solid #a855f7; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.4rem 0;">
              <div style="font-family:'Syne',sans-serif; font-weight:700;
                          color:#c084fc; font-size:0.88rem;">
                🔗 {p.get('pattern_name','')}
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                          font-size:0.78rem; margin-top:0.2rem;">
                Tests: {tests}
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                          font-size:0.82rem; margin-top:0.3rem;">
                {p.get('clinical_significance','')}
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{pat_html}</body></html>""",
            height=max(120, len(patterns) * 130),
        )

    # Missing Tests
    missing = data.get("missing_important_tests", [])
    if missing:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#94a3b8; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>📋 Recommended Missing Tests</h4>",
            unsafe_allow_html=True,
        )
        for mt in missing:
            urgency   = mt.get("urgency", "routine")
            urg_color = (
                "#ef4444" if urgency == "urgent"
                else "#fbbf24" if urgency == "soon"
                else "#64748b"
            )
            st.markdown(
                f"""
                <div style="background:#111918; border:1px solid #1f2937;
                            border-radius:8px; padding:0.7rem 1rem;
                            margin:0.3rem 0; display:flex;
                            justify-content:space-between; align-items:center;">
                  <div>
                    <span style="font-family:'DM Sans',sans-serif; color:#e2f0ef;
                                 font-size:0.88rem; font-weight:500;">
                      🧪 {mt.get('test_name','')}
                    </span>
                    <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                                font-size:0.78rem; margin-top:0.2rem;">
                      {mt.get('reason_needed','')}
                    </div>
                  </div>
                  <span style="background:{urg_color}22; color:{urg_color};
                               border:1px solid {urg_color}44; border-radius:20px;
                               padding:0.2rem 0.6rem; font-size:0.7rem;
                               font-family:'DM Sans',sans-serif;">{urgency}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ── Tab 3: Risk Assessment ─────────────────────────────────────
def _render_risk_assessment(data: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>⚠️ Risk Assessment</h3>",
        unsafe_allow_html=True,
    )

    risk_level = data.get("overall_risk_level", "unknown").lower()
    reasoning  = data.get("risk_reasoning", "")
    disposition = data.get("disposition_recommendation", "")
    disp_reason = data.get("disposition_reasoning", "")

    risk_color = {
        "critical": "#ef4444",
        "high":     "#f97316",
        "moderate": "#fbbf24",
        "low":      "#22c55e",
    }.get(risk_level, "#64748b")

    # Risk Level Display
    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
        </head><body>
        <div style="background:#111918; border:1px solid #1f2937;
                    border-top:4px solid {risk_color}; border-radius:12px;
                    padding:1.5rem; text-align:center; margin-bottom:1rem;">
          <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                      font-size:0.8rem; letter-spacing:0.1em; margin-bottom:0.5rem;">
            OVERALL RISK LEVEL
          </div>
          <div style="font-family:'Syne',sans-serif; font-size:3rem;
                      font-weight:800; color:{risk_color};
                      text-transform:uppercase; letter-spacing:0.05em;">
            {risk_level}
          </div>
          <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                      font-size:0.85rem; margin-top:0.8rem; line-height:1.6;
                      max-width:600px; margin-left:auto; margin-right:auto;">
            {reasoning[:300] if reasoning else ''}
          </div>
        </div>
        </body></html>""",
        height=220,
    )

    # Disposition
    if disposition:
        disp_color = (
            "#ef4444" if "admit" in disposition.lower()
            else "#fbbf24" if "observe" in disposition.lower()
            else "#22c55e"
        )
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid {disp_color}; border-radius:10px;
                        padding:1rem 1.2rem; margin-bottom:1rem;">
              <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                          font-size:0.75rem; letter-spacing:0.08em;">DISPOSITION RECOMMENDATION</div>
              <div style="font-family:'Syne',sans-serif; font-weight:700;
                          color:{disp_color}; font-size:1.1rem; margin:0.3rem 0;
                          text-transform:uppercase;">
                {disposition.replace('_',' ')}
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                          font-size:0.82rem;">{disp_reason[:200]}</div>
            </div>
            </body></html>""",
            height=130,
        )

    # Clinical Scores
    scores = data.get("clinical_scores", [])
    applicable = [s for s in scores if s.get("applicable", False)]
    if applicable:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:0.5rem 0;'>📊 Clinical Scores</h4>",
            unsafe_allow_html=True,
        )
        score_html = ""
        for sc in applicable:
            score_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid #3b82f6; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.4rem 0;
                        display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-family:'Syne',sans-serif; font-weight:700;
                            color:#e2f0ef; font-size:0.88rem;">
                  {sc.get('score_name','')}
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                            font-size:0.8rem; margin-top:0.2rem;">
                  {sc.get('interpretation','')}
                </div>
              </div>
              <div style="font-family:'Syne',sans-serif; font-size:1.8rem;
                          font-weight:800; color:#3b82f6; margin-left:1rem;">
                {sc.get('score_value','')}
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{score_html}</body></html>""",
            height=max(120, len(applicable) * 120),
        )

    # Urgent vs Important Actions
    urgent    = data.get("urgent_actions", [])
    important = data.get("important_actions", [])

    col_u, col_i = st.columns(2)

    with col_u:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#ef4444; "
            "font-size:0.95rem; margin:0.8rem 0 0.4rem 0;'>🚨 Urgent Actions (Hours)</h4>",
            unsafe_allow_html=True,
        )
        if urgent:
            for ua in urgent:
                components.html(
                    f"""<!DOCTYPE html><html><head>
                    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                    <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
                    </head><body>
                    <div style="background:#1a0808; border:1px solid #ef444433;
                                border-left:4px solid #ef4444; border-radius:8px;
                                padding:0.8rem; margin:0.3rem 0;">
                      <div style="font-family:'DM Sans',sans-serif; font-weight:500;
                                  color:#fca5a5; font-size:0.85rem;">
                        ⚡ {ua.get('action','')}
                      </div>
                      <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                                  font-size:0.75rem; margin-top:0.2rem;">
                        {ua.get('timeframe','')} • {ua.get('responsible_party','')}
                      </div>
                    </div>
                    </body></html>""",
                    height=90,
                )
        else:
            st.info("No urgent actions identified.")

    with col_i:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#fbbf24; "
            "font-size:0.95rem; margin:0.8rem 0 0.4rem 0;'>📌 Important Actions (Days)</h4>",
            unsafe_allow_html=True,
        )
        if important:
            for ia in important:
                components.html(
                    f"""<!DOCTYPE html><html><head>
                    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                    <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
                    </head><body>
                    <div style="background:#1a1208; border:1px solid #fbbf2433;
                                border-left:4px solid #fbbf24; border-radius:8px;
                                padding:0.8rem; margin:0.3rem 0;">
                      <div style="font-family:'DM Sans',sans-serif; font-weight:500;
                                  color:#fde68a; font-size:0.85rem;">
                        📌 {ia.get('action','')}
                      </div>
                      <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                                  font-size:0.75rem; margin-top:0.2rem;">
                        {ia.get('timeframe','')} • {ia.get('responsible_party','')}
                      </div>
                    </div>
                    </body></html>""",
                    height=90,
                )
        else:
            st.info("No important actions identified.")


# ── Main ───────────────────────────────────────────────────────
def main():
    _init_session()
    inject_styles()

    patient_name = st.session_state.get("patient_name", "") or "Patient"
    page_header(
        "🔬",
        "Diagnosis Analysis",
        f"Phase 2 — Symptom analysis, lab interpretation & risk assessment for {patient_name}",
    )
    disclaimer_banner()

    st.markdown("<br>", unsafe_allow_html=True)

    # Gate: Phase 1 must be complete
    if not st.session_state.parsed_report:
        st.warning(
            "⚠️ No report data found. Please complete **Phase 1 — Report Intake** first.",
            icon="📥",
        )
        st.stop()

    # ── Model Selector for Phase 2 ──────────────────────────────
    from utils.model_selector import render_phase_model_selector

    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1rem; margin-bottom:0.3rem;'>🤖 Select AI Model for Phase 2</h3>",
        unsafe_allow_html=True,
    )
    selected_model = render_phase_model_selector("phase2")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Run Button ──────────────────────────────────────────────
    col_btn, _ = st.columns([2, 3])
    with col_btn:
        run_btn = st.button(
            "🚀 Run Diagnosis Crew (Phase 2)",
            use_container_width=True,
            type="primary",
            disabled=(selected_model is None),
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
        for phase in ["symptoms", "labs", "risk"]:
            render_log = __import__(
                "utils.execution_log", fromlist=["render_log"]
            ).render_log
            render_log(_build_log_lines(phase), running=True, height=360)
            time.sleep(0.5)

        with st.spinner("🤖 Agents working — this may take 60-120 seconds..."):
            try:
                from crews.crews import run_diagnosis_crew
                from utils.execution_log import render_log as rl

                parsed_raw  = st.session_state.get("_parsed_raw", "{}")
                context_raw = st.session_state.get("_context_raw", "{}")

                result = run_diagnosis_crew(parsed_raw, context_raw, phase_key="phase2")

                st.session_state.diagnosis_result = result
                st.session_state["_symptom_raw"]  = result.get("_symptom_raw", "{}")
                st.session_state["_lab_raw"]       = result.get("_lab_raw", "{}")
                st.session_state["_risk_raw"]      = result.get("_risk_raw", "{}")

                # Save to Supabase
                try:
                    from utils.database import save_analysis
                    save_analysis(
                        st.session_state.get("patient_id"),
                        "diagnosis",
                        result,
                    )
                except Exception:
                    pass

                rl(_build_log_lines("done"), running=False, height=360)
                st.success(
                    "✅ Phase 2 Complete! Scroll down to view results.",
                    icon="🎉",
                )

            except Exception as e:
                from utils.execution_log import render_log as rl
                rl(
                    _build_log_lines("symptoms") + [
                        {"tag": "ERROR", "msg": f"Crew failed: {str(e)[:120]}"}
                    ],
                    running=False,
                    height=360,
                )
                st.error(f"❌ Error: {e}")

    # ── Results ─────────────────────────────────────────────────
    if st.session_state.diagnosis_result:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:1.3rem; margin-bottom:0.5rem;'>📊 Phase 2 Results</h2>",
            unsafe_allow_html=True,
        )

        result = st.session_state.diagnosis_result

        r_tab1, r_tab2, r_tab3 = st.tabs([
            "🧠 Symptom Analysis",
            "🧪 Lab Interpretation",
            "⚠️ Risk Assessment",
        ])

        with r_tab1:
            _render_symptom_analysis(
                result.get("symptom_analysis", {})
            )

        with r_tab2:
            _render_lab_interpretation(
                result.get("lab_interpretation", {})
            )

        with r_tab3:
            _render_risk_assessment(
                result.get("risk_assessment", {})
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.info(
            "✅ Phase 2 complete! Go to **Treatment Planning** in the sidebar "
            "to continue to Phase 3.",
            icon="➡️",
        )


if __name__ == "__main__":
    main()
