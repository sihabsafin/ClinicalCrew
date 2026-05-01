import json
from crewai import Crew, Process


# ─────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────

def _safe_json(raw) -> dict:
    """Safely parse JSON from agent output with fallback."""
    try:
        text = str(raw).strip()
        # Remove markdown code fences if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception:
        return {"raw_output": str(raw)}


def _out(task) -> str:
    """Safely extract raw string output from a task result."""
    try:
        o = task.output
        if hasattr(o, "raw"):
            return str(o.raw)
        return str(o)
    except Exception:
        return "{}"


# ─────────────────────────────────────────
# PHASE 1 — Report Intake Crew
# ─────────────────────────────────────────

def run_intake_crew(report_text: str, phase_key: str = "phase1") -> dict:
    """
    Phase 1: Parse report, build patient context, validate data.
    Returns dict with keys: parsed_report, patient_context, validation
    """
    from agents.agents import (
        get_report_parser_agent,
        get_patient_context_agent,
        get_data_validator_agent,
    )
    from agents.tasks import (
        task_parse_report,
        task_build_patient_context,
        task_validate_data,
    )

    # Instantiate agents
    parser_agent    = get_report_parser_agent(phase_key)
    context_agent   = get_patient_context_agent(phase_key)
    validator_agent = get_data_validator_agent(phase_key)

    # Build tasks
    t1 = task_parse_report(parser_agent, report_text)
    t2 = task_build_patient_context(context_agent, report_text)
    t3 = task_validate_data(validator_agent, report_text, report_text)

    # Run crew
    crew = Crew(
        agents=[parser_agent, context_agent, validator_agent],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()

    # Extract outputs
    parsed_raw    = _out(t1)
    context_raw   = _out(t2)
    validation_raw = _out(t3)

    parsed_report   = _safe_json(parsed_raw)
    patient_context = _safe_json(context_raw)
    validation      = _safe_json(validation_raw)

    return {
        "parsed_report":   parsed_report,
        "patient_context": patient_context,
        "validation":      validation,
        # Raw strings for passing to next crews
        "_parsed_raw":   parsed_raw,
        "_context_raw":  context_raw,
    }


# ─────────────────────────────────────────
# PHASE 2 — Diagnosis Analysis Crew
# ─────────────────────────────────────────

def run_diagnosis_crew(
    parsed_report: str,
    patient_context: str,
    phase_key: str = "phase2",
) -> dict:
    """
    Phase 2: Symptom analysis, lab interpretation, risk assessment.
    Returns dict with keys: symptom_analysis, lab_interpretation, risk_assessment
    """
    from agents.agents import (
        get_symptom_analyzer_agent,
        get_lab_interpreter_agent,
        get_risk_assessor_agent,
    )
    from agents.tasks import (
        task_analyze_symptoms,
        task_interpret_labs,
        task_assess_risk,
    )

    # Instantiate agents
    symptom_agent = get_symptom_analyzer_agent(phase_key)
    lab_agent     = get_lab_interpreter_agent(phase_key)
    risk_agent    = get_risk_assessor_agent(phase_key)

    # Build tasks
    t1 = task_analyze_symptoms(symptom_agent, patient_context, parsed_report)
    t2 = task_interpret_labs(lab_agent, parsed_report, patient_context)
    t3 = task_assess_risk(risk_agent, patient_context, parsed_report, parsed_report)

    # Run crew
    crew = Crew(
        agents=[symptom_agent, lab_agent, risk_agent],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()

    # Extract outputs
    symptom_raw = _out(t1)
    lab_raw     = _out(t2)
    risk_raw    = _out(t3)

    symptom_analysis   = _safe_json(symptom_raw)
    lab_interpretation = _safe_json(lab_raw)
    risk_assessment    = _safe_json(risk_raw)

    return {
        "symptom_analysis":   symptom_analysis,
        "lab_interpretation": lab_interpretation,
        "risk_assessment":    risk_assessment,
        # Raw strings for passing to next crews
        "_symptom_raw": symptom_raw,
        "_lab_raw":     lab_raw,
        "_risk_raw":    risk_raw,
    }


# ─────────────────────────────────────────
# PHASE 3 — Treatment Planning Crew
# ─────────────────────────────────────────

def run_treatment_crew(
    patient_context: str,
    symptom_analysis: str,
    risk_assessment: str,
    lab_interpretation: str,
    phase_key: str = "phase3",
) -> dict:
    """
    Phase 3: Treatment suggestions, drug interactions, dosage calculation.
    Returns dict with keys: treatment_suggestions, drug_interactions, dosage_recommendations
    """
    from agents.agents import (
        get_treatment_suggester_agent,
        get_drug_interaction_agent,
        get_dosage_calculator_agent,
    )
    from agents.tasks import (
        task_suggest_treatments,
        task_check_drug_interactions,
        task_calculate_dosages,
    )

    # Instantiate agents
    treatment_agent  = get_treatment_suggester_agent(phase_key)
    drug_agent       = get_drug_interaction_agent(phase_key)
    dosage_agent     = get_dosage_calculator_agent(phase_key)

    # Build tasks — each task uses output of previous as context
    t1 = task_suggest_treatments(
        treatment_agent,
        patient_context,
        symptom_analysis,
        risk_assessment,
    )
    t2 = task_check_drug_interactions(
        drug_agent,
        patient_context,
        symptom_analysis,   # treatment suggestions context
    )
    t3 = task_calculate_dosages(
        dosage_agent,
        patient_context,
        symptom_analysis,   # treatment suggestions context
        risk_assessment,    # drug interaction context
    )

    # Run crew
    crew = Crew(
        agents=[treatment_agent, drug_agent, dosage_agent],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()

    # Extract outputs
    treatment_raw = _out(t1)
    drug_raw      = _out(t2)
    dosage_raw    = _out(t3)

    treatment_suggestions  = _safe_json(treatment_raw)
    drug_interactions      = _safe_json(drug_raw)
    dosage_recommendations = _safe_json(dosage_raw)

    return {
        "treatment_suggestions":  treatment_suggestions,
        "drug_interactions":      drug_interactions,
        "dosage_recommendations": dosage_recommendations,
        # Raw strings for passing to next crew
        "_treatment_raw": treatment_raw,
        "_drug_raw":      drug_raw,
        "_dosage_raw":    dosage_raw,
    }


# ─────────────────────────────────────────
# PHASE 4 — Clinical Summary Crew
# ─────────────────────────────────────────

def run_summary_crew(
    patient_context: str,
    symptom_analysis: str,
    lab_interpretation: str,
    risk_assessment: str,
    treatment_suggestions: str,
    drug_interactions: str,
    dosage_recommendations: str,
    phase_key: str = "phase4",
) -> dict:
    """
    Phase 4: Physician report, patient summary, follow-up plan.
    Returns dict with keys: physician_report, patient_summary, followup_plan
    """
    from agents.agents import (
        get_report_writer_agent,
        get_patient_explainer_agent,
        get_followup_planner_agent,
    )
    from agents.tasks import (
        task_write_physician_report,
        task_write_patient_summary,
        task_create_followup_plan,
    )

    # Instantiate agents
    writer_agent    = get_report_writer_agent(phase_key)
    explainer_agent = get_patient_explainer_agent(phase_key)
    followup_agent  = get_followup_planner_agent(phase_key)

    # Build tasks
    t1 = task_write_physician_report(
        writer_agent,
        patient_context,
        symptom_analysis,
        lab_interpretation,
        risk_assessment,
        treatment_suggestions,
        drug_interactions,
        dosage_recommendations,
    )
    t2 = task_write_patient_summary(
        explainer_agent,
        patient_context,
        symptom_analysis,
        treatment_suggestions,
        risk_assessment,
    )
    t3 = task_create_followup_plan(
        followup_agent,
        patient_context,
        risk_assessment,
        treatment_suggestions,
        lab_interpretation,
    )

    # Run crew
    crew = Crew(
        agents=[writer_agent, explainer_agent, followup_agent],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()

    # Extract outputs
    physician_raw  = _out(t1)
    patient_raw    = _out(t2)
    followup_raw   = _out(t3)

    # Physician report and patient summary are plain text (not JSON)
    # Follow-up plan is JSON
    followup_plan = _safe_json(followup_raw)

    return {
        "physician_report": physician_raw,
        "patient_summary":  patient_raw,
        "followup_plan":    followup_plan,
        # Raw strings for storage
        "_physician_raw": physician_raw,
        "_patient_raw":   patient_raw,
        "_followup_raw":  followup_raw,
    }
