# =========================================================
# BEHAVIORAL CONSISTENCY DETECTION
# Detect cross-modal contradictions in behavioral signals
# =========================================================

from typing import Dict, List, Any, Optional, Union
import numpy as np


# =========================================================
# CONSISTENCY RULES
# Each rule defines expected correlations between modalities
# =========================================================
CONSISTENCY_RULES = [
    {
        "id": "calm_voice_unstable_gaze",
        "name": "Voice-Gaze Mismatch",
        "description": "Calm vocal patterns but unstable eye behavior",
        "conditions": {
            "pitch_variance": {"max": 40},  # Calm voice
            "blink_rate": {"min": 25},       # High blink rate
        },
        "severity": "moderate",
        "interpretation": "May indicate controlled speech masking internal stress"
    },
    {
        "id": "positive_sentiment_high_stress",
        "name": "Sentiment-Stress Contradiction",
        "description": "Positive verbal content with high physiological stress",
        "conditions": {
            "sentiment_polarity": {"min": 0.3},  # Positive sentiment
            "stress_score": {"min": 0.6},        # High stress
        },
        "severity": "high",
        "interpretation": "Verbal content may not reflect true emotional state"
    },
    {
        "id": "fluent_speech_high_filler",
        "name": "Speech Fluency Paradox",
        "description": "High energy speech with many filler words",
        "conditions": {
            "energy_variance": {"min": 0.03},  # High energy
            "filler_count": {"min": 5},         # Many fillers
        },
        "severity": "low",
        "interpretation": "May indicate rushed or anxious speech pattern"
    },
    {
        "id": "stable_gaze_volatile_voice",
        "name": "Visual-Vocal Dissociation",
        "description": "Stable eye contact but highly variable voice",
        "conditions": {
            "gaze_stability": {"min": 0.7},   # Stable gaze
            "pitch_variance": {"min": 80},     # Volatile pitch
        },
        "severity": "moderate",
        "interpretation": "May indicate deliberate focus while emotionally stressed"
    },
    {
        "id": "low_energy_high_blink",
        "name": "Energy-Alertness Mismatch",
        "description": "Low vocal energy with high blink frequency",
        "conditions": {
            "energy_variance": {"max": 0.01},  # Low energy
            "blink_rate": {"min": 30},          # High blinks
        },
        "severity": "moderate",
        "interpretation": "May indicate fatigue or disengagement while trying to stay alert"
    },
    {
        "id": "negative_content_calm_delivery",
        "name": "Content-Delivery Mismatch",
        "description": "Negative verbal content with calm physiological state",
        "conditions": {
            "sentiment_polarity": {"max": -0.2},  # Negative sentiment
            "pitch_variance": {"max": 30},         # Very calm
            "blink_rate": {"max": 15},             # Low blinks
        },
        "severity": "high",
        "interpretation": "Emotionally detached delivery of negative content"
    },
]


def check_rule(rule: Dict, metrics: Dict[str, float]) -> bool:
    """
    Check if a single rule's conditions are satisfied.
    
    Args:
        rule: Rule definition with conditions
        metrics: Dictionary of numeric signal values
        
    Returns:
        True if all conditions are met (inconsistency detected)
    """
    conditions = rule.get("conditions", {})
    
    for signal, bounds in conditions.items():
        if signal not in metrics or metrics[signal] is None:
            return False  # Can't evaluate without data
        
        value = metrics[signal]
        
        # Check min bound
        if "min" in bounds and value < bounds["min"]:
            return False
        
        # Check max bound
        if "max" in bounds and value > bounds["max"]:
            return False
    
    return True


def detect_inconsistencies(
    data: Any
) -> Dict[str, Any]:
    """
    Detect behavioral inconsistencies in multimodal signals.
    
    Accepts either:
    - A flat metrics dictionary for single analysis
    - A list of question data dictionaries for session analysis
    
    Args:
        data: Either a single metrics dict or list of question data
            Each question data should have:
            - question_num: Question number
            - metrics: Dictionary of signal values
            
    Returns:
        Dictionary containing:
            - details: List of detected inconsistencies with question info
            - inconsistency_count: Total count
            - consistency_score: 0-1 score (1 = fully consistent)
            - is_consistent: Boolean flag
    """
    # Handle list of questions
    if isinstance(data, list):
        all_details = []
        all_scores = []
        
        for item in data:
            if isinstance(item, dict):
                q_num = item.get("question_num", len(all_scores) + 1)
                metrics = item.get("metrics", item)  # Use item itself if no metrics key
                
                result = _detect_single_inconsistencies(metrics)
                all_scores.append(result["consistency_score"])
                
                # Add question number to each detected inconsistency
                for inc in result["inconsistencies"]:
                    all_details.append({
                        "question_num": q_num,
                        "rule": inc.get("id", "unknown"),
                        "name": inc.get("name", ""),
                        "severity": inc.get("severity", "low"),
                        "interpretation": inc.get("interpretation", "")
                    })
        
        if all_scores:
            avg_score = sum(all_scores) / len(all_scores)
        else:
            avg_score = 1.0
        
        return {
            "details": all_details,
            "inconsistency_count": len(all_details),
            "consistency_score": round(avg_score, 2),
            "is_consistent": len(all_details) == 0
        }
    
    # Handle single metrics dict (original behavior)
    result = _detect_single_inconsistencies(data)
    return {
        "details": [{
            "question_num": 1,
            "rule": inc.get("id", "unknown"),
            "name": inc.get("name", ""),
            "severity": inc.get("severity", "low"),
            "interpretation": inc.get("interpretation", "")
        } for inc in result["inconsistencies"]],
        "inconsistency_count": result["inconsistency_count"],
        "consistency_score": result["consistency_score"],
        "is_consistent": result["inconsistency_count"] == 0
    }


def _detect_single_inconsistencies(metrics: Dict[str, float]) -> Dict[str, Any]:
    """
    Detect behavioral inconsistencies in a single metrics dictionary.
    
    Args:
        metrics: Dictionary containing signal values
            
    Returns:
        Dictionary containing inconsistencies list and consistency score
    """
    if not isinstance(metrics, dict):
        return {
            "inconsistencies": [],
            "inconsistency_count": 0,
            "consistency_score": 1.0
        }
    
    detected = []
    
    for rule in CONSISTENCY_RULES:
        if check_rule(rule, metrics):
            detected.append({
                "id": rule["id"],
                "name": rule["name"],
                "description": rule["description"],
                "severity": rule["severity"],
                "interpretation": rule["interpretation"],
                "matching_signals": _get_matching_signals(rule, metrics)
            })
    
    # Calculate consistency score
    severity_weights = {"low": 0.1, "moderate": 0.2, "high": 0.3}
    penalty = sum(severity_weights.get(d["severity"], 0.1) for d in detected)
    consistency_score = max(0, 1 - penalty)
    
    return {
        "inconsistencies": detected,
        "inconsistency_count": len(detected),
        "consistency_score": round(consistency_score, 2)
    }


def _get_matching_signals(rule: Dict, metrics: Dict[str, float]) -> Dict[str, float]:
    """Get the actual values that matched the rule conditions."""
    matching = {}
    conditions = rule.get("conditions", {})
    
    for signal in conditions.keys():
        if signal in metrics:
            matching[signal] = metrics[signal]
    
    return matching


def _generate_summary(
    inconsistencies: List[Dict],
    consistency_score: float
) -> Dict[str, str]:
    """Generate human-readable summary of consistency analysis."""
    
    if not inconsistencies:
        return {
            "level": "Consistent",
            "color": "#10b981",
            "text": "All behavioral signals align well across modalities.",
            "recommendation": "No concerning cross-modal contradictions detected."
        }
    
    severity_counts = {"low": 0, "moderate": 0, "high": 0}
    for inc in inconsistencies:
        sev = inc.get("severity", "low")
        severity_counts[sev] += 1
    
    if severity_counts["high"] > 0:
        return {
            "level": "Significant Inconsistencies",
            "color": "#ef4444",
            "text": f"Detected {len(inconsistencies)} cross-modal contradiction(s), including {severity_counts['high']} high-severity pattern(s).",
            "recommendation": "Review high-severity inconsistencies for potential masking or stress indicators."
        }
    elif severity_counts["moderate"] > 0:
        return {
            "level": "Moderate Inconsistencies",
            "color": "#f59e0b",
            "text": f"Detected {len(inconsistencies)} behavioral inconsistency pattern(s) across modalities.",
            "recommendation": "Some signals don't align as expected; may indicate mixed emotional states."
        }
    else:
        return {
            "level": "Minor Inconsistencies",
            "color": "#22c55e",
            "text": f"Detected {len(inconsistencies)} minor inconsistency pattern(s).",
            "recommendation": "Minor variations are normal and don't indicate significant concerns."
        }


def analyze_session_consistency(
    question_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze behavioral consistency across entire session.
    
    Args:
        question_results: List of detect_inconsistencies results
        
    Returns:
        Session-level consistency analysis
    """
    all_inconsistencies = []
    consistency_scores = []
    
    for i, qr in enumerate(question_results):
        consistency_scores.append(qr.get("consistency_score", 1.0))
        
        for inc in qr.get("inconsistencies", []):
            inc_copy = inc.copy()
            inc_copy["question"] = i + 1
            all_inconsistencies.append(inc_copy)
    
    # Count recurring patterns
    pattern_counts = {}
    for inc in all_inconsistencies:
        pattern_id = inc["id"]
        if pattern_id not in pattern_counts:
            pattern_counts[pattern_id] = {
                "count": 0,
                "name": inc["name"],
                "severity": inc["severity"],
                "questions": []
            }
        pattern_counts[pattern_id]["count"] += 1
        pattern_counts[pattern_id]["questions"].append(inc["question"])
    
    # Sort by frequency
    recurring = sorted(
        pattern_counts.values(),
        key=lambda x: x["count"],
        reverse=True
    )
    
    avg_consistency = np.mean(consistency_scores) if consistency_scores else 1.0
    
    return {
        "session_consistency_score": round(avg_consistency, 2),
        "total_inconsistencies": len(all_inconsistencies),
        "recurring_patterns": recurring,
        "per_question_scores": [round(s, 2) for s in consistency_scores],
        "summary": _generate_summary(
            all_inconsistencies, 
            avg_consistency
        )
    }


def get_most_concerning_inconsistency(
    inconsistencies: List[Dict]
) -> Optional[Dict]:
    """
    Get the most concerning inconsistency from a list.
    Prioritizes high severity, then frequency.
    """
    if not inconsistencies:
        return None
    
    severity_order = {"high": 3, "moderate": 2, "low": 1}
    
    sorted_inc = sorted(
        inconsistencies,
        key=lambda x: severity_order.get(x.get("severity", "low"), 0),
        reverse=True
    )
    
    return sorted_inc[0]
