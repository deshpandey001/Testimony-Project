# =========================================================
# PSYCHOLOGICAL WELLNESS ANALYSIS HELPERS
# (Student / Educational / HR safe domain)
# =========================================================

import os
import warnings
import subprocess
import shutil
import cv2
import numpy as np
import mediapipe as mp
import librosa
import asyncio
import tempfile
from textblob import TextBlob

# =========================================================
# SAFE GEMINI IMPORT
# =========================================================
try:
    import google.generativeai as genai
except Exception:
    genai = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =========================================================
# MEDIAPIPE FACE MESH INIT
# =========================================================
mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1
)

# =========================================================
# ---------------- FACIAL WELLNESS ------------------------
# =========================================================

def calculate_ear(eye):
    """Eye Aspect Ratio (EAR)"""
    A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
    B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
    C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
    return (A + B) / (2.0 * C + 1e-6)


def analyze_facial_features(frames):
    """
    Facial behavioral wellness indicators.

    RETURNS (ALWAYS):
        List[Dict] → wellness indicators
    """

    metrics = []

    if not frames or len(frames) < 2:
        return [{
            "type": "Facial Data Unavailable",
            "value": None,
            "details": "Insufficient video frames for facial analysis"
        }]

    blink_count = 0
    eye_closed = False
    EAR_THRESHOLD = 0.22

    for frame in frames:
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = mp_face_mesh.process(rgb)

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


def analyze_vocal_features(audio_path):
    """
    Vocal wellness indicators.

    RETURNS (ALWAYS):
        List[Dict]
    """

    metrics = []

    if not audio_path or not os.path.exists(audio_path):
        return [{
            "type": "Audio Data Unavailable",
            "value": None,
            "details": "No valid audio input for vocal analysis"
        }]

    safe_path = _ensure_wav(audio_path)

    try:
        y, sr = librosa.load(safe_path, sr=16000)

        rms = librosa.feature.rms(y=y)
        energy_var = float(np.var(rms))

        pitches, mags = librosa.piptrack(y=y, sr=sr)
        pitch_vals = pitches[mags > np.median(mags)]
        pitch_var = float(np.var(pitch_vals)) if len(pitch_vals) else 0.0

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
        model = genai.GenerativeModel("gemini-1.5-flash")

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
