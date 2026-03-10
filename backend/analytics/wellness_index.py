# =========================================================
# MULTIMODAL WELLNESS INDEX
# Computes a 0-100 wellness score from multimodal signals
# =========================================================

from typing import Dict, Any, Tuple
import numpy as np


# =========================================================
# NORMALIZATION BOUNDS (based on research literature)
# =========================================================
SIGNAL_BOUNDS = {
    "blink_rate": {"min": 0, "max": 50, "optimal_low": 10, "optimal_high": 20},
    "gaze_stability": {"min": 0, "max": 1, "optimal_low": 0.7, "optimal_high": 1.0},
    "pitch_variance": {"min": 0, "max": 200, "optimal_low": 20, "optimal_high": 60},
    "energy_variance": {"min": 0, "max": 0.1, "optimal_low": 0.01, "optimal_high": 0.05},
    "filler_count": {"min": 0, "max": 20, "optimal_low": 0, "optimal_high": 3},
    "sentiment_polarity": {"min": -1, "max": 1, "optimal_low": 0.1, "optimal_high": 1.0},
}

# =========================================================
# SIGNAL WEIGHTS (sum = 1.0)
# Based on psychological research importance
# =========================================================
SIGNAL_WEIGHTS = {
    "blink_rate": 0.15,
    "gaze_stability": 0.15,
    "pitch_variance": 0.20,
    "energy_variance": 0.15,
    "filler_count": 0.15,
    "sentiment_polarity": 0.20,
}


def normalize(value: float, signal_type: str) -> float:
    """
    Normalize a signal value to 0-1 range based on optimal bounds.
    
    Values within optimal range → high score (close to 1)
    Values outside optimal range → lower score (towards 0)
    
    Args:
        value: Raw signal value
        signal_type: One of the keys in SIGNAL_BOUNDS
        
    Returns:
        Normalized score between 0 and 1
    """
    if signal_type not in SIGNAL_BOUNDS:
        return 0.5  # Default neutral score for unknown signals
    
    bounds = SIGNAL_BOUNDS[signal_type]
    min_val = bounds["min"]
    max_val = bounds["max"]
    opt_low = bounds["optimal_low"]
    opt_high = bounds["optimal_high"]
    
    # Clamp value to bounds
    value = max(min_val, min(max_val, value))
    
    # If within optimal range, return high score
    if opt_low <= value <= opt_high:
        return 1.0
    
    # Below optimal range
    if value < opt_low:
        if opt_low == min_val:
            return 1.0
        return value / opt_low
    
    # Above optimal range
    if value > opt_high:
        if opt_high == max_val:
            return 1.0
        # Inverse relationship: higher values = lower score
        remaining_range = max_val - opt_high
        excess = value - opt_high
        return max(0, 1.0 - (excess / remaining_range))
    
    return 0.5


def compute_wellness_score(metrics: Dict[str, float]) -> Dict[str, Any]:
    """
    Compute overall wellness score from multimodal signals.
    
    Args:
        metrics: Dictionary containing:
            - blink_rate: Blinks per minute
            - gaze_stability: 0-1 stability score
            - pitch_variance: Pitch variation in Hz
            - energy_variance: RMS energy variance
            - filler_count: Number of filler words
            - sentiment_polarity: -1 to 1 sentiment score
            
    Returns:
        Dictionary containing:
            - score: 0-100 wellness score
            - interpretation: Human-readable interpretation
            - component_scores: Individual signal contributions
            - confidence: Confidence level based on available signals
    """
    component_scores = {}
    weighted_sum = 0.0
    total_weight = 0.0
    available_signals = 0
    
    for signal, weight in SIGNAL_WEIGHTS.items():
        if signal in metrics and metrics[signal] is not None:
            normalized = normalize(metrics[signal], signal)
            component_scores[signal] = {
                "raw_value": metrics[signal],
                "normalized": round(normalized, 3),
                "contribution": round(normalized * weight * 100, 2)
            }
            weighted_sum += normalized * weight
            total_weight += weight
            available_signals += 1
    
    # Calculate final score (0-100)
    if total_weight > 0:
        raw_score = (weighted_sum / total_weight) * 100
    else:
        raw_score = 50.0  # Default neutral score
    
    score = round(raw_score, 1)
    
    # Calculate confidence based on available signals
    confidence = available_signals / len(SIGNAL_WEIGHTS)
    
    # Generate interpretation
    interpretation = _get_interpretation(score)
    
    return {
        "score": score,
        "interpretation": interpretation,
        "component_scores": component_scores,
        "confidence": round(confidence, 2),
        "available_signals": available_signals,
        "total_signals": len(SIGNAL_WEIGHTS)
    }


def _get_interpretation(score: float) -> Dict[str, str]:
    """
    Generate human-readable interpretation of wellness score.
    """
    if score >= 85:
        return {
            "level": "Excellent",
            "color": "#10b981",
            "summary": "Strong emotional stability and confident communication",
            "detail": "All behavioral signals indicate calm, focused, and well-regulated responses."
        }
    elif score >= 70:
        return {
            "level": "Good",
            "color": "#22c55e",
            "summary": "Positive emotional state with minor variations",
            "detail": "Overall stable patterns with occasional mild stress indicators."
        }
    elif score >= 55:
        return {
            "level": "Moderate",
            "color": "#f59e0b",
            "summary": "Mixed signals suggesting moderate stress",
            "detail": "Some behavioral indicators suggest heightened cognitive load or mild anxiety."
        }
    elif score >= 40:
        return {
            "level": "Elevated Concern",
            "color": "#f97316",
            "summary": "Multiple stress indicators detected",
            "detail": "Several signals suggest significant stress or discomfort. Consider supportive follow-up."
        }
    else:
        return {
            "level": "High Concern",
            "color": "#ef4444",
            "summary": "Strong stress indicators across modalities",
            "detail": "Multiple signals indicate high stress levels. Recommend supportive intervention."
        }


def aggregate_session_wellness(question_scores: list) -> Dict[str, Any]:
    """
    Aggregate wellness scores across all questions in a session.
    
    Args:
        question_scores: List of wellness score dictionaries
        
    Returns:
        Aggregated session wellness metrics
    """
    if not question_scores:
        return compute_wellness_score({})
    
    scores = [q.get("score", 50) for q in question_scores]
    
    return {
        "session_score": round(np.mean(scores), 1),
        "min_score": round(min(scores), 1),
        "max_score": round(max(scores), 1),
        "score_variance": round(np.var(scores), 2),
        "interpretation": _get_interpretation(np.mean(scores)),
        "question_scores": scores
    }
