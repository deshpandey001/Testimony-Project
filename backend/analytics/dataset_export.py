# =========================================================
# MULTIMODAL DATASET EXPORT
# Create structured research datasets from session data
# =========================================================

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
import csv


def create_dataset_entry(
    session_id: str,
    question_id: int,
    metrics: Dict[str, float],
    wellness_score: float,
    stress_score: float,
    transcription: str = "",
    question_text: str = ""
) -> Dict[str, Any]:
    """
    Create a single dataset entry for research purposes.
    
    Args:
        session_id: Unique session identifier
        question_id: Question number in session
        metrics: Dictionary of numeric metrics
        wellness_score: Computed wellness score (0-100)
        stress_score: Computed stress score (0-1)
        transcription: Speech transcription
        question_text: Question prompt text
        
    Returns:
        Structured dataset entry
    """
    entry = {
        # Identifiers
        "session_id": session_id,
        "question_id": question_id,
        "timestamp": datetime.utcnow().isoformat(),
        
        # Raw metrics
        "blink_rate": metrics.get("blink_rate"),
        "gaze_stability": metrics.get("gaze_stability"),
        "pitch_variance": metrics.get("pitch_variance"),
        "energy_variance": metrics.get("energy_variance"),
        "filler_count": metrics.get("filler_count"),
        "sentiment_polarity": metrics.get("sentiment_polarity"),
        "pause_duration": metrics.get("pause_duration"),
        
        # Computed scores
        "wellness_score": wellness_score,
        "stress_score": stress_score,
        
        # Text data
        "transcription_length": len(transcription) if transcription else 0,
        "word_count": len(transcription.split()) if transcription else 0,
        
        # Metadata
        "question_text": question_text,
        "has_transcription": bool(transcription),
    }
    
    return entry


def export_session_data(
    session_id: str,
    questions_data: List[Dict[str, Any]],
    session_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Export complete session data for research dataset.
    
    Args:
        session_id: Unique session identifier
        questions_data: List of per-question data with metrics
        session_metadata: Optional session-level metadata
        
    Returns:
        Complete session export with all entries
    """
    entries = []
    
    for q_data in questions_data:
        entry = create_dataset_entry(
            session_id=session_id,
            question_id=q_data.get("question_num", len(entries) + 1),
            metrics=q_data.get("metrics", {}),
            wellness_score=q_data.get("wellness_score", 0),
            stress_score=q_data.get("stress_score", 0),
            transcription=q_data.get("transcription", ""),
            question_text=q_data.get("question_text", "")
        )
        entries.append(entry)
    
    # Session-level aggregation
    session_export = {
        "session_id": session_id,
        "export_timestamp": datetime.utcnow().isoformat(),
        "entry_count": len(entries),
        "entries": entries,
        "metadata": session_metadata or {},
        
        # Session aggregates
        "session_aggregates": _compute_session_aggregates(entries)
    }
    
    return session_export


def _compute_session_aggregates(entries: List[Dict]) -> Dict[str, Any]:
    """Compute session-level aggregate statistics."""
    import numpy as np
    
    if not entries:
        return {}
    
    aggregates = {}
    
    # Numeric fields to aggregate
    numeric_fields = [
        "blink_rate", "pitch_variance", "energy_variance",
        "filler_count", "sentiment_polarity", "wellness_score", "stress_score"
    ]
    
    for field in numeric_fields:
        values = [e[field] for e in entries if e.get(field) is not None]
        if values:
            aggregates[f"{field}_mean"] = round(float(np.mean(values)), 4)
            aggregates[f"{field}_std"] = round(float(np.std(values)), 4)
            aggregates[f"{field}_min"] = round(float(min(values)), 4)
            aggregates[f"{field}_max"] = round(float(max(values)), 4)
    
    # Total metrics
    aggregates["total_word_count"] = sum(e.get("word_count", 0) for e in entries)
    aggregates["total_filler_count"] = sum(e.get("filler_count", 0) or 0 for e in entries)
    
    return aggregates


def export_to_csv(
    session_export: Dict[str, Any],
    output_path: str
) -> str:
    """
    Export session data to CSV file.
    
    Args:
        session_export: Result from export_session_data
        output_path: Path for CSV output
        
    Returns:
        Path to created CSV file
    """
    entries = session_export.get("entries", [])
    
    if not entries:
        return ""
    
    # Define column order
    columns = [
        "session_id", "question_id", "timestamp",
        "blink_rate", "gaze_stability", "pitch_variance",
        "energy_variance", "filler_count", "sentiment_polarity",
        "pause_duration", "wellness_score", "stress_score",
        "word_count", "transcription_length", "question_text"
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(entries)
    
    return output_path


def export_to_json(
    session_export: Dict[str, Any],
    output_path: str
) -> str:
    """
    Export session data to JSON file.
    
    Args:
        session_export: Result from export_session_data
        output_path: Path for JSON output
        
    Returns:
        Path to created JSON file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(session_export, f, indent=2, default=str)
    
    return output_path


def prepare_for_supabase(
    session_export: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Prepare dataset entries for Supabase insertion.
    
    Formats entries to match database schema.
    
    Args:
        session_export: Result from export_session_data
        
    Returns:
        List of entries ready for database insertion
    """
    entries = session_export.get("entries", [])
    session_id = session_export.get("session_id")
    
    db_entries = []
    
    for entry in entries:
        db_entry = {
            "session_id": session_id,
            "question_id": entry.get("question_id"),
            "timestamp": entry.get("timestamp"),
            
            # Metrics (store as JSONB or individual columns)
            "metrics": {
                "blink_rate": entry.get("blink_rate"),
                "gaze_stability": entry.get("gaze_stability"),
                "pitch_variance": entry.get("pitch_variance"),
                "energy_variance": entry.get("energy_variance"),
                "filler_count": entry.get("filler_count"),
                "sentiment_polarity": entry.get("sentiment_polarity"),
                "pause_duration": entry.get("pause_duration"),
            },
            
            # Computed scores
            "wellness_score": entry.get("wellness_score"),
            "stress_score": entry.get("stress_score"),
            
            # Text metadata
            "word_count": entry.get("word_count"),
            "transcription_length": entry.get("transcription_length"),
        }
        db_entries.append(db_entry)
    
    return db_entries


def create_session_metrics_record(
    session_id: str,
    session_export: Dict[str, Any],
    wellness_result: Dict[str, Any],
    stress_result: Dict[str, Any],
    consistency_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a session_metrics record for database storage.
    
    Args:
        session_id: Session identifier
        session_export: Full session export
        wellness_result: Aggregated wellness analysis
        stress_result: Stress mapping result
        consistency_result: Consistency analysis result
        
    Returns:
        Record ready for session_metrics table
    """
    aggregates = session_export.get("session_aggregates", {})
    
    return {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        
        # Wellness metrics
        "wellness_score": wellness_result.get("score"),
        "wellness_interpretation": wellness_result.get("interpretation", {}).get("level"),
        
        # Stress metrics
        "average_stress": stress_result.get("average_stress"),
        "peak_stress": stress_result.get("peak_stress_question", {}).get("stress_score"),
        "peak_stress_question": stress_result.get("peak_stress_question", {}).get("question_num"),
        "stress_trend": stress_result.get("stress_trend"),
        
        # Consistency metrics
        "consistency_score": consistency_result.get("consistency_score"),
        "inconsistency_count": consistency_result.get("inconsistency_count"),
        
        # Aggregates
        "mean_blink_rate": aggregates.get("blink_rate_mean"),
        "mean_pitch_variance": aggregates.get("pitch_variance_mean"),
        "mean_sentiment": aggregates.get("sentiment_polarity_mean"),
        "total_filler_count": aggregates.get("total_filler_count"),
        "total_word_count": aggregates.get("total_word_count"),
        
        # Entry count
        "question_count": session_export.get("entry_count"),
    }
