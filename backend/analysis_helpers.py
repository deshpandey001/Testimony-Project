# =========================================================
# PSYCHOLOGICAL WELLNESS ANALYSIS HELPERS
# (Student / Educational / HR safe domain)
# =========================================================

import os
import warnings
import subprocess
import shutil
import asyncio
import tempfile
import logging

logger = logging.getLogger(__name__)

# Lazy imports for heavy dependencies
cv2 = None
np = None
mp = None
librosa = None
genai = None
mp_face_mesh = None

def _init_cv2():
    global cv2
    if cv2 is None:
        import cv2 as cv2_module
        cv2 = cv2_module
    return cv2

def _init_numpy():
    global np
    if np is None:
        import numpy as np_module
        np = np_module
    return np

def _init_mediapipe():
    global mp, mp_face_mesh
    if mp is None:
        import mediapipe as mp_module
        mp = mp_module
        try:
            mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1
            )
            logger.info("✅ MediaPipe initialized")
        except Exception as e:
            logger.warning(f"⚠️ MediaPipe init failed: {e}")
    return mp_face_mesh

def _init_librosa():
    global librosa
    if librosa is None:
        import librosa as librosa_module
        librosa = librosa_module
    return librosa

def _init_gemini():
    global genai
    if genai is None:
        try:
            import google.generativeai as genai_module
            genai = genai_module
        except Exception:
            logger.warning("⚠️ google.generativeai not available")
    return genai

from textblob import TextBlob

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
logger.info("✅ analysis_helpers module loaded")

# =========================================================
# ---------------- FACIAL WELLNESS ------------------------
# =========================================================

def calculate_ear(eye):
    """Eye Aspect Ratio (EAR)"""
    np_module = _init_numpy()
    A = np_module.linalg.norm(np_module.array(eye[1]) - np_module.array(eye[5]))
    B = np_module.linalg.norm(np_module.array(eye[2]) - np_module.array(eye[4]))
    C = np_module.linalg.norm(np_module.array(eye[0]) - np_module.array(eye[3]))
    return (A + B) / (2.0 * C + 1e-6)


def extract_facial_metrics(frames, duration_sec=60):
    """
    Extract numeric facial metrics for analytics.

    RETURNS:
        Dict with:
            - blink_rate: blinks per minute
            - gaze_stability: 0-1 stability score
            - face_detected_ratio: frames with face / total frames
    """
    # Initialize on first use
    cv2_module = _init_cv2()
    np_module = _init_numpy()
    mesh = _init_mediapipe()
    
    if mesh is None:
        logger.warning("MediaPipe not available, returning empty metrics")
        return {
            "blink_rate": None,
            "gaze_stability": None,
            "face_detected_ratio": 0.0
        }
    
    if not frames or len(frames) < 2:
        return {
            "blink_rate": None,
            "gaze_stability": None,
            "face_detected_ratio": 0.0
        }

    blink_count = 0
    eye_closed = False
    EAR_THRESHOLD = 0.22
    face_detected = 0
    ear_values = []

    for frame in frames:
        try:
            rgb = cv2_module.cvtColor(frame, cv2_module.COLOR_BGR2RGB)
            results = mesh.process(rgb)

            if results.multi_face_landmarks:
                face_detected += 1
                for face in results.multi_face_landmarks:
                    lm = face.landmark

                    left_eye = [(lm[i].x, lm[i].y) for i in [362, 385, 387, 263, 373, 380]]
                    right_eye = [(lm[i].x, lm[i].y) for i in [33, 160, 158, 133, 153, 144]]

                    ear = (calculate_ear(left_eye) + calculate_ear(right_eye)) / 2
                    ear_values.append(ear)

                    if ear < EAR_THRESHOLD:
                        if not eye_closed:
                            blink_count += 1
                            eye_closed = True
                    else:
                        eye_closed = False
        except Exception:
            continue

    # Calculate metrics
    blink_rate = (blink_count / duration_sec) * 60 if duration_sec > 0 else blink_count
    
    # Gaze stability: inverse of EAR variance (normalized)
    if ear_values:
        ear_var = np.var(ear_values)
        gaze_stability = max(0, 1 - min(ear_var * 10, 1))  # Normalize to 0-1
    else:
        gaze_stability = None

    face_ratio = face_detected / len(frames) if frames else 0.0

    return {
        "blink_rate": round(blink_rate, 2),
        "gaze_stability": round(gaze_stability, 4) if gaze_stability else None,
        "face_detected_ratio": round(face_ratio, 4),
        "raw_blink_count": blink_count
    }


def analyze_facial_features(frames):
    """
    Facial behavioral wellness indicators.

    RETURNS (ALWAYS):
        List[Dict] → wellness indicators
    """
    # Initialize on first use
    cv2_module = _init_cv2()
    mesh = _init_mediapipe()

    metrics = []

    if not frames or len(frames) < 2:
        return [{
            "type": "Facial Data Unavailable",
            "value": None,
            "details": "Insufficient video frames for facial analysis"
        }]

    if mesh is None:
        logger.warning("MediaPipe not available for facial analysis")
        return [{
            "type": "Facial Analysis Unavailable",
            "value": None,
            "details": "MediaPipe not available in this environment"
        }]

    blink_count = 0
    eye_closed = False
    EAR_THRESHOLD = 0.22

    for frame in frames:
        try:
            rgb = cv2_module.cvtColor(frame, cv2_module.COLOR_BGR2RGB)
            results = mesh.process(rgb)

            if results.multi_face_landmarks:
                for face in results.multi_face_landmarks:
                    lm = face.landmark

                    left_eye = [(lm[i].x, lm[i].y) for i in [362, 385, 387, 263, 373, 380]]
                    right_eye = [(lm[i].x, lm[i].y) for i in [33, 160, 158, 133, 153, 144]]

                    ear = (calculate_ear(left_eye) + calculate_ear(right_eye)) / 2

                    if ear < EAR_THRESHOLD:
                        if not eye_closed:
                            blink_count += 1
                            eye_closed = True
                    else:
                        eye_closed = False
        except Exception:
            continue

    if blink_count > 25:
        metrics.append({
            "type": "High Blink Frequency",
            "value": blink_count,
            "details": "May indicate fatigue, stress, or cognitive load"
        })
    else:
        metrics.append({
            "type": "Stable Eye Engagement",
            "value": blink_count,
            "details": "Indicates sustained attention and focus"
        })

    return metrics


# =========================================================
# ---------------- VOCAL WELLNESS -------------------------
# =========================================================

def _ensure_wav(audio_path):
    """Convert non-WAV audio to WAV using ffmpeg if available."""
    if not audio_path or not os.path.exists(audio_path):
        return None

    ext = os.path.splitext(audio_path)[1].lower()
    if ext == ".wav":
        return audio_path

    if shutil.which("ffmpeg") is None:
        return audio_path

    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    cmd = [
        "ffmpeg", "-y", "-i", audio_path,
        "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", tmp
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return tmp
    except Exception:
        return audio_path


def extract_vocal_metrics(audio_path):
    """
    Extract numeric vocal metrics for analytics.

    RETURNS:
        Dict with:
            - pitch_variance: variance of pitch values
            - energy_variance: variance of RMS energy
            - duration_sec: audio duration in seconds
            - pause_duration: estimated pause time in seconds
    """
    # Initialize on first use
    librosa_module = _init_librosa()
    np_module = _init_numpy()
    
    if librosa_module is None or np_module is None:
        return {
            "pitch_variance": None,
            "energy_variance": None,
            "duration_sec": None,
            "pause_duration": None,
            "error": "librosa not available"
        }
    
    if not audio_path or not os.path.exists(audio_path):
        return {
            "pitch_variance": None,
            "energy_variance": None,
            "duration_sec": None,
            "pause_duration": None
        }

    safe_path = _ensure_wav(audio_path)

    try:
        y, sr = librosa_module.load(safe_path, sr=16000)
        duration = len(y) / sr

        # Energy analysis
        rms = librosa_module.feature.rms(y=y)
        energy_var = float(np_module.var(rms))

        # Pitch analysis
        pitches, mags = librosa_module.piptrack(y=y, sr=sr)
        pitch_vals = pitches[mags > np_module.median(mags)]
        pitch_var = float(np_module.var(pitch_vals)) if len(pitch_vals) else 0.0

        # Pause detection (frames with very low energy)
        rms_flat = rms.flatten()
        silence_threshold = np_module.percentile(rms_flat, 20)  # Bottom 20% as pause
        pause_frames = np_module.sum(rms_flat < silence_threshold)
        hop_length = 512  # librosa default
        pause_duration = (pause_frames * hop_length) / sr

        return {
            "pitch_variance": round(pitch_var, 4),
            "energy_variance": round(energy_var, 6),
            "duration_sec": round(duration, 2),
            "pause_duration": round(pause_duration, 2)
        }

    except Exception as e:
        return {
            "pitch_variance": None,
            "energy_variance": None,
            "duration_sec": None,
            "pause_duration": None,
            "error": str(e)
        }

    finally:
        if safe_path and safe_path != audio_path and os.path.exists(safe_path):
            try:
                os.remove(safe_path)
            except Exception:
                pass


def analyze_vocal_features(audio_path):
    """
    Vocal wellness indicators.

    RETURNS (ALWAYS):
        List[Dict]
    """
    # Initialize on first use
    librosa_module = _init_librosa()
    np_module = _init_numpy()

    metrics = []

    if not audio_path or not os.path.exists(audio_path):
        return [{
            "type": "Audio Data Unavailable",
            "value": None,
            "details": "No valid audio input for vocal analysis"
        }]

    if librosa_module is None or np_module is None:
        return [{
            "type": "Audio Analysis Unavailable",
            "value": None,
            "details": "librosa not available in this environment"
        }]

    safe_path = _ensure_wav(audio_path)

    try:
        y, sr = librosa_module.load(safe_path, sr=16000)

        rms = librosa_module.feature.rms(y=y)
        energy_var = float(np_module.var(rms))

        pitches, mags = librosa_module.piptrack(y=y, sr=sr)
        pitch_vals = pitches[mags > np_module.median(mags)]
        pitch_var = float(np_module.var(pitch_vals)) if len(pitch_vals) else 0.0

        if pitch_var > 60:
            metrics.append({
                "type": "Voice Variability",
                "value": round(pitch_var, 2),
                "details": "May reflect emotional excitement or stress"
            })
        else:
            metrics.append({
                "type": "Stable Voice Pattern",
                "value": round(pitch_var, 2),
                "details": "Calm and controlled speech delivery"
            })

    except Exception as e:
        metrics.append({
            "type": "Vocal Analysis Error",
            "value": None,
            "details": str(e)
        })

    finally:
        if safe_path and safe_path != audio_path and os.path.exists(safe_path):
            try:
                os.remove(safe_path)
            except Exception:
                pass

    return metrics


# =========================================================
# ---------------- GEMINI ASR -----------------------------
# =========================================================

async def transcribe_audio(audio_path):
    """
    Speech-to-text using Gemini.

    RETURNS:
        str (never raises)
    """

    if not audio_path or not os.path.exists(audio_path):
        return "[No audio provided]"

    if not GEMINI_API_KEY or genai is None:
        return "[Speech-to-text unavailable]"

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        response = await model.generate_content_async(
            [
                {"mime_type": "audio/wav", "data": audio_bytes},
                "Transcribe the spoken content verbatim. Output plain text only."
            ]
        )

        return response.text.strip() if response and response.text else ""

    except Exception as e:
        return f"[ASR error: {e}]"


# =========================================================
# ---------------- TEXT WELLNESS --------------------------
# =========================================================

def extract_text_metrics(text):
    """
    Extract numeric text metrics for analytics.

    RETURNS:
        Dict with:
            - filler_count: number of filler words
            - sentiment_polarity: -1 to 1 sentiment score
            - word_count: total words
            - sentence_count: total sentences
    """
    if not text:
        return {
            "filler_count": 0,
            "sentiment_polarity": 0.0,
            "word_count": 0,
            "sentence_count": 0
        }

    text_lower = text.lower()

    # Filler word count
    fillers = [
        "um", "uh", "like", "you know", "i mean",
        "sort of", "kind of", "basically", "actually"
    ]
    filler_count = sum(text_lower.count(f) for f in fillers)

    # Sentiment analysis
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  # -1 to 1

    # Word and sentence count
    words = text.split()
    word_count = len(words)
    sentence_count = len(blob.sentences)

    return {
        "filler_count": filler_count,
        "sentiment_polarity": round(sentiment, 4),
        "word_count": word_count,
        "sentence_count": sentence_count
    }


def analyze_text(text):
    """
    Counts filler words to estimate hesitation.

    RETURNS:
        int
    """

    if not text:
        return 0

    text = text.lower()

    fillers = [
        "um", "uh", "like", "you know", "i mean",
        "sort of", "kind of", "basically", "actually"
    ]

    count = 0
    for f in fillers:
        count += text.count(f)

    return count
