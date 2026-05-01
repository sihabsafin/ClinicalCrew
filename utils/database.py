import json


SCHEMA_SQL = """
create table if not exists patients (
    id              uuid primary key default gen_random_uuid(),
    name            text,
    age             int,
    gender          text,
    report_text     text,
    patient_context jsonb,
    created_at      timestamptz default now()
);

create table if not exists analyses (
    id              uuid primary key default gen_random_uuid(),
    patient_id      uuid references patients(id),
    phase           text,
    result_json     jsonb,
    created_at      timestamptz default now()
);

create table if not exists clinical_reports (
    id              uuid primary key default gen_random_uuid(),
    patient_id      uuid references patients(id),
    diagnosis       jsonb,
    treatment_plan  jsonb,
    doctor_summary  text,
    patient_summary text,
    followup_plan   jsonb,
    created_at      timestamptz default now()
);
"""


def _get_client():
    try:
        from config import _secret
        from supabase import create_client
        url = _secret("SUPABASE_URL")
        key = _secret("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def save_patient(name: str, age: int, gender: str,
                 report_text: str, patient_context: dict) -> str | None:
    client = _get_client()
    if not client:
        return None
    try:
        res = client.table("patients").insert({
            "name": name,
            "age": age,
            "gender": gender,
            "report_text": report_text,
            "patient_context": patient_context,
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        print(f"[DB] save_patient error: {e}")
        return None


def save_analysis(patient_id: str, phase: str, result: dict) -> bool:
    client = _get_client()
    if not client or not patient_id:
        return False
    try:
        client.table("analyses").insert({
            "patient_id": patient_id,
            "phase": phase,
            "result_json": result,
        }).execute()
        return True
    except Exception as e:
        print(f"[DB] save_analysis error: {e}")
        return False


def save_clinical_report(patient_id: str, diagnosis: dict,
                          treatment_plan: dict, doctor_summary: str,
                          patient_summary: str, followup_plan: dict) -> bool:
    client = _get_client()
    if not client or not patient_id:
        return False
    try:
        client.table("clinical_reports").insert({
            "patient_id": patient_id,
            "diagnosis": diagnosis,
            "treatment_plan": treatment_plan,
            "doctor_summary": doctor_summary,
            "patient_summary": patient_summary,
            "followup_plan": followup_plan,
        }).execute()
        return True
    except Exception as e:
        print(f"[DB] save_clinical_report error: {e}")
        return False


def get_patient_count() -> int:
    client = _get_client()
    if not client:
        return 0
    try:
        res = client.table("patients").select("id", count="exact").execute()
        return res.count or 0
    except Exception:
        return 0


def get_analysis_count() -> int:
    client = _get_client()
    if not client:
        return 0
    try:
        res = client.table("analyses").select("id", count="exact").execute()
        return res.count or 0
    except Exception:
        return 0