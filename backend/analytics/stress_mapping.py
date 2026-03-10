# =========================================================
# QUESTION STRESS MAPPING
# Compute stress level per question for identifying
# high-stress topics and peak stress moments
# =========================================================

from typing import Dict, List, Any, Optional
import numpy as np


# =========================================================
# STRESS SIGNAL WEIGHTS
# Based on psychophysiological research
# =========================================================
STRESS_WEIGHTS = {
    "pitch_variance": 0.25,
    "blink_rate": 0.20,
    "filler_count": 0.20,
    "pause_duration": 0.15,
    "energy_variance": 0.10,
    "sentiment_polarity": 0.10,  # Negative sentiment = stress
}

# =========================================================
# NORMALIZATION THRESHOLDS FOR STRESS
# Higher raw values = higher stress (except sentiment)
# =========================================================
STRESS_THRESHOLDS = {
    "pitch_variance": {"low": 20, "high": 100},
    "blink_rate": {"low": 10, "high": 40},
    "filler_count": {"low": 1, "high": 10},
    "pause_duration": {"low": 0.5, "high": 3.0},
    "energy_variance": {"low": 0.01, "high": 0.08},
    "sentiment_polarity": {"low": -1, "high": 1},  # Inverted
}


def _normalize_stress_signal(value: float, signal_type: str) -> float:
    """
    Normalize a signal to a 0-1 stress scale.
    Higher value = higher stress.
    """
    if signal_type not in STRESS_THRESHOLDS:
        return 0.5
    
    thresholds = STRESS_THRESHOLDS[signal_type]
    low = thresholds["low"]
    high = thresholds["high"]
    
    # Special handling for sentiment (inverted relationship)
    if signal_type == "sentiment_polarity":
        # -1 (very negative) → 1.0 stress
        # +1 (very positive) → 0.0 stress
        normalized = (1 - value) / 2
        return max(0, min(1, normalized))
    
    # Clamp and normalize
    if value <= low:
        return 0.0
    elif value >= high:
        return 1.0
    else:
        return (value - low) / (high - low)


def compute_question_stress(metrics: Dict[str, float]) -> Dict[str, Any]:
    """
    Compute stress score for a single question.
    
    Args:
        metrics: Dictionary containing signal values:
            - pitch_variance
            - blink_rate
            - filler_count
            - pause_duration
            - energy_variance
            - sentiment_polarity
            
    Returns:
        Dictionary with stress score and breakdown
    """
    stress_components = {}
    weighted_sum = 0.0
    total_weight = 0.0
    
    for signal, weight in STRESS_WEIGHTS.items():
        if signal in metrics and metrics[signal] is not None:
            normalized = _normalize_stress_signal(metrics[signal], signal)
            stress_components[signal] = {
                "raw_value": metrics[signal],
                "normalized_stress": round(normalized, 3),
                "weighted_contribution": round(normalized * weight, 4)
            }
            weighted_sum += normalized * weight
            total_weight += weight
    
    # Calculate final stress score (0-1)
    if total_weight > 0:
        stress_score = weighted_sum / total_weight
    else:
        stress_score = 0.0
    
    # Get stress level label
    level = _get_stress_level(stress_score)
    
    return {
        "stress_score": round(stress_score, 3),
        "stress_percent": round(stress_score * 100, 1),
        "level": level,
        "components": stress_components
    }


def _get_stress_level(score: float) -> Dict[str, str]:
    """Get human-readable stress level."""
    if score < 0.2:
        return {"label": "Relaxed", "color": "#10b981"}
    elif score < 0.4:
        return {"label": "Mild", "color": "#22c55e"}
    elif score < 0.6:
        return {"label": "Moderate", "color": "#f59e0b"}
    elif score < 0.8:
        return {"label": "Elevated", "color": "#f97316"}
    else:
        return {"label": "High", "color": "#ef4444"}


def compute_stress_map(questions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute stress map across all questions in a session.
    
    Args:
        questions_data: List of dictionaries, each containing:
            - question_num: Question number
            - metrics: Signal values dictionary
            
    Returns:
        Dictionary containing:
            - stress_map: List of per-question stress data
            - peak_stress_question: Question with highest stress
            - average_stress: Session average stress
            - stress_trend: Increasing/Decreasing/Stable
    """
    stress_map = []
    
    for q_data in questions_data:
        question_num = q_data.get("question_num", len(stress_map) + 1)
        metrics = q_data.get("metrics", {})
        
        stress_result = compute_question_stress(metrics)
        stress_result["question_num"] = question_num
        stress_result["question_text"] = q_data.get("question_text", f"Question {question_num}")
        
        stress_map.append(stress_result)
    
    if not stress_map:
        return {
            "stress_map": [],
            "peak_stress_question": None,
            "average_stress": 0,
            "stress_trend": "unknown"
        }
    
    # Find peak stress question
    peak_idx = max(range(len(stress_map)), key=lambda i: stress_map[i]["stress_score"])
    peak_stress_question = {
        "question_num": stress_map[peak_idx]["question_num"],
        "stress_score": stress_map[peak_idx]["stress_score"],
        "stress_percent": stress_map[peak_idx]["stress_percent"],
        "level": stress_map[peak_idx]["level"]
    }
    
    # Calculate average stress
    avg_stress = np.mean([s["stress_score"] for s in stress_map])
    
    # Determine trend
    stress_trend = _calculate_stress_trend([s["stress_score"] for s in stress_map])
    
    return {
        "stress_map": stress_map,
        "peak_stress_question": peak_stress_question,
        "average_stress": round(avg_stress, 3),
        "average_stress_percent": round(avg_stress * 100, 1),
        "stress_trend": stress_trend
    }


def get_peak_stress_question(stress_map_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract peak stress question from stress map result.
    
    Args:
        stress_map_result: Result from compute_stress_map()
        
    Returns:
        Peak stress question data or None
    """
    return stress_map_result.get("peak_stress_question")


def _calculate_stress_trend(stress_scores: List[float]) -> str:
    """
    Determine if stress is increasing, decreasing, or stable.
    Uses simple linear regression slope.
    """
    if len(stress_scores) < 2:
        return "insufficient_data"
    
    x = np.arange(len(stress_scores))
    y = np.array(stress_scores)
    
    # Calculate slope using least squares
    n = len(x)
    slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2 + 1e-10)
    
    if slope > 0.05:
        return "increasing"
    elif slope < -0.05:
        return "decreasing"
    else:
        return "stable"
