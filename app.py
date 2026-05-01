import streamlit as st

st.set_page_config(
    page_title="ClinicalCrew",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import inject_styles, page_header, disclaimer_banner, metric_card
from utils.database import get_patient_count, get_analysis_count
import streamlit.components.v1 as components


def main():
    inject_styles()

    # ── Model Selector Sidebar ─────────────────────────────────
    with st.sidebar:
        st.markdown(
            """
            <div style="font-family:'Syne',sans-serif; font-weight:700;
                        color:#2dd4bf; font-size:0.9rem; margin-bottom:0.5rem;">
                🤖 Select AI Model
            </div>
            """,
            unsafe_allow_html=True,
        )
        from config import AVAILABLE_MODELS
        model_names = list(AVAILABLE_MODELS.keys())
        selected = st.selectbox(
            "AI Model",
            model_names,
            index=0,
            label_visibility="collapsed",
            key="selected_model",
        )
        cfg = AVAILABLE_MODELS[selected]
        provider_colors = {
            "groq":       "#f97316",
            "gemini":     "#3b82f6",
            "openrouter": "#a855f7",
        }
        p_color = provider_colors.get(cfg["provider"], "#0d9488")
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:3px solid {p_color}; border-radius:8px;
                        padding:0.7rem 0.9rem; margin-top:0.3rem;">
              <div style="font-family:'DM Sans',sans-serif; color:{p_color};
                          font-size:0.72rem; font-weight:500; margin-bottom:0.3rem;
                          text-transform:uppercase; letter-spacing:0.05em;">
                {cfg['provider'].title()}
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                          font-size:0.75rem;">
                ✓ {cfg['tpm_limit']}
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                          font-size:0.72rem; margin-top:0.1rem;">
                Best for: {cfg['best_for']}
              </div>
            </div>
            </body></html>""",
            height=100,
        )
        st.markdown(
            """
            <div style="font-family:'DM Sans',sans-serif; color:#475569;
                        font-size:0.72rem; margin-top:0.5rem; line-height:1.5;">
                💡 If you hit rate limits, switch to a different model.
                Gemini 2.5 Flash recommended for best results.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

    # ── Hero Section ──────────────────────────────────────────
    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
          * { margin:0; padding:0; box-sizing:border-box; }
          body { background: transparent; }

          .hero {
            padding: 3rem 2rem 2rem 2rem;
            text-align: center;
            background: linear-gradient(135deg, #0a0f0f 0%, #0d1f1e 50%, #0a0f0f 100%);
            border-radius: 16px;
            border: 1px solid #1f2937;
            position: relative;
            overflow: hidden;
          }

          .hero::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(ellipse at center,
              rgba(13,148,136,0.08) 0%, transparent 60%);
            pointer-events: none;
          }

          .badge {
            display: inline-block;
            background: rgba(13,148,136,0.15);
            border: 1px solid rgba(13,148,136,0.4);
            color: #2dd4bf;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.78rem;
            font-weight: 500;
            letter-spacing: 0.1em;
            padding: 0.3rem 1rem;
            border-radius: 20px;
            margin-bottom: 1.2rem;
          }

          .hero-title {
            font-family: 'Syne', sans-serif;
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #2dd4bf 50%, #0d9488 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.15;
            margin-bottom: 1rem;
          }

          .hero-subtitle {
            font-family: 'DM Sans', sans-serif;
            font-size: 1.05rem;
            color: #94a3b8;
            max-width: 600px;
            margin: 0 auto 1.5rem auto;
            line-height: 1.7;
            font-weight: 300;
          }

          .hero-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            display: block;
          }

          .tag-row {
            display: flex;
            justify-content: center;
            gap: 0.6rem;
            flex-wrap: wrap;
            margin-top: 1.2rem;
          }

          .tag {
            background: #111918;
            border: 1px solid #1f2937;
            color: #64748b;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.75rem;
            padding: 0.25rem 0.8rem;
            border-radius: 20px;
          }
        </style>
        </head>
        <body>
        <div class="hero">
          <span class="hero-icon">🏥</span>
          <div class="badge">⚡ MULTI-AGENT CLINICAL DECISION SUPPORT</div>
          <div class="hero-title">ClinicalCrew</div>
          <div class="hero-subtitle">
            A 4-phase AI pipeline with 11 specialized agents that analyze medical
            reports and generate evidence-based clinical decision support packages —
            structured diagnosis, treatment planning, drug safety checks, and patient summaries.
          </div>
          <div class="tag-row">
            <span class="tag">🤖 CrewAI Framework</span>
            <span class="tag">🧠 LLaMA 3.3 70B</span>
            <span class="tag">🔬 11 Specialized Agents</span>
            <span class="tag">📋 4 Sequential Phases</span>
            <span class="tag">💊 Drug Safety Check</span>
            <span class="tag">📄 SOAP Reports</span>
          </div>
        </div>
        </body>
        </html>
        """,
        height=380,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Disclaimer ─────────────────────────────────────────────
    disclaimer_banner()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Metrics ────────────────────────────────────────────────
    patient_count  = get_patient_count()
    analysis_count = get_analysis_count()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        components.html(
            metric_card("Reports Analyzed", str(patient_count), "📋", "#0d9488"),
            height=120,
        )
    with col2:
        components.html(
            metric_card("Diagnoses Generated", str(analysis_count), "🔬", "#2dd4bf"),
            height=120,
        )
    with col3:
        components.html(
            metric_card("Drug Checks Done", str(analysis_count), "💊", "#a855f7"),
            height=120,
        )
    with col4:
        components.html(
            metric_card("Reports Exported", str(patient_count), "📄", "#22c55e"),
            height=120,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pipeline Steps ─────────────────────────────────────────
    st.markdown(
        """
        <h2 style="font-family:'Syne',sans-serif; font-size:1.5rem;
                   color:#e2f0ef; margin-bottom:1rem;">
            🔄 The 4-Phase Pipeline
        </h2>
        """,
        unsafe_allow_html=True,
    )

    phases = [
        {
            "number": "01",
            "icon": "📥",
            "title": "Report Intake",
            "color": "#0d9488",
            "agents": "3 Agents",
            "desc": "Parse medical report, build patient profile, validate data completeness.",
            "tasks": ["Report Parser", "Context Builder", "Data Validator"],
        },
        {
            "number": "02",
            "icon": "🔬",
            "title": "Diagnosis Analysis",
            "color": "#3b82f6",
            "agents": "3 Agents",
            "desc": "Symptom clustering, differential diagnosis, lab interpretation, risk scoring.",
            "tasks": ["Symptom Analyzer", "Lab Interpreter", "Risk Assessor"],
        },
        {
            "number": "03",
            "icon": "💊",
            "title": "Treatment Planning",
            "color": "#a855f7",
            "agents": "3 Agents",
            "desc": "Evidence-based treatments, drug interaction check, patient-specific dosing.",
            "tasks": ["Treatment Suggester", "Drug Checker", "Dosage Calculator"],
        },
        {
            "number": "04",
            "icon": "📄",
            "title": "Clinical Summary",
            "color": "#22c55e",
            "agents": "3 Agents",
            "desc": "SOAP physician report, patient-friendly summary, structured follow-up plan.",
            "tasks": ["Report Writer", "Patient Explainer", "Follow-up Planner"],
        },
    ]

    cols = st.columns(4)
    for i, (col, phase) in enumerate(zip(cols, phases)):
        with col:
            tasks_html = "".join(
                f'<div style="background:rgba(255,255,255,0.04); border-radius:6px; '
                f'padding:0.3rem 0.6rem; margin:0.25rem 0; font-size:0.75rem; '
                f'color:#94a3b8;">• {t}</div>'
                for t in phase["tasks"]
            )
            components.html(
                f"""
                <!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                <style>
                  * {{ margin:0; padding:0; box-sizing:border-box; }}
                  body {{ background:transparent; }}
                  .card {{
                    background: #111918;
                    border: 1px solid #1f2937;
                    border-top: 3px solid {phase['color']};
                    border-radius: 12px;
                    padding: 1.2rem;
                    height: 100%;
                  }}
                  .phase-num {{
                    font-family: 'Syne', sans-serif;
                    font-size: 2rem;
                    font-weight: 800;
                    color: {phase['color']};
                    opacity: 0.3;
                    line-height: 1;
                  }}
                  .phase-icon {{ font-size: 1.8rem; margin: 0.4rem 0; }}
                  .phase-title {{
                    font-family: 'Syne', sans-serif;
                    font-size: 1rem;
                    font-weight: 700;
                    color: #e2f0ef;
                    margin-bottom: 0.3rem;
                  }}
                  .phase-agents {{
                    display: inline-block;
                    background: {phase['color']}22;
                    color: {phase['color']};
                    border: 1px solid {phase['color']}44;
                    border-radius: 20px;
                    font-size: 0.7rem;
                    padding: 0.15rem 0.6rem;
                    font-family: 'DM Sans', sans-serif;
                    margin-bottom: 0.6rem;
                  }}
                  .phase-desc {{
                    font-family: 'DM Sans', sans-serif;
                    font-size: 0.8rem;
                    color: #64748b;
                    line-height: 1.5;
                    margin-bottom: 0.8rem;
                  }}
                </style>
                </head><body>
                <div class="card">
                  <div class="phase-num">{phase['number']}</div>
                  <div class="phase-icon">{phase['icon']}</div>
                  <div class="phase-title">{phase['title']}</div>
                  <div class="phase-agents">{phase['agents']}</div>
                  <div class="phase-desc">{phase['desc']}</div>
                  {tasks_html}
                </div>
                </body></html>
                """,
                height=280,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How to Use ─────────────────────────────────────────────
    st.markdown(
        """
        <h2 style="font-family:'Syne',sans-serif; font-size:1.5rem;
                   color:#e2f0ef; margin-bottom:0.5rem;">
            🚀 How to Use ClinicalCrew
        </h2>
        """,
        unsafe_allow_html=True,
    )

    steps_html = """
    <div style="display:flex; flex-direction:column; gap:0.6rem; margin-top:0.5rem;">
    """
    how_to = [
        ("1", "📥", "Report Intake",
         "Go to <b>Report Intake</b> in the sidebar. Upload a PDF/DOCX or paste report text. Run the Intake Crew."),
        ("2", "🔬", "Diagnosis Analysis",
         "Go to <b>Diagnosis Analysis</b>. Run the Diagnosis Crew to get differential diagnosis and risk assessment."),
        ("3", "💊", "Treatment Planning",
         "Go to <b>Treatment Planning</b>. Run the Treatment Crew for evidence-based options and drug safety check."),
        ("4", "📄", "Clinical Summary",
         "Go to <b>Clinical Summary</b>. Generate the full physician report and patient summary. Download both."),
    ]
    for num, icon, title, desc in how_to:
        steps_html += f"""
        <div style="background:#111918; border:1px solid #1f2937; border-radius:10px;
                    padding:0.9rem 1.2rem; display:flex; align-items:flex-start; gap:1rem;">
          <div style="background:#0d948822; border:1px solid #0d948844; border-radius:8px;
                      width:32px; height:32px; display:flex; align-items:center;
                      justify-content:center; font-family:'Syne',sans-serif;
                      font-weight:800; color:#0d9488; font-size:0.9rem; flex-shrink:0;">{num}</div>
          <div>
            <div style="font-family:'Syne',sans-serif; font-weight:700;
                        color:#e2f0ef; font-size:0.9rem;">{icon} {title}</div>
            <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                        font-size:0.82rem; margin-top:0.2rem;">{desc}</div>
          </div>
        </div>
        """
    steps_html += "</div>"

    components.html(
        f"""
        <!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>* {{ margin:0; padding:0; box-sizing:border-box; }} body {{ background:transparent; }}</style>
        </head><body>{steps_html}</body></html>
        """,
        height=280,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Session State Init ──────────────────────────────────────
    defaults = {
        "report_text":        None,
        "patient_name":       "",
        "patient_age":        0,
        "patient_gender":     "",
        "parsed_report":      None,
        "patient_context":    None,
        "validation":         None,
        "diagnosis_result":   None,
        "treatment_result":   None,
        "summary_result":     None,
        "patient_id":         None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ── Status Bar ─────────────────────────────────────────────
    st.markdown(
        """
        <h2 style="font-family:'Syne',sans-serif; font-size:1.5rem;
                   color:#e2f0ef; margin-bottom:0.5rem;">
            📊 Current Session Status
        </h2>
        """,
        unsafe_allow_html=True,
    )

    phase_status = [
        ("Phase 1 — Report Intake",
         st.session_state.parsed_report is not None),
        ("Phase 2 — Diagnosis Analysis",
         st.session_state.diagnosis_result is not None),
        ("Phase 3 — Treatment Planning",
         st.session_state.treatment_result is not None),
        ("Phase 4 — Clinical Summary",
         st.session_state.summary_result is not None),
    ]

    status_cols = st.columns(4)
    for col, (label, done) in zip(status_cols, phase_status):
        with col:
            color  = "#22c55e" if done else "#374151"
            icon   = "✅" if done else "⏳"
            status = "Complete" if done else "Pending"
            components.html(
                f"""
                <!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                <style>* {{ margin:0; padding:0; box-sizing:border-box; }} body {{ background:transparent; }}</style>
                </head><body>
                <div style="background:#111918; border:1px solid #1f2937;
                            border-left:4px solid {color}; border-radius:10px;
                            padding:0.9rem 1rem;">
                  <div style="font-size:1.4rem;">{icon}</div>
                  <div style="font-family:'Syne',sans-serif; font-size:0.82rem;
                              font-weight:700; color:#e2f0ef; margin:0.3rem 0;">{label}</div>
                  <div style="font-family:'DM Sans',sans-serif; font-size:0.75rem;
                              color:{color};">{status}</div>
                </div>
                </body></html>
                """,
                height=110,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation CTA ─────────────────────────────────────────
    if st.session_state.report_text is None:
        st.info(
            "👈 **Get started!** Go to **Report Intake** in the sidebar "
            "to upload or paste a medical report.",
            icon="🏥",
        )
    else:
        st.success(
            f"✅ Report loaded for **{st.session_state.patient_name or 'Patient'}**. "
            "Continue to the next incomplete phase in the sidebar.",
            icon="🎯",
        )


if __name__ == "__main__":
    main()
