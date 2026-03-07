# =========================================================
# DATABASE LAYER (Psychological Wellness Edition)
# Safe for Student / HR / Research domain
# =========================================================

import os
from typing import Optional, List, Dict
from supabase import create_client, Client


# =========================================================
# Lazy Supabase client
# =========================================================
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """
    Creates Supabase client only once.
    """
    global _supabase_client

    if _supabase_client is None:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "Supabase not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY."
            )

        _supabase_client = create_client(supabase_url, supabase_key)

    return _supabase_client


# =========================================================
# ---------------- SESSION MANAGEMENT ---------------------
# =========================================================

def create_session(participant_name: str) -> Optional[str]:
    """
    Creates a new psychological wellness session.

    participant_name:
        Student / Candidate / Employee

    Returns session_id
    """

    try:
        client = get_supabase()

        response = client.table('sessions').insert({
            "participant_name": participant_name,
            "session_type": "wellness_assessment"
        }).execute()

        if response.data:
            session_id = response.data[0].get('id')
            print(f"✅ Wellness session created: {session_id}")
            return session_id

        return None

    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return None


# =========================================================
# ---------------- SAVE FINAL REPORT ----------------------
# =========================================================

def save_report(
    session_id: str,
    report_text: str,
    wellness_metrics: Dict
):
    """
    Saves final psychological report + metrics
    """

    try:
        client = get_supabase()

        response = client.table('reports').insert({
            "session_id": session_id,
            "report_text": report_text,
            "wellness_metrics": wellness_metrics
        }).execute()

        return response.data

    except Exception as e:
        print(f"❌ Error saving report: {e}")
        return None


# =========================================================
# ---------------- FETCH REPORTS --------------------------
# =========================================================

def get_recent_reports(limit: int = 20) -> List[Dict]:
    """
    Fetch recent wellness reports
    """

    try:
        client = get_supabase()

        resp = (
            client.table('reports')
            .select('*')
            .order('created_at', desc=True)
            .limit(limit)
            .execute()
        )

        return resp.data or []

    except Exception as e:
        print(f"❌ Error fetching reports: {e}")
        return []


def get_report_by_id(report_id: str):
    """
    Fetch single wellness report
    """

    try:
        client = get_supabase()

        resp = (
            client.table('reports')
            .select('*')
            .eq('id', report_id)
            .single()
            .execute()
        )

        return resp.data

    except Exception as e:
        print(f"❌ Error fetching report {report_id}: {e}")
        return None
