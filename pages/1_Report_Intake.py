import streamlit as st

st.set_page_config(
    page_title="Report Intake — ClinicalCrew",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded",
)

import json
import streamlit.components.v1 as components
from utils.styles import inject_styles, page_header, disclaimer_banner, badge, info_card
from utils.execution_log import render_log
from utils.report_parser import parse_uploaded_file


# ── Session State Defaults ─────────────────────────────────────
def _init_session():
    defaults = {
        "report_text":      None,
        "patient_name":     "",
        "patient_age":      0,
        "patient_gender":   "",
        "parsed_report":    None,
        "patient_context":  None,
        "validation":       None,
        "diagnosis_result": None,
        "treatment_result": None,
        "summary_result":   None,
        "patient_id":       None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Execution Log Builder ──────────────────────────────────────
def _build_log_lines(phase: str) -> list[dict]:
    base = [
        {"tag": "SYS",   "msg": "ClinicalCrew v1.0 — Phase 1: Report Intake"},
        {"tag": "SYS",   "msg": "Initializing agent runtime environment..."},
        {"tag": "LLM",   "msg": "Loading LLM — groq/llama-3.3-70b-versatile"},
        {"tag": "SYS",   "msg": "All 3 agents instantiated successfully"},
    ]
    agent_lines = {
        "parsing": [
            {"tag": "AGENT", "msg": "ReportParserAgent → Starting report extraction"},
            {"tag": "TASK",  "msg": "Task: Parse raw medical report text"},
            {"tag": "RUN",   "msg": "Extracting patient demographics..."},
            {"tag": "RUN",   "msg": "Extracting vital signs and physical exam..."},
            {"tag": "RUN",   "msg": "Extracting laboratory results with flags..."},
            {"tag": "RUN",   "msg": "Extracting medications and allergies..."},
            {"tag": "RUN",   "msg": "Extracting investigations (ECG, imaging, echo)..."},
            {"tag": "DONE",  "msg": "ReportParserAgent → Report parsed successfully ✓"},
        ],
        "context": [
            {"tag": "AGENT", "msg": "PatientContextAgent → Building clinical profile"},
            {"tag": "TASK",  "msg": "Task: Build comprehensive patient context"},
            {"tag": "RUN",   "msg": "Identifying comorbidities and severity..."},
            {"tag": "RUN",   "msg": "Classifying medications by drug class..."},
            {"tag": "RUN",   "msg": "Building allergy profile and cross-reactivity risks..."},
            {"tag": "RUN",   "msg": "Assessing clinical complexity..."},
            {"tag": "DONE",  "msg": "PatientContextAgent → Patient profile complete ✓"},
        ],
        "validation": [
            {"tag": "AGENT", "msg": "DataValidatorAgent → Validating data completeness"},
            {"tag": "TASK",  "msg": "Task: Validate data quality and completeness"},
            {"tag": "RUN",   "msg": "Scoring completeness across all sections..."},
            {"tag": "RUN",   "msg": "Checking for contradictions and data gaps..."},
            {"tag": "RUN",   "msg": "Setting safe_to_proceed flag..."},
            {"tag": "DONE",  "msg": "DataValidatorAgent → Validation complete ✓"},
        ],
        "done": [
            {"tag": "SYS",  "msg": "─" * 45},
            {"tag": "DONE", "msg": "Phase 1 Complete — All 3 agents finished"},
            {"tag": "SYS",  "msg": "Results saved to session state"},
            {"tag": "SYS",  "msg": "Proceed to Diagnosis Analysis →"},
        ],
    }
    lines = base[:]
    for key in ["parsing", "context", "validation", "done"]:
        lines.extend(agent_lines[key])
        if key == phase:
            break
    return lines


# ── Render Patient Profile Tab ─────────────────────────────────
def _render_patient_profile(context: dict):
    st.markdown(
        """
        <h3 style="font-family:'Syne',sans-serif; color:#e2f0ef;
                   font-size:1.1rem; margin-bottom:1rem;">
            👤 Patient Clinical Profile
        </h3>
        """,
        unsafe_allow_html=True,
    )

    summary = context.get("patient_summary", "No summary available.")
    components.html(
        f"""
        <!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>* {{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
        </head><body>
        <div style="background:#111918; border:1px solid #1f2937;
                    border-left:4px solid #0d9488; border-radius:10px;
                    padding:1.2rem; margin-bottom:1rem;">
          <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                      font-size:0.9rem; line-height:1.7;">{summary}</div>
        </div>
        </body></html>
        """,
        height=120,
    )

    # Comorbidities
    st.markdown(
        "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>🏥 Comorbidities</h4>",
        unsafe_allow_html=True,
    )
    comorbidities = context.get("comorbidities", [])
    if comorbidities:
        cards_html = ""
        for c in comorbidities:
            severity = c.get("severity", "unknown").lower()
            sev_color = (
                "#22c55e" if severity == "controlled"
                else "#ef4444" if severity == "uncontrolled"
                else "#fbbf24"
            )
            relevant = c.get("relevant_to_presentation", False)
            cards_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid {sev_color}; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.4rem 0;
                        display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-family:'DM Sans',sans-serif; font-weight:500;
                            color:#e2f0ef; font-size:0.9rem;">
                  {c.get('condition','Unknown')}
                  {'<span style="color:#fbbf24; font-size:0.75rem; margin-left:0.5rem;">⚠ Relevant</span>'
                   if relevant else ''}
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                            font-size:0.78rem; margin-top:0.2rem;">
                  {c.get('notes','')}</div>
              </div>
              <span style="background:{sev_color}22; color:{sev_color};
                           border:1px solid {sev_color}44; border-radius:20px;
                           padding:0.2rem 0.7rem; font-size:0.75rem;
                           font-family:'DM Sans',sans-serif; white-space:nowrap;">
                {severity.title()}
              </span>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{cards_html}</body></html>""",
            height=max(120, len(comorbidities) * 90),
        )
    else:
        st.info("No comorbidities extracted.")

    # Risk Factors
    st.markdown(
        "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>⚠️ Risk Factors</h4>",
        unsafe_allow_html=True,
    )
    risk_factors = context.get("risk_factors", [])
    if risk_factors:
        tags_html = "".join(
            f'<span style="background:#fbbf2422; color:#fbbf24; '
            f'border:1px solid #fbbf2444; border-radius:20px; '
            f'padding:0.3rem 0.8rem; font-size:0.8rem; '
            f'font-family:DM Sans,sans-serif; margin:0.2rem;">{r}</span>'
            for r in risk_factors
        )
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}
            .wrap{{display:flex;flex-wrap:wrap;gap:0.3rem;padding:0.3rem 0;}}</style>
            </head><body><div class="wrap">{tags_html}</div></body></html>""",
            height=80,
        )
    else:
        st.info("No risk factors identified.")

    # Clinical Complexity
    complexity = context.get("clinical_complexity", "unknown")
    comp_color = (
        "#22c55e" if complexity == "low"
        else "#fbbf24" if complexity == "moderate"
        else "#ef4444"
    )
    st.markdown(
        f"""
        <div style="background:#111918; border:1px solid #1f2937;
                    border-radius:10px; padding:1rem 1.2rem; margin-top:1rem;
                    display:flex; align-items:center; gap:1rem;">
          <div style="font-family:'Syne',sans-serif; color:#94a3b8;
                      font-size:0.85rem;">Clinical Complexity:</div>
          <span style="background:{comp_color}22; color:{comp_color};
                       border:1px solid {comp_color}44; border-radius:20px;
                       padding:0.3rem 1rem; font-size:0.9rem;
                       font-family:'DM Sans',sans-serif; font-weight:500;">
            {complexity.upper()}
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Render Extracted Data Tab ──────────────────────────────────
def _render_extracted_data(parsed: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>🔬 Extracted Clinical Data</h3>",
        unsafe_allow_html=True,
    )

    # Vital Signs
    vitals = parsed.get("vital_signs", {})
    if vitals:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin-bottom:0.5rem;'>💓 Vital Signs</h4>",
            unsafe_allow_html=True,
        )
        vital_items = [
            ("BP",       vitals.get("bp", "N/A"),          "mmHg",     "🩸"),
            ("HR",       vitals.get("heart_rate", "N/A"),  "bpm",      "❤️"),
            ("SpO2",     vitals.get("spo2", "N/A"),        "%",        "🫁"),
            ("Temp",     vitals.get("temperature", "N/A"), "°C",       "🌡️"),
            ("RR",       vitals.get("rr", "N/A"),          "/min",     "💨"),
            ("BMI",      vitals.get("bmi", "N/A"),         "kg/m²",    "⚖️"),
        ]
        vital_cards = ""
        for label, value, unit, icon in vital_items:
            vital_cards += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-radius:10px; padding:0.8rem; text-align:center;">
              <div style="font-size:1.3rem;">{icon}</div>
              <div style="font-family:'Syne',sans-serif; font-size:1rem;
                          font-weight:700; color:#2dd4bf;">{value}</div>
              <div style="font-family:'DM Sans',sans-serif; font-size:0.7rem;
                          color:#64748b;">{label} ({unit})</div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}
            .grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:0.5rem;}}</style>
            </head><body><div class="grid">{vital_cards}</div></body></html>""",
            height=120,
        )

    # Lab Results Table
    labs = parsed.get("lab_results", [])
    if labs:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>🧪 Laboratory Results</h4>",
            unsafe_allow_html=True,
        )
        import pandas as pd
        df = pd.DataFrame(labs)
        if not df.empty:
            flag_colors = {
                "H":        "🔴 H",
                "L":        "🔵 L",
                "N":        "🟢 N",
                "C":        "🚨 C",
                "CRITICAL": "🚨 CRITICAL",
            }
            if "flag" in df.columns:
                df["flag"] = df["flag"].apply(
                    lambda x: flag_colors.get(str(x).upper(), str(x))
                )
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

    # Investigations
    investigations = parsed.get("investigations", [])
    if investigations:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>📷 Investigations</h4>",
            unsafe_allow_html=True,
        )
        for inv in investigations:
            inv_type    = inv.get("type", "Investigation")
            inv_finding = inv.get("findings", "No findings recorded.")
            components.html(
                f"""<!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
                <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
                </head><body>
                <div style="background:#111918; border:1px solid #1f2937;
                            border-left:4px solid #3b82f6; border-radius:10px;
                            padding:1rem; margin:0.4rem 0;">
                  <div style="font-family:'Syne',sans-serif; font-weight:700;
                              color:#e2f0ef; font-size:0.9rem; margin-bottom:0.3rem;">
                    📋 {inv_type}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.85rem; line-height:1.6;">
                    {inv_finding}
                  </div>
                </div>
                </body></html>""",
                height=110,
            )


# ── Render Validation Tab ──────────────────────────────────────
def _render_validation(validation: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>✅ Data Validation Report</h3>",
        unsafe_allow_html=True,
    )

    score         = validation.get("completeness_score", 0)
    safe          = validation.get("safe_to_proceed", False)
    missing       = validation.get("missing_critical_data", [])
    contradictions = validation.get("data_contradictions", [])
    caveats       = validation.get("proceed_caveats", [])
    notes         = validation.get("validator_notes", "")

    score_color = (
        "#22c55e" if score >= 70
        else "#fbbf24" if score >= 40
        else "#ef4444"
    )
    safe_color  = "#22c55e" if safe else "#ef4444"
    safe_text   = "✅ Safe to Proceed" if safe else "❌ Not Safe to Proceed"

    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
        </head><body>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
          <div style="background:#111918; border:1px solid #1f2937;
                      border-top:3px solid {score_color}; border-radius:12px;
                      padding:1.5rem; text-align:center;">
            <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                        font-size:0.8rem; margin-bottom:0.5rem;">
              COMPLETENESS SCORE
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:3rem;
                        font-weight:800; color:{score_color};">{score}</div>
            <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                        font-size:0.75rem;">out of 100</div>
          </div>
          <div style="background:#111918; border:1px solid #1f2937;
                      border-top:3px solid {safe_color}; border-radius:12px;
                      padding:1.5rem; text-align:center;">
            <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                        font-size:0.8rem; margin-bottom:0.5rem;">
              PROCEED STATUS
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:1.3rem;
                        font-weight:700; color:{safe_color};">{safe_text}</div>
            <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                        font-size:0.75rem; margin-top:0.3rem;">{notes[:80] if notes else ''}</div>
          </div>
        </div>
        </body></html>""",
        height=160,
    )

    if missing:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#ef4444; "
            "font-size:0.9rem; margin:1rem 0 0.4rem 0;'>⚠️ Missing Critical Data</h4>",
            unsafe_allow_html=True,
        )
        for m in missing:
            st.warning(m, icon="⚠️")

    if contradictions:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#fbbf24; "
            "font-size:0.9rem; margin:1rem 0 0.4rem 0;'>🔄 Data Contradictions</h4>",
            unsafe_allow_html=True,
        )
        for c in contradictions:
            st.warning(c, icon="🔄")

    if caveats:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#94a3b8; "
            "font-size:0.9rem; margin:1rem 0 0.4rem 0;'>📌 Proceed With Caveats</h4>",
            unsafe_allow_html=True,
        )
        for cv in caveats:
            st.info(cv, icon="📌")


# ── Main ───────────────────────────────────────────────────────
def main():
    _init_session()
    inject_styles()
    page_header("📥", "Report Intake", "Upload or paste a medical report to begin Phase 1 analysis")
    disclaimer_banner()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Report Input Section ────────────────────────────────────
    tab_upload, tab_paste = st.tabs(["📎 Upload PDF / DOCX", "📝 Paste Report Text"])

    with tab_upload:
        st.markdown(
            "<p style='color:#94a3b8; font-size:0.9rem;'>"
            "Upload a medical report in PDF or DOCX format.</p>",
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Choose file",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
        )
        if uploaded:
            with st.spinner("Extracting text from file..."):
                text = parse_uploaded_file(uploaded)
            if text:
                st.session_state.report_text = text
                st.success(
                    f"✅ File parsed successfully — "
                    f"{len(text):,} characters extracted.",
                    icon="📄",
                )
                with st.expander("Preview extracted text"):
                    st.text(text[:1500] + ("..." if len(text) > 1500 else ""))
            else:
                st.error("Could not extract text from file. Try pasting the text manually.")

    with tab_paste:
        st.markdown(
            "<p style='color:#94a3b8; font-size:0.9rem;'>"
            "Paste the full medical report text below.</p>",
            unsafe_allow_html=True,
        )
        pasted = st.text_area(
            "Medical Report Text",
            height=300,
            placeholder="Paste the full medical report here...",
            label_visibility="collapsed",
        )
        if st.button("📋 Use This Report Text", use_container_width=False):
            if pasted.strip():
                st.session_state.report_text = pasted.strip()
                st.success(
                    f"✅ Report text loaded — "
                    f"{len(pasted):,} characters.",
                    icon="✅",
                )
            else:
                st.error("Please paste some report text first.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Patient Info ────────────────────────────────────────────
    if st.session_state.report_text:
        st.markdown(
            """
            <h3 style="font-family:'Syne',sans-serif; color:#e2f0ef;
                       font-size:1.1rem; margin-bottom:0.5rem;">
                👤 Patient Information
            </h3>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.patient_name = st.text_input(
                "Patient Name",
                value=st.session_state.patient_name,
                placeholder="e.g. Rahim Uddin",
            )
        with c2:
            st.session_state.patient_age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=int(st.session_state.patient_age or 0),
            )
        with c3:
            st.session_state.patient_gender = st.selectbox(
                "Gender",
                ["", "Male", "Female", "Other"],
                index=["", "Male", "Female", "Other"].index(
                    st.session_state.patient_gender
                ) if st.session_state.patient_gender in ["", "Male", "Female", "Other"]
                else 0,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Run Intake Crew ─────────────────────────────────────
        col_btn, col_status = st.columns([2, 3])
        with col_btn:
            run_btn = st.button(
                "🚀 Run Intake Crew (Phase 1)",
                use_container_width=True,
                type="primary",
            )

        if run_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
                "font-size:1rem;'>⚡ Agent Execution Log</h3>",
                unsafe_allow_html=True,
            )

            log_placeholder = st.empty()

            # Show progressive log
            import time
            phases_seq = ["parsing", "context", "validation", "done"]
            for phase in phases_seq[:-1]:
                render_log(
                    _build_log_lines(phase),
                    running=True,
                    height=340,
                )
                time.sleep(0.5)

            with st.spinner("🤖 Agents working — this may take 60-120 seconds..."):
                try:
                    from crews.crews import run_intake_crew
                    result = run_intake_crew(st.session_state.report_text)

                    st.session_state.parsed_report   = result["parsed_report"]
                    st.session_state.patient_context  = result["patient_context"]
                    st.session_state.validation       = result["validation"]
                    st.session_state["_parsed_raw"]   = result.get("_parsed_raw", "{}")
                    st.session_state["_context_raw"]  = result.get("_context_raw", "{}")

                    # Save to Supabase
                    try:
                        from utils.database import save_patient
                        pid = save_patient(
                            name=st.session_state.patient_name,
                            age=int(st.session_state.patient_age or 0),
                            gender=st.session_state.patient_gender,
                            report_text=st.session_state.report_text,
                            patient_context=result["patient_context"],
                        )
                        st.session_state.patient_id = pid
                    except Exception:
                        pass

                    render_log(
                        _build_log_lines("done"),
                        running=False,
                        height=340,
                    )
                    st.success(
                        "✅ Phase 1 Complete! Scroll down to view results.",
                        icon="🎉",
                    )

                except Exception as e:
                    render_log(
                        _build_log_lines("parsing") + [
                            {"tag": "ERROR", "msg": f"Crew execution failed: {str(e)[:120]}"}
                        ],
                        running=False,
                        height=340,
                    )
                    st.error(f"❌ Error: {e}")

    # ── Results ─────────────────────────────────────────────────
    if st.session_state.parsed_report:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:1.3rem; margin-bottom:0.5rem;'>📊 Phase 1 Results</h2>",
            unsafe_allow_html=True,
        )

        r_tab1, r_tab2, r_tab3 = st.tabs([
            "👤 Patient Profile",
            "🔬 Extracted Data",
            "✅ Validation",
        ])

        with r_tab1:
            if st.session_state.patient_context:
                _render_patient_profile(st.session_state.patient_context)
            else:
                st.info("Patient context not yet available.")

        with r_tab2:
            if st.session_state.parsed_report:
                _render_extracted_data(st.session_state.parsed_report)
            else:
                st.info("Parsed report not yet available.")

        with r_tab3:
            if st.session_state.validation:
                _render_validation(st.session_state.validation)
            else:
                st.info("Validation not yet available.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info(
            "✅ Phase 1 complete! Go to **Diagnosis Analysis** in the sidebar "
            "to continue to Phase 2.",
            icon="➡️",
        )


if __name__ == "__main__":
    main()