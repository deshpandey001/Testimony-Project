# =========================================================
# EMOTIONAL TREND GRAPH
# Detect stress variations across time windows in response
# Uses pitch + energy signals for temporal analysis
# =========================================================

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import os


def compute_emotional_timeline(
    metrics_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Compute emotional stress timeline from pre-computed metrics.
    
    Each item represents one question/segment with its metrics.
    
    Args:
        metrics_list: List of metric dictionaries per question, each containing:
            - pitch_variance
            - energy_variance
            - blink_rate
            - sentiment_polarity
            - filler_count
            
    Returns:
        List of timeline points with stress_index, energy_level, dominant_state
    """
    if not metrics_list:
        return []
    
    timeline = []
    
    for idx, metrics in enumerate(metrics_list):
        if not metrics or not isinstance(metrics, dict):
            timeline.append({
                "segment": idx + 1,
                "stress_index": 0.5,
                "energy_level": 0.5,
                "dominant_state": "neutral"
            })
            continue
        
        # Compute stress index from available metrics
        stress_index = _compute_stress_from_metrics(metrics)
        
        # Compute energy level
        energy_level = _compute_energy_level(metrics)
        
        # Determine dominant emotional state
        dominant_state = _determine_emotional_state(stress_index, energy_level)
        
        timeline.append({
            "segment": idx + 1,
            "stress_index": round(stress_index, 3),
            "energy_level": round(energy_level, 3),
            "dominant_state": dominant_state,
            "pitch_variance": metrics.get("pitch_variance"),
            "blink_rate": metrics.get("blink_rate")
        })
    
    return timeline


def _compute_stress_from_metrics(metrics: Dict[str, Any]) -> float:
    """Compute stress index 0-1 from metrics."""
    stress_signals = []
    
    # Pitch variance contribution (higher = more stress)
    pitch_var = metrics.get("pitch_variance")
    if pitch_var is not None:
        normalized_pitch = min(1.0, pitch_var / 100.0)
        stress_signals.append(normalized_pitch * 0.30)
    
    # Blink rate contribution (high or very low = stress)
    blink_rate = metrics.get("blink_rate")
    if blink_rate is not None:
        # Optimal range 10-20, stress increases outside this
        if blink_rate < 10:
            normalized_blink = (10 - blink_rate) / 10
        elif blink_rate > 25:
            normalized_blink = min(1.0, (blink_rate - 25) / 25)
        else:
            normalized_blink = 0.0
        stress_signals.append(normalized_blink * 0.20)
    
    # Filler count contribution
    filler_count = metrics.get("filler_count")
    if filler_count is not None:
        normalized_filler = min(1.0, filler_count / 10.0)
        stress_signals.append(normalized_filler * 0.20)
    
    # Energy variance contribution
    energy_var = metrics.get("energy_variance")
    if energy_var is not None:
        normalized_energy = min(1.0, energy_var / 0.05)
        stress_signals.append(normalized_energy * 0.15)
    
    # Sentiment (negative = stress)
    sentiment = metrics.get("sentiment_polarity")
    if sentiment is not None:
        # Convert -1 to 1 range to 0-1 stress (negative = high stress)
        normalized_sentiment = (1 - sentiment) / 2
        stress_signals.append(normalized_sentiment * 0.15)
    
    if not stress_signals:
        return 0.5  # Default neutral
    
    # Sum weighted signals
    total_stress = sum(stress_signals)
    # Normalize by maximum possible (sum of weights used)
    return min(1.0, total_stress)


def _compute_energy_level(metrics: Dict[str, Any]) -> float:
    """Compute energy level 0-1 from metrics."""
    energy_signals = []
    
    # Energy variance (higher = more energy)
    energy_var = metrics.get("energy_variance")
    if energy_var is not None:
        normalized = min(1.0, energy_var / 0.03)
        energy_signals.append(normalized)
    
    # Pitch variance also indicates energy
    pitch_var = metrics.get("pitch_variance")
    if pitch_var is not None:
        normalized = min(1.0, pitch_var / 80.0)
        energy_signals.append(normalized)
    
    # Blink rate can indicate alertness
    blink_rate = metrics.get("blink_rate")
    if blink_rate is not None:
        # High blink = alertness
        normalized = min(1.0, blink_rate / 30.0)
        energy_signals.append(normalized)
    
    if not energy_signals:
        return 0.5
    
    return sum(energy_signals) / len(energy_signals)


def _determine_emotional_state(stress: float, energy: float) -> str:
    """
    Determine dominant emotional state from stress and energy.
    
    Based on circumplex model of affect:
    - High stress + High energy = "stressed"
    - High stress + Low energy = "anxious"
    - Low stress + High energy = "excited"
    - Low stress + Low energy = "calm"
    """
    if stress >= 0.6:
        if energy >= 0.5:
            return "stressed"
        else:
            return "anxious"
    elif stress <= 0.4:
        if energy >= 0.5:
            return "excited"
        else:
            return "calm"
    else:
        return "neutral"


def compute_emotional_timeline_from_audio(
    audio_path: str,
    window_size: float = 1.0,
    hop_size: float = 0.5,
    sr: int = 16000
) -> Dict[str, Any]:
    """
    Compute emotional stress timeline from audio signal.
    
    Analyzes pitch and energy variations in sliding windows
    to create a time-series of emotional intensity.
    
    Args:
        audio_path: Path to audio file
        window_size: Window size in seconds
        hop_size: Hop size in seconds
        sr: Sample rate
        
    Returns:
        Dictionary containing:
            - timeline: List of {time, stress, energy, pitch} points
            - peak_moments: Times of highest stress
            - overall_pattern: Description of emotional pattern
    """
    try:
        import librosa
    except ImportError:
        return _empty_timeline("librosa not available")
    
    if not audio_path or not os.path.exists(audio_path):
        return _empty_timeline("No audio file provided")
    
    try:
        # Load audio
        y, loaded_sr = librosa.load(audio_path, sr=sr)
        duration = len(y) / sr
        
        if duration < window_size:
            return _empty_timeline("Audio too short for analysis")
        
        # Convert to samples
        window_samples = int(window_size * sr)
        hop_samples = int(hop_size * sr)
        
        timeline = []
        times = []
        stress_values = []
        
        # Sliding window analysis
        for start in range(0, len(y) - window_samples, hop_samples):
            end = start + window_samples
            window = y[start:end]
            time_sec = start / sr
            
            # Compute features for this window
            features = _compute_window_features(window, sr)
            
            # Compute stress score for window
            stress = _compute_window_stress(features)
            
            timeline.append({
                "time": round(time_sec, 2),
                "stress": round(stress, 3),
                "energy": round(features.get("energy", 0), 4),
                "pitch_mean": round(features.get("pitch_mean", 0), 2),
                "pitch_var": round(features.get("pitch_var", 0), 2)
            })
            
            times.append(time_sec)
            stress_values.append(stress)
        
        if not timeline:
            return _empty_timeline("No windows computed")
        
        # Find peak moments (local maxima above threshold)
        peak_moments = _find_peak_moments(times, stress_values)
        
        # Analyze overall pattern
        overall_pattern = _analyze_pattern(stress_values)
        
        # Compute statistics
        stats = {
            "max_stress": round(max(stress_values), 3),
            "min_stress": round(min(stress_values), 3),
            "mean_stress": round(np.mean(stress_values), 3),
            "stress_range": round(max(stress_values) - min(stress_values), 3),
            "duration_seconds": round(duration, 2)
        }
        
        return {
            "timeline": timeline,
            "peak_moments": peak_moments,
            "overall_pattern": overall_pattern,
            "statistics": stats,
            "window_size": window_size,
            "hop_size": hop_size
        }
        
    except Exception as e:
        return _empty_timeline(f"Analysis error: {str(e)}")


def _compute_window_features(window: np.ndarray, sr: int) -> Dict[str, float]:
    """
    Compute audio features for a single window.
    """
    import librosa
    
    features = {}
    
    try:
        # Energy (RMS)
        rms = librosa.feature.rms(y=window)[0]
        features["energy"] = float(np.mean(rms))
        features["energy_var"] = float(np.var(rms))
        
        # Pitch tracking
        pitches, magnitudes = librosa.piptrack(y=window, sr=sr)
        pitch_vals = pitches[magnitudes > np.median(magnitudes)]
        pitch_vals = pitch_vals[pitch_vals > 0]  # Filter zero pitches
        
        if len(pitch_vals) > 0:
            features["pitch_mean"] = float(np.mean(pitch_vals))
            features["pitch_var"] = float(np.var(pitch_vals))
            features["pitch_max"] = float(np.max(pitch_vals))
            features["pitch_min"] = float(np.min(pitch_vals))
        else:
            features["pitch_mean"] = 0.0
            features["pitch_var"] = 0.0
            features["pitch_max"] = 0.0
            features["pitch_min"] = 0.0
        
        # Zero crossing rate (relates to speech intensity)
        zcr = librosa.feature.zero_crossing_rate(window)[0]
        features["zcr"] = float(np.mean(zcr))
        
    except Exception:
        features = {
            "energy": 0.0,
            "energy_var": 0.0,
            "pitch_mean": 0.0,
            "pitch_var": 0.0,
            "pitch_max": 0.0,
            "pitch_min": 0.0,
            "zcr": 0.0
        }
    
    return features


def _compute_window_stress(features: Dict[str, float]) -> float:
    """
    Compute stress score for a window based on features.
    
    Higher pitch variance + higher energy = higher stress
    """
    # Normalize pitch variance (typical range 0-200)
    pitch_var = features.get("pitch_var", 0)
    norm_pitch = min(1.0, pitch_var / 100)
    
    # Normalize energy (typical range 0-0.1)
    energy = features.get("energy", 0)
    norm_energy = min(1.0, energy / 0.05)
    
    # Normalize energy variance
    energy_var = features.get("energy_var", 0)
    norm_energy_var = min(1.0, energy_var / 0.01)
    
    # ZCR contribution (higher = more fricatives/stress)
    zcr = features.get("zcr", 0)
    norm_zcr = min(1.0, zcr / 0.2)
    
    # Weighted combination
    stress = (
        0.35 * norm_pitch +
        0.25 * norm_energy +
        0.25 * norm_energy_var +
        0.15 * norm_zcr
    )
    
    return max(0, min(1, stress))


def _find_peak_moments(
    times: List[float],
    stress_values: List[float],
    threshold: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Find moments of peak stress (local maxima above threshold).
    """
    peaks = []
    
    if len(stress_values) < 3:
        if stress_values and max(stress_values) > threshold:
            idx = stress_values.index(max(stress_values))
            peaks.append({
                "time": times[idx],
                "stress": stress_values[idx],
                "label": "Peak stress moment"
            })
        return peaks
    
    for i in range(1, len(stress_values) - 1):
        # Check if local maximum
        if (stress_values[i] > stress_values[i-1] and 
            stress_values[i] > stress_values[i+1] and
            stress_values[i] > threshold):
            
            peaks.append({
                "time": round(times[i], 2),
                "stress": round(stress_values[i], 3),
                "label": f"Stress peak at {round(times[i], 1)}s"
            })
    
    # Sort by stress level and keep top 3
    peaks.sort(key=lambda x: x["stress"], reverse=True)
    return peaks[:3]


def _analyze_pattern(stress_values: List[float]) -> Dict[str, str]:
    """
    Analyze overall emotional pattern from stress timeline.
    """
    if len(stress_values) < 2:
        return {
            "type": "insufficient_data",
            "description": "Not enough data points for pattern analysis"
        }
    
    mean_stress = np.mean(stress_values)
    stress_range = max(stress_values) - min(stress_values)
    
    # Check for trend
    first_half = np.mean(stress_values[:len(stress_values)//2])
    second_half = np.mean(stress_values[len(stress_values)//2:])
    trend_diff = second_half - first_half
    
    # Determine pattern type
    if stress_range < 0.15:
        pattern_type = "stable"
        description = "Consistent emotional state throughout"
    elif trend_diff > 0.15:
        pattern_type = "escalating"
        description = "Stress increases over the response duration"
    elif trend_diff < -0.15:
        pattern_type = "calming"
        description = "Stress decreases, possibly indicating comfort or resolution"
    elif stress_range > 0.4:
        pattern_type = "volatile"
        description = "High emotional variability with significant stress fluctuations"
    else:
        pattern_type = "fluctuating"
        description = "Moderate emotional variations during response"
    
    return {
        "type": pattern_type,
        "description": description,
        "mean_stress": round(mean_stress, 3),
        "variability": round(stress_range, 3)
    }


def _empty_timeline(reason: str) -> Dict[str, Any]:
    """Return empty timeline structure with reason."""
    return {
        "timeline": [],
        "peak_moments": [],
        "overall_pattern": {
            "type": "unavailable",
            "description": reason
        },
        "statistics": {
            "max_stress": 0,
            "min_stress": 0,
            "mean_stress": 0,
            "stress_range": 0,
            "duration_seconds": 0
        },
        "error": reason
    }


def aggregate_session_timeline(question_timelines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate emotional timelines across all questions.
    
    Args:
        question_timelines: List of timeline results from compute_emotional_timeline
        
    Returns:
        Session-level emotional analysis
    """
    all_stress = []
    all_patterns = []
    total_peaks = []
    
    for i, qt in enumerate(question_timelines):
        # Collect stress values
        for point in qt.get("timeline", []):
            all_stress.append(point.get("stress", 0))
        
        # Collect patterns
        pattern = qt.get("overall_pattern", {}).get("type", "unknown")
        all_patterns.append(pattern)
        
        # Collect peaks with question context
        for peak in qt.get("peak_moments", []):
            peak_copy = peak.copy()
            peak_copy["question"] = i + 1
            total_peaks.append(peak_copy)
    
    # Sort all peaks by stress level
    total_peaks.sort(key=lambda x: x.get("stress", 0), reverse=True)
    
    # Determine dominant pattern
    from collections import Counter
    pattern_counts = Counter(all_patterns)
    dominant_pattern = pattern_counts.most_common(1)[0][0] if pattern_counts else "unknown"
    
    return {
        "session_mean_stress": round(np.mean(all_stress), 3) if all_stress else 0,
        "session_max_stress": round(max(all_stress), 3) if all_stress else 0,
        "top_stress_peaks": total_peaks[:5],
        "dominant_pattern": dominant_pattern,
        "pattern_distribution": dict(pattern_counts)
    }
