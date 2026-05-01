from crewai import Task


# ─────────────────────────────────────────
# PHASE 1 — Report Intake Tasks
# ─────────────────────────────────────────

def task_parse_report(agent, report_text: str) -> Task:
    return Task(
        description=f"""
        Parse the following medical report and extract ALL structured clinical data.

        MEDICAL REPORT:
        {report_text}

        Extract and return a comprehensive JSON object with these exact sections:
        1. patient_demographics: name, age, gender, date, referring_physician
        2. chief_complaint: main presenting complaint as a string
        3. history_present_illness: detailed HPI as a string
        4. past_medical_history: list of conditions with year diagnosed if available
        5. current_medications: list of objects with name, dose, frequency, route
        6. allergies: list of objects with allergen and reaction
        7. vital_signs: bp, heart_rate, rr, temperature, spo2, weight_kg, height_cm, bmi
        8. physical_exam: dict of system findings (cardiovascular, respiratory, etc.)
        9. lab_results: list of objects with test_name, value, unit, reference_range, flag (H/L/N/C/CRITICAL)
        10. investigations: list of objects with type (ECG/XRay/Echo etc.) and findings
        11. clinical_impression: the physician impression as written in the report

        RULES:
        - If data is not present, use "Not reported" — NEVER invent data
        - Preserve exact numeric values and units
        - Flag CRITICAL for any value that is life-threatening
        - Return ONLY valid JSON, no extra text
        """,
        expected_output="""
        A valid JSON object with keys: patient_demographics, chief_complaint,
        history_present_illness, past_medical_history, current_medications,
        allergies, vital_signs, physical_exam, lab_results, investigations,
        clinical_impression. All values populated from the report text only.
        """,
        agent=agent,
    )


def task_build_patient_context(agent, parsed_report: str) -> Task:
    return Task(
        description=f"""
        Using the parsed medical report data below, build a comprehensive
        patient clinical context profile.

        PARSED REPORT DATA:
        {parsed_report}

        Build and return a JSON object with these sections:
        1. patient_summary: one paragraph clinical summary of the patient
        2. comorbidities: list of objects with:
           - condition (name)
           - severity (controlled/uncontrolled/unknown)
           - relevant_to_presentation (true/false)
           - notes (brief clinical note)
        3. medication_profile: list of objects with:
           - name, drug_class, indication, relevant_interactions_risk (low/moderate/high)
        4. allergy_profile: object with:
           - allergens (list), cross_reactivity_risks (list), safe_drug_classes (list)
        5. risk_factors: list of strings (e.g., "Male sex", "Age >55", "Poorly controlled DM")
        6. clinical_complexity: low/moderate/high with reasoning
        7. key_concerns: list of top 3-5 clinical concerns requiring attention

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: patient_summary, comorbidities,
        medication_profile, allergy_profile, risk_factors,
        clinical_complexity, key_concerns.
        """,
        agent=agent,
    )


def task_validate_data(agent, parsed_report: str, patient_context: str) -> Task:
    return Task(
        description=f"""
        Validate the completeness and consistency of the extracted medical report data.

        PARSED REPORT:
        {parsed_report}

        PATIENT CONTEXT:
        {patient_context}

        Perform validation and return a JSON object with:
        1. completeness_score: integer 0-100
        2. completeness_breakdown: object with scores for each section:
           - demographics, history, medications, allergies, vitals,
             physical_exam, labs, investigations
        3. missing_critical_data: list of strings describing missing important items
        4. data_contradictions: list of strings describing any inconsistencies found
        5. data_quality_flags: list of strings for any quality concerns
        6. safe_to_proceed: true or false
        7. proceed_caveats: list of strings — warnings to carry through all analysis
        8. validator_notes: brief overall assessment string

        RULES FOR safe_to_proceed:
        - Set false if completeness_score < 40
        - Set false if critical data like medications or allergies are completely missing
        - Set true with caveats if score is 40-70
        - Set true if score > 70

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: completeness_score, completeness_breakdown,
        missing_critical_data, data_contradictions, data_quality_flags,
        safe_to_proceed, proceed_caveats, validator_notes.
        """,
        agent=agent,
    )


# ─────────────────────────────────────────
# PHASE 2 — Diagnosis Analysis Tasks
# ─────────────────────────────────────────

def task_analyze_symptoms(agent, patient_context: str, parsed_report: str) -> Task:
    return Task(
        description=f"""
        Perform a comprehensive symptom analysis and generate a differential diagnosis.

        PATIENT CONTEXT:
        {patient_context}

        PARSED REPORT DATA:
        {parsed_report}

        Return a JSON object with:
        1. clinical_impression: your overall clinical impression in 2-3 sentences
        2. symptom_clusters: list of objects with:
           - cluster_name (e.g., "Cardiac syndrome", "Metabolic derangement")
           - symptoms (list of symptoms in this cluster)
           - clinical_significance (string)
        3. differential_diagnosis: list of objects ordered by likelihood:
           - diagnosis (name)
           - likelihood (high/medium/low)
           - supporting_evidence (list of findings that support this)
           - against_evidence (list of findings that argue against)
           - reasoning (one paragraph clinical reasoning)
           - urgency (emergent/urgent/non-urgent)
        4. red_flags: list of objects with:
           - finding (the red flag finding)
           - concern (what it may indicate)
           - action_required (what should be done)
           - timeframe (immediate/within hours/within days)
        5. missing_diagnostic_info: list of additional history or exam findings
           that would help narrow the differential

        DISCLAIMER: Add a field "disclaimer" with value:
        "This differential diagnosis is AI-generated for decision support only.
        Final diagnosis must be made by a licensed physician."

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: clinical_impression, symptom_clusters,
        differential_diagnosis, red_flags, missing_diagnostic_info, disclaimer.
        Differential diagnosis ordered from highest to lowest likelihood.
        """,
        agent=agent,
    )


def task_interpret_labs(agent, parsed_report: str, patient_context: str) -> Task:
    return Task(
        description=f"""
        Interpret all laboratory results and investigation findings from the medical report.

        PARSED REPORT DATA:
        {parsed_report}

        PATIENT CONTEXT:
        {patient_context}

        Return a JSON object with:
        1. critical_values: list of objects with:
           - test_name, value, reference_range
           - clinical_significance (why this is dangerous)
           - urgency (immediate/within hours)
           - recommended_action
        2. abnormal_values: list of objects with:
           - test_name, value, reference_range, flag (H/L)
           - clinical_significance
           - urgency (routine/soon/urgent)
           - trend_concern (true/false)
        3. normal_values: list of test names that are within normal range
        4. lab_patterns: list of objects with:
           - pattern_name (e.g., "Acute kidney injury pattern", "Dyslipidemia pattern")
           - contributing_tests (list of test names)
           - clinical_significance
        5. investigation_findings: list of objects with:
           - investigation_type (ECG/XRay/Echo etc.)
           - key_findings (list)
           - clinical_significance
           - urgency
        6. missing_important_tests: list of objects with:
           - test_name
           - reason_needed
           - urgency (routine/soon/urgent)

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: critical_values, abnormal_values,
        normal_values, lab_patterns, investigation_findings, missing_important_tests.
        Critical values must be listed first and prominently flagged.
        """,
        agent=agent,
    )


def task_assess_risk(agent, patient_context: str,
                     symptom_analysis: str, lab_interpretation: str) -> Task:
    return Task(
        description=f"""
        Calculate overall patient risk and generate a prioritized clinical action plan.

        PATIENT CONTEXT:
        {patient_context}

        SYMPTOM ANALYSIS:
        {symptom_analysis}

        LAB INTERPRETATION:
        {lab_interpretation}

        Return a JSON object with:
        1. overall_risk_level: critical/high/moderate/low
        2. risk_reasoning: paragraph explaining overall risk assessment
        3. clinical_scores: list of objects with:
           - score_name (e.g., "CHADS2-VASc", "Wells PE", "qSOFA", "TIMI")
           - score_value (calculated score)
           - interpretation (what the score means)
           - applicable (true/false — only include if applicable to this patient)
        4. urgent_actions: list of objects (actions needed within hours):
           - action (what to do)
           - reason (why it is urgent)
           - timeframe (e.g., "Within 1 hour", "Within 4 hours")
           - responsible_party (physician/nurse/lab/cardiology etc.)
        5. important_actions: list of objects (actions needed within days):
           - action
           - reason
           - timeframe (e.g., "Within 24 hours", "Within 48 hours", "Within 1 week")
           - responsible_party
        6. monitoring_parameters: list of objects with:
           - parameter (what to monitor)
           - frequency
           - target_value (if applicable)
        7. disposition_recommendation: admit/observe/discharge_with_followup/urgent_referral
        8. disposition_reasoning: string explaining recommendation

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: overall_risk_level, risk_reasoning,
        clinical_scores, urgent_actions, important_actions,
        monitoring_parameters, disposition_recommendation, disposition_reasoning.
        """,
        agent=agent,
    )


# ─────────────────────────────────────────
# PHASE 3 — Treatment Planning Tasks
# ─────────────────────────────────────────

def task_suggest_treatments(agent, patient_context: str,
                             symptom_analysis: str, risk_assessment: str) -> Task:
    return Task(
        description=f"""
        Generate evidence-based treatment options for this patient's conditions.

        PATIENT CONTEXT:
        {patient_context}

        SYMPTOM ANALYSIS AND DIAGNOSIS:
        {symptom_analysis}

        RISK ASSESSMENT:
        {risk_assessment}

        Return a JSON object with:
        1. treatment_goals: list of strings (overall treatment objectives)
        2. condition_treatments: list of objects, one per condition being treated:
           - condition (name of condition)
           - first_line: list of objects with:
             * drug_or_intervention (name)
             * type (pharmacological/non-pharmacological/procedural)
             * evidence_grade (A/B/C)
             * guideline_source (WHO/AHA/ADA/NICE/ESC)
             * rationale (why this is first line for THIS patient)
             * considerations (patient-specific factors to consider)
           - second_line: same structure as first_line
           - alternatives: same structure
           - contraindicated: list of objects with:
             * drug_or_intervention
             * reason_contraindicated
        3. non_pharmacological: list of objects with:
           - intervention (e.g., "Cardiac rehabilitation", "Low sodium diet")
           - evidence_grade (A/B/C)
           - rationale
        4. treatment_priorities: ordered list of what to address first, second, etc.
        5. special_considerations: list of patient-specific factors affecting treatment
           (e.g., renal impairment, drug allergies, polypharmacy)

        MANDATORY: Add field "disclaimer":
        "All treatment suggestions are AI-generated for clinical decision support only.
        No medication should be prescribed or administered without review and approval
        by a licensed physician."

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: treatment_goals, condition_treatments,
        non_pharmacological, treatment_priorities, special_considerations, disclaimer.
        Evidence grades and guideline sources must be included for all recommendations.
        """,
        agent=agent,
    )


def task_check_drug_interactions(agent, patient_context: str,
                                  treatment_suggestions: str) -> Task:
    return Task(
        description=f"""
        Perform a comprehensive drug safety check for all suggested medications.

        PATIENT CONTEXT (includes current medications and allergies):
        {patient_context}

        TREATMENT SUGGESTIONS:
        {treatment_suggestions}

        Return a JSON object with:
        1. overall_safety_clearance: safe/caution/contraindicated
        2. safety_summary: one paragraph summary of key safety findings
        3. drug_drug_interactions: list of objects with:
           - drug_1, drug_2
           - severity (Major/Moderate/Minor)
           - mechanism (how the interaction occurs)
           - clinical_effect (what happens to the patient)
           - management (what to do about it)
           - recommendation (use_with_monitoring/avoid/contraindicated/alternative_preferred)
        4. drug_disease_contraindications: list of objects with:
           - drug
           - disease
           - risk (why this combination is dangerous)
           - recommendation
        5. allergy_alerts: list of objects with:
           - suggested_drug
           - allergen_concern
           - cross_reactivity_risk (high/moderate/low)
           - safe_alternative
        6. renal_dose_flags: list of drugs needing dose adjustment for renal impairment
        7. hepatic_dose_flags: list of drugs needing dose adjustment for hepatic impairment
        8. safe_medications: list of drug names cleared as safe with no major concerns
        9. recommended_alternatives: list of objects with:
           - original_drug (to replace)
           - alternative_drug
           - reason_for_switch

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: overall_safety_clearance, safety_summary,
        drug_drug_interactions, drug_disease_contraindications, allergy_alerts,
        renal_dose_flags, hepatic_dose_flags, safe_medications, recommended_alternatives.
        Major interactions must be listed first.
        """,
        agent=agent,
    )


def task_calculate_dosages(agent, patient_context: str,
                            treatment_suggestions: str,
                            drug_interaction_check: str) -> Task:
    return Task(
        description=f"""
        Calculate patient-specific dosing for all safe and recommended medications.

        PATIENT CONTEXT (weight, age, renal function, hepatic function):
        {patient_context}

        TREATMENT SUGGESTIONS:
        {treatment_suggestions}

        DRUG INTERACTION CHECK (use this to exclude contraindicated drugs):
        {drug_interaction_check}

        Return a JSON object with:
        1. patient_dosing_parameters: object with:
           - weight_kg, age, egfr, hepatic_function_assessment
           - renal_category (normal/>60 / mild_impairment/30-60 / moderate/15-30 / severe/<15)
        2. dosing_recommendations: list of objects per medication:
           - drug_name
           - indication (what it is being used for)
           - standard_dose (what a standard adult would receive)
           - recommended_dose (patient-specific adjusted dose)
           - frequency (e.g., "Once daily", "Twice daily")
           - route (oral/IV/subcutaneous etc.)
           - duration (e.g., "Indefinite", "7 days", "Until review")
           - dose_adjustments: list of adjustments made with reasoning:
             * adjustment_type (renal/hepatic/age/weight)
             * standard (what the standard dose is)
             * adjusted (what the adjusted dose is)
             * reasoning (clinical reason for adjustment)
           - monitoring_required: list of parameters to monitor
           - titration_notes: any notes on how to up/down titrate
        3. high_risk_medications: list of drugs requiring extra caution with reasons
        4. dosing_schedule_summary: plain text summary of the complete daily
           medication schedule (morning/afternoon/evening/night)

        MANDATORY: Add field "disclaimer":
        "All dosing recommendations are AI-generated estimates for decision support only.
        Every dose MUST be verified and approved by a licensed physician or clinical
        pharmacist before prescribing or administering to any patient."

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: patient_dosing_parameters,
        dosing_recommendations, high_risk_medications,
        dosing_schedule_summary, disclaimer.
        Every recommended dose must include reasoning for any adjustment from standard dose.
        """,
        agent=agent,
    )


# ─────────────────────────────────────────
# PHASE 4 — Clinical Summary Tasks
# ─────────────────────────────────────────

def task_write_physician_report(agent, patient_context: str, symptom_analysis: str,
                                 lab_interpretation: str, risk_assessment: str,
                                 treatment_suggestions: str, drug_interaction_check: str,
                                 dosage_recommendations: str) -> Task:
    return Task(
        description=f"""
        Write a comprehensive structured SOAP-format clinical summary report
        for the treating physician.

        PATIENT CONTEXT: {patient_context}
        SYMPTOM ANALYSIS: {symptom_analysis}
        LAB INTERPRETATION: {lab_interpretation}
        RISK ASSESSMENT: {risk_assessment}
        TREATMENT SUGGESTIONS: {treatment_suggestions}
        DRUG SAFETY CHECK: {drug_interaction_check}
        DOSAGE RECOMMENDATIONS: {dosage_recommendations}

        Write a complete physician report with these clearly labeled sections:

        ## PATIENT SUMMARY
        [Demographics, complexity, key comorbidities — 3-4 sentences]

        ## PRESENTING COMPLAINT
        [Chief complaint and HPI — 2-3 sentences]

        ## KEY CLINICAL FINDINGS
        ### Vital Signs
        [Abnormal vitals with clinical significance]
        ### Laboratory Results
        [Critical and abnormal values with clinical significance]
        ### Investigation Findings
        [ECG, imaging, echo findings]

        ## WORKING DIAGNOSIS
        [Primary working diagnosis with supporting evidence]
        ### Differential Diagnosis
        [Ranked differential with brief reasoning]

        ## RISK ASSESSMENT
        [Risk level, clinical scores, key risk factors]

        ## PROPOSED MANAGEMENT PLAN
        ### Immediate Actions Required
        [Urgent actions within hours]
        ### Pharmacological Treatment
        [Recommended medications with doses — labeled as suggestions requiring approval]
        ### Non-Pharmacological
        [Lifestyle, dietary, other interventions]

        ## DRUG SAFETY NOTES
        [Key interactions, contraindications, allergy alerts]

        ## ITEMS REQUIRING PHYSICIAN DECISION
        [Explicit list of decisions the physician must make]

        ## FOLLOW-UP REQUIRED
        [Brief follow-up summary]

        ## AI DISCLAIMER
        This report was generated by ClinicalCrew AI decision support system.
        All findings, diagnoses, and management suggestions require review and
        approval by a licensed physician before any clinical action is taken.
        This report does not constitute a medical diagnosis or prescription.

        Write in clear professional medical language. Be concise but complete.
        Return the full report as a formatted text string (not JSON).
        """,
        expected_output="""
        A complete, well-structured physician report in SOAP format with all
        sections filled in. Professional medical language. Clear section headers.
        Includes mandatory AI disclaimer at the end.
        """,
        agent=agent,
    )


def task_write_patient_summary(agent, patient_context: str, symptom_analysis: str,
                                treatment_suggestions: str, risk_assessment: str) -> Task:
    return Task(
        description=f"""
        Write a patient-friendly explanation of the medical findings and recommendations.

        PATIENT CONTEXT: {patient_context}
        SYMPTOM ANALYSIS: {symptom_analysis}
        TREATMENT SUGGESTIONS: {treatment_suggestions}
        RISK ASSESSMENT: {risk_assessment}

        Write a complete patient summary with these sections:

        ## WHAT WE FOUND
        [Explain the key findings in plain English — no jargon.
         Use analogies to explain complex concepts.
         Short sentences. Maximum reading level: Grade 8.]

        ## WHAT THIS MEANS FOR YOU
        [Explain what the findings mean for the patient's daily life and health.
         Be honest but reassuring. Focus on what can be done.]

        ## WHAT HAPPENS NEXT
        [Explain the proposed next steps in simple terms.
         What tests, treatments, or specialist visits are planned.]

        ## YOUR MEDICATIONS
        [Explain each medication in plain language:
         what it does, why it is prescribed, how to take it.
         Remind patient their doctor makes final decisions on medications.]

        ## WHAT TO WATCH FOR
        [List warning signs that mean the patient should seek immediate help.
         Use simple, direct language: "Go to emergency immediately if..."]

        ## IMPORTANT REMINDER
        [Remind patient that this summary was created with AI assistance and
         their doctor has reviewed all recommendations. Their doctor is their
         primary source of medical advice.]

        RULES:
        - No medical jargon — explain every technical term if used
        - Short paragraphs and sentences
        - Warm, supportive, empowering tone
        - Never cause unnecessary alarm
        - Always direct patient to their physician for decisions

        Return the full patient summary as formatted text (not JSON).
        """,
        expected_output="""
        A complete patient-friendly summary with all sections. Plain language,
        no jargon, warm supportive tone. Includes warning signs and reminder
        to consult physician for all medical decisions.
        """,
        agent=agent,
    )


def task_create_followup_plan(agent, patient_context: str, risk_assessment: str,
                               treatment_suggestions: str, lab_interpretation: str) -> Task:
    return Task(
        description=f"""
        Create a detailed structured follow-up plan for this patient.

        PATIENT CONTEXT: {patient_context}
        RISK ASSESSMENT: {risk_assessment}
        TREATMENT SUGGESTIONS: {treatment_suggestions}
        LAB INTERPRETATION: {lab_interpretation}

        Return a JSON object with:
        1. followup_appointments: list of objects with:
           - specialty (e.g., Cardiology, Endocrinology, General Medicine)
           - purpose (reason for the appointment)
           - timeframe (e.g., "Within 1 week", "Within 1 month", "In 3 months")
           - urgency (urgent/routine)
           - preparation_required (any tests needed before the appointment)
        2. repeat_investigations: list of objects with:
           - test_name
           - timeframe (when to repeat)
           - rationale (why it needs to be repeated)
           - target_result (what value to aim for, if applicable)
        3. monitoring_schedule: list of objects with:
           - parameter (what to monitor e.g., blood pressure, blood glucose)
           - frequency (how often e.g., daily, weekly)
           - method (how e.g., home BP monitor, clinic visit, blood test)
           - target_range
        4. specialist_referrals: list of objects with:
           - specialty
           - reason
           - urgency (urgent within days / soon within weeks / routine)
           - referral_notes (what information to include in referral)
        5. lifestyle_recommendations: list of objects with:
           - category (diet/exercise/smoking/alcohol/stress/sleep)
           - recommendation (specific actionable recommendation)
           - evidence_base (why this is recommended)
           - timeline (when to start/achieve)
        6. warning_signs_emergency: list of strings — symptoms requiring
           IMMEDIATE emergency department visit
        7. warning_signs_urgent: list of strings — symptoms requiring
           urgent (same day) physician contact
        8. patient_education_topics: list of topics the patient needs
           to be educated about before discharge/followup

        Return ONLY valid JSON, no extra text.
        """,
        expected_output="""
        A valid JSON object with keys: followup_appointments, repeat_investigations,
        monitoring_schedule, specialist_referrals, lifestyle_recommendations,
        warning_signs_emergency, warning_signs_urgent, patient_education_topics.
        Timeframes must be specific and realistic.
        """,
        agent=agent,
    )