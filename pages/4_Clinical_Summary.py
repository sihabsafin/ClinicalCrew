import streamlit as st

st.set_page_config(
    page_title="Clinical Summary — ClinicalCrew",
    page_icon="📄",
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
        "_treatment_raw":   "{}",
        "_drug_raw":        "{}",
        "_dosage_raw":      "{}",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Execution Log Lines ────────────────────────────────────────
def _build_log_lines(phase: str) -> list[dict]:
    base = [
        {"tag": "SYS",   "msg": "ClinicalCrew v1.0 — Phase 4: Clinical Summary"},
        {"tag": "SYS",   "msg": "Loading all Phase 1-3 results from session state..."},
        {"tag": "LLM",   "msg": "Loading LLM — groq/llama-3.3-70b-versatile"},
        {"tag": "SYS",   "msg": "All 3 summary agents instantiated successfully"},
    ]
    agent_lines = {
        "report": [
            {"tag": "AGENT", "msg": "ReportWriterAgent → Starting physician report"},
            {"tag": "TASK",  "msg": "Task: Write SOAP-format clinical summary"},
            {"tag": "RUN",   "msg": "Compiling patient summary and key findings..."},
            {"tag": "RUN",   "msg": "Writing working diagnosis and differential..."},
            {"tag": "RUN",   "msg": "Documenting proposed management plan..."},
            {"tag": "RUN",   "msg": "Adding drug safety notes and physician decisions..."},
            {"tag": "RUN",   "msg": "Finalizing SOAP report with AI disclaimer..."},
            {"tag": "DONE",  "msg": "ReportWriterAgent → Physician report complete ✓"},
        ],
        "patient": [
            {"tag": "AGENT", "msg": "PatientExplainerAgent → Starting patient summary"},
            {"tag": "TASK",  "msg": "Task: Write plain-language patient summary"},
            {"tag": "RUN",   "msg": "Translating clinical findings to plain language..."},
            {"tag": "RUN",   "msg": "Writing what findings mean for the patient..."},
            {"tag": "RUN",   "msg": "Writing medication explanations..."},
            {"tag": "RUN",   "msg": "Listing warning signs to watch for..."},
            {"tag": "DONE",  "msg": "PatientExplainerAgent → Patient summary complete ✓"},
        ],
        "followup": [
            {"tag": "AGENT", "msg": "FollowUpPlannerAgent → Building follow-up plan"},
            {"tag": "TASK",  "msg": "Task: Create structured follow-up plan"},
            {"tag": "RUN",   "msg": "Scheduling follow-up appointments..."},
            {"tag": "RUN",   "msg": "Planning repeat investigations with rationale..."},
            {"tag": "RUN",   "msg": "Creating monitoring schedule..."},
            {"tag": "RUN",   "msg": "Identifying specialist referrals with urgency..."},
            {"tag": "RUN",   "msg": "Listing lifestyle recommendations..."},
            {"tag": "RUN",   "msg": "Defining emergency warning signs..."},
            {"tag": "DONE",  "msg": "FollowUpPlannerAgent → Follow-up plan complete ✓"},
        ],
        "done": [
            {"tag": "SYS",  "msg": "─" * 45},
            {"tag": "DONE", "msg": "Phase 4 Complete — All 3 agents finished"},
            {"tag": "DONE", "msg": "Full clinical package generated successfully"},
            {"tag": "SYS",  "msg": "Download physician report and patient summary below"},
        ],
    }
    lines = base[:]
    for key in ["report", "patient", "followup", "done"]:
        lines.extend(agent_lines[key])
        if key == phase:
            break
    return lines


# ── Tab 1: Physician Report ────────────────────────────────────
def _render_physician_report(report_text: str, patient_name: str):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>🩺 Physician Clinical Report (SOAP)</h3>",
        unsafe_allow_html=True,
    )

    if not report_text:
        st.info("No physician report generated yet.")
        return

    # Render report in styled box
    # Escape HTML special chars for safe rendering
    safe_report = (
        report_text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
        .replace("## ", "<br><span style='font-family:Syne,sans-serif;"
                  "font-weight:700; color:#2dd4bf; font-size:1rem;'>")
        .replace("### ", "<br><span style='font-family:Syne,sans-serif;"
                  "font-weight:600; color:#94a3b8; font-size:0.9rem;'>")
    )

    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
          * {{margin:0;padding:0;box-sizing:border-box;}}
          body {{background:transparent;}}
          .report-box {{
            background:#111918;
            border:1px solid #1f2937;
            border-top:3px solid #0d9488;
            border-radius:12px;
            padding:1.5rem;
            font-family:'DM Sans',sans-serif;
            color:#94a3b8;
            font-size:0.88rem;
            line-height:1.8;
            max-height:600px;
            overflow-y:auto;
          }}
          .report-box::-webkit-scrollbar {{width:4px;}}
          .report-box::-webkit-scrollbar-track {{background:#111918;}}
          .report-box::-webkit-scrollbar-thumb {{background:#0d9488; border-radius:2px;}}
        </style>
        </head><body>
        <div class="report-box">{safe_report}</div>
        </body></html>""",
        height=640,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Download Button
    fname = f"ClinicalCrew_Physician_Report_{patient_name.replace(' ','_')}.txt"
    st.download_button(
        label="📥 Download Physician Report (.txt)",
        data=report_text,
        file_name=fname,
        mime="text/plain",
        use_container_width=False,
    )


# ── Tab 2: Patient Summary ─────────────────────────────────────
def _render_patient_summary(summary_text: str, patient_name: str):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>👤 Patient-Friendly Summary</h3>",
        unsafe_allow_html=True,
    )

    if not summary_text:
        st.info("No patient summary generated yet.")
        return

    # Format the text
    safe_summary = (
        summary_text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
        .replace("## ", "<br><span style='font-family:Syne,sans-serif;"
                  "font-weight:700; color:#2dd4bf; font-size:1rem;'>")
    )

    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
          * {{margin:0;padding:0;box-sizing:border-box;}}
          body {{background:transparent;}}
          .summary-box {{
            background:#0d1f1e;
            border:2px solid #0d9488;
            border-radius:12px;
            padding:1.5rem;
            font-family:'DM Sans',sans-serif;
            color:#e2f0ef;
            font-size:0.92rem;
            line-height:1.9;
            max-height:600px;
            overflow-y:auto;
          }}
          .summary-box::-webkit-scrollbar {{width:4px;}}
          .summary-box::-webkit-scrollbar-track {{background:#0d1f1e;}}
          .summary-box::-webkit-scrollbar-thumb {{background:#0d9488; border-radius:2px;}}
        </style>
        </head><body>
        <div class="summary-box">{safe_summary}</div>
        </body></html>""",
        height=640,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    fname = f"ClinicalCrew_Patient_Summary_{patient_name.replace(' ','_')}.txt"
    st.download_button(
        label="📥 Download Patient Summary (.txt)",
        data=summary_text,
        file_name=fname,
        mime="text/plain",
        use_container_width=False,
    )


# ── Tab 3: Follow-Up Plan ──────────────────────────────────────
def _render_followup_plan(data: dict):
    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1.1rem; margin-bottom:1rem;'>📅 Follow-Up Plan</h3>",
        unsafe_allow_html=True,
    )

    if not data:
        st.info("No follow-up plan generated yet.")
        return

    # ── Warning Signs Emergency ─────────────────────────────────
    emergency = data.get("warning_signs_emergency", [])
    if emergency:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#ef4444; "
            "font-size:0.95rem; margin-bottom:0.5rem;'>🚨 Go to Emergency IMMEDIATELY if:</h4>",
            unsafe_allow_html=True,
        )
        em_html = ""
        for sign in emergency:
            em_html += f"""
            <div style="background:#1a0808; border:1px solid #ef444433;
                        border-left:4px solid #ef4444; border-radius:8px;
                        padding:0.7rem 1rem; margin:0.3rem 0;
                        font-family:'DM Sans',sans-serif; color:#fca5a5;
                        font-size:0.88rem;">
              🚨 {sign}
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{em_html}</body></html>""",
            height=max(100, len(emergency) * 65),
        )

    # ── Warning Signs Urgent ────────────────────────────────────
    urgent_signs = data.get("warning_signs_urgent", [])
    if urgent_signs:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#fbbf24; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>"
            "⚠️ Contact Your Doctor Same Day if:</h4>",
            unsafe_allow_html=True,
        )
        urg_html = ""
        for sign in urgent_signs:
            urg_html += f"""
            <div style="background:#1a1208; border:1px solid #fbbf2433;
                        border-left:4px solid #fbbf24; border-radius:8px;
                        padding:0.7rem 1rem; margin:0.3rem 0;
                        font-family:'DM Sans',sans-serif; color:#fde68a;
                        font-size:0.88rem;">
              ⚠️ {sign}
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{urg_html}</body></html>""",
            height=max(100, len(urgent_signs) * 65),
        )

    # ── Follow-Up Appointments ──────────────────────────────────
    appointments = data.get("followup_appointments", [])
    if appointments:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>📅 Follow-Up Appointments</h4>",
            unsafe_allow_html=True,
        )
        appt_html = ""
        for appt in appointments:
            urgency   = appt.get("urgency", "routine").lower()
            urg_color = "#ef4444" if urgency == "urgent" else "#0d9488"
            appt_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid {urg_color}; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.4rem 0;">
              <div style="display:flex; justify-content:space-between;
                          align-items:flex-start;">
                <div>
                  <div style="font-family:'Syne',sans-serif; font-weight:700;
                              color:#e2f0ef; font-size:0.9rem;">
                    🏥 {appt.get('specialty','')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; margin-top:0.2rem;">
                    {appt.get('purpose','')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                              font-size:0.78rem; margin-top:0.2rem; font-style:italic;">
                    Prep: {appt.get('preparation_required','None')}
                  </div>
                </div>
                <div style="text-align:right; flex-shrink:0; margin-left:0.5rem;">
                  <div style="font-family:'DM Sans',sans-serif; color:#2dd4bf;
                              font-size:0.85rem; font-weight:500;">
                    {appt.get('timeframe','')}
                  </div>
                  <span style="background:{urg_color}22; color:{urg_color};
                               border:1px solid {urg_color}44; border-radius:20px;
                               padding:0.15rem 0.6rem; font-size:0.7rem;
                               font-family:'DM Sans',sans-serif;">
                    {urgency.title()}
                  </span>
                </div>
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{appt_html}</body></html>""",
            height=max(150, len(appointments) * 130),
        )

    # ── Repeat Investigations ───────────────────────────────────
    investigations = data.get("repeat_investigations", [])
    if investigations:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>🧪 Repeat Investigations</h4>",
            unsafe_allow_html=True,
        )
        inv_html = ""
        for inv in investigations:
            inv_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid #3b82f6; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.4rem 0;
                        display:flex; justify-content:space-between; align-items:center;">
              <div style="flex:1;">
                <div style="font-family:'Syne',sans-serif; font-weight:700;
                            color:#e2f0ef; font-size:0.88rem;">
                  🧪 {inv.get('test_name','')}
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                            font-size:0.8rem; margin-top:0.2rem;">
                  {inv.get('rationale','')}
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                            font-size:0.75rem; margin-top:0.1rem; font-style:italic;">
                  Target: {inv.get('target_result','N/A')}
                </div>
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#2dd4bf;
                          font-size:0.82rem; font-weight:500; flex-shrink:0;
                          margin-left:0.8rem; text-align:right;">
                {inv.get('timeframe','')}
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{inv_html}</body></html>""",
            height=max(150, len(investigations) * 120),
        )

    # ── Monitoring Schedule ─────────────────────────────────────
    monitoring = data.get("monitoring_schedule", [])
    if monitoring:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>📊 Monitoring Schedule</h4>",
            unsafe_allow_html=True,
        )
        mon_html = ""
        for mon in monitoring:
            mon_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-radius:8px; padding:0.8rem 1rem; margin:0.3rem 0;
                        display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:0.5rem;
                        align-items:center;">
              <div style="font-family:'DM Sans',sans-serif; color:#e2f0ef;
                          font-size:0.87rem; font-weight:500;">
                📊 {mon.get('parameter','')}
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#2dd4bf;
                          font-size:0.8rem; text-align:center;">
                {mon.get('frequency','')}
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                          font-size:0.78rem; text-align:center;">
                {mon.get('method','')}
              </div>
              <div style="font-family:'DM Sans',sans-serif; color:#22c55e;
                          font-size:0.78rem; text-align:center;">
                {mon.get('target_range','')}
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{mon_html}</body></html>""",
            height=max(120, len(monitoring) * 75),
        )

    # ── Specialist Referrals ────────────────────────────────────
    referrals = data.get("specialist_referrals", [])
    if referrals:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>👨‍⚕️ Specialist Referrals</h4>",
            unsafe_allow_html=True,
        )
        ref_html = ""
        for ref in referrals:
            urgency   = ref.get("urgency", "routine").lower()
            urg_color = (
                "#ef4444" if "urgent" in urgency and "days" in urgency
                else "#fbbf24" if "weeks" in urgency
                else "#0d9488"
            )
            ref_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid {urg_color}; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.4rem 0;
                        display:flex; justify-content:space-between; align-items:flex-start;">
              <div style="flex:1;">
                <div style="font-family:'Syne',sans-serif; font-weight:700;
                            color:#e2f0ef; font-size:0.9rem;">
                  👨‍⚕️ {ref.get('specialty','')}
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                            font-size:0.82rem; margin-top:0.2rem;">
                  {ref.get('reason','')}
                </div>
                <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                            font-size:0.75rem; margin-top:0.2rem; font-style:italic;">
                  Notes: {ref.get('referral_notes','')[:150]}
                </div>
              </div>
              <span style="background:{urg_color}22; color:{urg_color};
                           border:1px solid {urg_color}44; border-radius:20px;
                           padding:0.2rem 0.7rem; font-size:0.72rem;
                           font-family:'DM Sans',sans-serif; white-space:nowrap;
                           flex-shrink:0; margin-left:0.5rem;">
                {urgency}
              </span>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{ref_html}</body></html>""",
            height=max(120, len(referrals) * 130),
        )

    # ── Lifestyle Recommendations ───────────────────────────────
    lifestyle = data.get("lifestyle_recommendations", [])
    if lifestyle:
        st.markdown(
            "<h4 style='font-family:Syne,sans-serif; color:#22c55e; "
            "font-size:0.95rem; margin:1rem 0 0.5rem 0;'>🌿 Lifestyle Recommendations</h4>",
            unsafe_allow_html=True,
        )
        cat_icons = {
            "diet":     "🥗",
            "exercise": "🏃",
            "smoking":  "🚭",
            "alcohol":  "🍷",
            "stress":   "🧘",
            "sleep":    "😴",
        }
        life_html = ""
        for lf in lifestyle:
            cat  = lf.get("category", "").lower()
            icon = cat_icons.get(cat, "🌿")
            life_html += f"""
            <div style="background:#111918; border:1px solid #1f2937;
                        border-left:4px solid #22c55e; border-radius:10px;
                        padding:0.9rem 1rem; margin:0.3rem 0;">
              <div style="display:flex; justify-content:space-between;
                          align-items:flex-start;">
                <div style="flex:1;">
                  <div style="font-family:'Syne',sans-serif; font-weight:700;
                              color:#e2f0ef; font-size:0.88rem;">
                    {icon} {lf.get('category','').title()}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#94a3b8;
                              font-size:0.82rem; margin-top:0.2rem; line-height:1.5;">
                    {lf.get('recommendation','')}
                  </div>
                  <div style="font-family:'DM Sans',sans-serif; color:#64748b;
                              font-size:0.75rem; margin-top:0.2rem; font-style:italic;">
                    {lf.get('evidence_base','')[:120]}
                  </div>
                </div>
                <span style="background:#22c55e22; color:#22c55e;
                             border:1px solid #22c55e44; border-radius:20px;
                             padding:0.15rem 0.6rem; font-size:0.7rem;
                             font-family:'DM Sans',sans-serif; white-space:nowrap;
                             flex-shrink:0; margin-left:0.5rem;">
                  {lf.get('timeline','')}
                </span>
              </div>
            </div>
            """
        components.html(
            f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>{life_html}</body></html>""",
            height=max(120, len(lifestyle) * 115),
        )


# ── Completion Banner ──────────────────────────────────────────
def _render_completion_banner(patient_name: str):
    components.html(
        f"""<!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
          * {{margin:0;padding:0;box-sizing:border-box;}}
          body {{background:transparent;}}
          @keyframes shimmer {{
            0%   {{background-position: -200% center;}}
            100% {{background-position:  200% center;}}
          }}
          .banner {{
            background: linear-gradient(135deg, #0d1f1e 0%, #0a1f18 50%, #0d1f1e 100%);
            border:1px solid #0d9488;
            border-radius:16px;
            padding:2rem;
            text-align:center;
          }}
          .title {{
            font-family:'Syne',sans-serif;
            font-size:1.8rem;
            font-weight:800;
            background: linear-gradient(135deg, #ffffff, #2dd4bf, #0d9488);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s linear infinite;
          }}
          .sub {{
            font-family:'DM Sans',sans-serif;
            color:#94a3b8;
            font-size:0.9rem;
            margin-top:0.5rem;
            line-height:1.6;
          }}
          .tags {{
            display:flex;
            justify-content:center;
            gap:0.6rem;
            flex-wrap:wrap;
            margin-top:1rem;
          }}
          .tag {{
            background:#0d948822;
            border:1px solid #0d948844;
            color:#2dd4bf;
            border-radius:20px;
            padding:0.3rem 0.9rem;
            font-size:0.78rem;
            font-family:'DM Sans',sans-serif;
          }}
        </style>
        </head><body>
        <div class="banner">
          <div style="font-size:3rem; margin-bottom:0.8rem;">🎉</div>
          <div class="title">Clinical Package Complete!</div>
          <div class="sub">
            Full ClinicalCrew analysis for <b style="color:#2dd4bf;">{patient_name}</b>
            has been generated.<br>
            All outputs are for clinical decision support only and require physician review.
          </div>
          <div class="tags">
            <span class="tag">✅ Phase 1 — Report Intake</span>
            <span class="tag">✅ Phase 2 — Diagnosis Analysis</span>
            <span class="tag">✅ Phase 3 — Treatment Planning</span>
            <span class="tag">✅ Phase 4 — Clinical Summary</span>
          </div>
        </div>
        </body></html>""",
        height=260,
    )


# ── Main ───────────────────────────────────────────────────────
def main():
    _init_session()
    inject_styles()

    patient_name = st.session_state.get("patient_name", "") or "Patient"
    page_header(
        "📄",
        "Clinical Summary",
        f"Phase 4 — Full clinical package generation for {patient_name}",
    )
    disclaimer_banner()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gate Checks ─────────────────────────────────────────────
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

    if not st.session_state.treatment_result:
        st.warning(
            "⚠️ Please complete **Phase 3 — Treatment Planning** first.",
            icon="💊",
        )
        st.stop()

    # ── Model Selector for Phase 4 ──────────────────────────────
    from utils.model_selector import render_phase_model_selector

    st.markdown(
        "<h3 style='font-family:Syne,sans-serif; color:#e2f0ef; "
        "font-size:1rem; margin-bottom:0.3rem;'>🤖 Select AI Model for Phase 4</h3>",
        unsafe_allow_html=True,
    )
    selected_model = render_phase_model_selector("phase4")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Run Button ──────────────────────────────────────────────
    col_btn, _ = st.columns([2, 3])
    with col_btn:
        run_btn = st.button(
            "🚀 Run Summary Crew (Phase 4)",
            use_container_width=True,
            type="primary",
            disabled=(selected_model is None),  # ← Fix 6: guard
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

        for phase in ["report", "patient", "followup"]:
            render_log(_build_log_lines(phase), running=True, height=400)
            time.sleep(0.5)

        with st.spinner("🤖 Agents working — this may take 60-120 seconds..."):
            try:
                from crews.crews import run_summary_crew

                context_raw  = st.session_state.get("_context_raw",  "{}")
                symptom_raw  = st.session_state.get("_symptom_raw",  "{}")
                lab_raw      = st.session_state.get("_lab_raw",      "{}")
                risk_raw     = st.session_state.get("_risk_raw",     "{}")
                treatment_raw = st.session_state.get("_treatment_raw","{}")
                drug_raw     = st.session_state.get("_drug_raw",     "{}")
                dosage_raw   = st.session_state.get("_dosage_raw",   "{}")

                result = run_summary_crew(
                    patient_context=context_raw,
                    symptom_analysis=symptom_raw,
                    lab_interpretation=lab_raw,
                    risk_assessment=risk_raw,
                    treatment_suggestions=treatment_raw,
                    drug_interactions=drug_raw,
                    dosage_recommendations=dosage_raw,
                    phase_key="phase4",        # ← Fix 6: phase_key pass
                )

                st.session_state.summary_result = result

                # Save to Supabase
                try:
                    from utils.database import save_clinical_report
                    save_clinical_report(
                        patient_id=st.session_state.get("patient_id"),
                        diagnosis=st.session_state.diagnosis_result or {},
                        treatment_plan=st.session_state.treatment_result or {},
                        doctor_summary=result.get("physician_report", ""),
                        patient_summary=result.get("patient_summary", ""),
                        followup_plan=result.get("followup_plan", {}),
                    )
                except Exception:
                    pass

                from utils.execution_log import render_log as rl
                rl(_build_log_lines("done"), running=False, height=400)
                st.success(
                    "✅ Phase 4 Complete! Full clinical package generated.",
                    icon="🎉",
                )

            except Exception as e:
                from utils.execution_log import render_log as rl
                rl(
                    _build_log_lines("report") + [
                        {"tag": "ERROR", "msg": f"Crew failed: {str(e)[:120]}"}
                    ],
                    running=False,
                    height=400,
                )
                st.error(f"❌ Error: {e}")

    # ── Results ─────────────────────────────────────────────────
    if st.session_state.summary_result:
        st.markdown("<br>", unsafe_allow_html=True)

        result = st.session_state.summary_result

        # Completion Banner
        _render_completion_banner(patient_name)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='font-family:Syne,sans-serif; color:#e2f0ef; "
            "font-size:1.3rem; margin-bottom:0.5rem;'>📊 Phase 4 Results</h2>",
            unsafe_allow_html=True,
        )

        r_tab1, r_tab2, r_tab3 = st.tabs([
            "🩺 Physician Report",
            "👤 Patient Summary",
            "📅 Follow-Up Plan",
        ])

        with r_tab1:
            _render_physician_report(
                result.get("physician_report", ""),
                patient_name,
            )

        with r_tab2:
            _render_patient_summary(
                result.get("patient_summary", ""),
                patient_name,
            )

        with r_tab3:
            _render_followup_plan(
                result.get("followup_plan", {})
            )

        # ── Final Disclaimer ────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        disclaimer_banner()

        st.markdown("<br>", unsafe_allow_html=True)
        components.html(
            """<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
            <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:transparent;}}</style>
            </head><body>
            <div style="background:#111918; border:1px solid #1f2937;
                        border-radius:10px; padding:1rem 1.2rem; text-align:center;">
              <div style="font-family:'DM Sans',sans-serif; color:#475569;
                          font-size:0.8rem; line-height:1.7;">
                ClinicalCrew is powered by CrewAI + LLaMA 3.3 70B (Groq) |
                Built for clinical decision support only |
                All outputs require physician review before clinical action
              </div>
            </div>
            </body></html>""",
            height=70,
        )


if __name__ == "__main__":
    main()
