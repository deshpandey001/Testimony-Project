# =========================================================
# ENV + LOG SUPPRESSION (clean startup)
# =========================================================
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "2"

import sys


class _StderrFilter:
    def __init__(self, stream):
        self._stream = stream

    def write(self, s):
        msg = str(s)
        if (
            "TensorFlow Lite" in msg
            or "absl::InitializeLog()" in msg
            or "inference_feedback_manager.cc" in msg
        ):
            return
        self._stream.write(s)

    def flush(self):
        self._stream.flush()


sys.stderr = _StderrFilter(sys.stderr)

# =========================================================
# IMPORTS
# =========================================================
import uuid
import logging
import shutil
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from importlib import util as importlib_util

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env FIRST
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Lazy imports with error handling
analysis = None
llm = None
db = None
analytics_available = False

try:
    import analysis_helpers as analysis
    logger.info("✅ analysis_helpers loaded")
except ImportError as e:
    logger.error(f"⚠️ Failed to import analysis_helpers: {e}")

try:
    import llm_reporter as llm
    logger.info("✅ llm_reporter loaded")
except ImportError as e:
    logger.error(f"⚠️ Failed to import llm_reporter: {e}")

try:
    import database as db
    logger.info("✅ database loaded")
except ImportError as e:
    logger.error(f"⚠️ Failed to import database: {e}")

try:
    # Analytics module for research-grade metrics
    from analytics import (
        compute_wellness_score,
        compute_stress_map,
        get_peak_stress_question,
        compute_emotional_timeline,
        detect_inconsistencies,
        export_session_data,
    )
    analytics_available = True
    logger.info("✅ analytics module loaded")
except ImportError as e:
    logger.warning(f"⚠️ analytics module not available: {e}")
    analytics_available = False

# =========================================================
# APP INIT
# =========================================================
app = FastAPI(title="Student Psychological Wellness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5000",
        "https://testimony-frontend.onrender.com",
        "https://*.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# UTIL
# =========================================================
def extract_frames(video_path: str):
    try:
        import cv2
    except ImportError:
        logger.error("OpenCV not available")
        return []
    
    frames = []
    cap = cv2.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames


# =========================================================
# HEALTH CHECK
# =========================================================
@app.get("/")
@app.head("/")
async def root():
    """Welcome endpoint with API documentation."""
    return {
        "service": "Student Psychological Wellness API",
        "status": "🎉 Live on Render",
        "version": "1.0.0",
        "docs": "https://testimony-project-1.onrender.com/docs",
        "endpoints": {
            "health": "GET /health - Health check with module status",
            "upload_recording": "POST /upload_recording/{question_num} - Upload and analyze a single recording",
            "upload_and_assess": "POST /upload_and_assess - Upload video with optional audio",
            "generate_report": "POST /generate_report - Generate comprehensive report from analysis data",
            "recent": "GET /recent - Get recent reports",
            "analysis": "GET /analysis/{report_id} - Get specific analysis by ID"
        }
    }


@app.get("/health")
async def health():
    """Minimal health check for Render deployment."""
    return {
        "status": "healthy",
        "modules": {
            "analysis": analysis is not None,
            "llm_reporter": llm is not None,
            "database": db is not None,
            "analytics": analytics_available
        }
    }


# =========================================================
# SINGLE RESPONSE ANALYSIS
# =========================================================
@app.post("/upload_recording/{question_num}")
async def upload_recording(question_num: int, request: Request):
    body = await request.body()
    if not body:
        raise HTTPException(400, "Empty upload")

    filename = f"temp_{uuid.uuid4()}.webm"

    try:
        with open(filename, "wb") as f:
            f.write(body)

        frames = extract_frames(filename)

        # ✅ NEW CONTRACT - Alert-style metrics
        facial_metrics = analysis.analyze_facial_features(frames)
        vocal_metrics = analysis.analyze_vocal_features(filename)
        transcription = await analysis.transcribe_audio(filename)
        filler_count = analysis.analyze_text(transcription)

        # ✅ NUMERIC METRICS for analytics
        facial_numeric = analysis.extract_facial_metrics(frames)
        vocal_numeric = analysis.extract_vocal_metrics(filename)
        text_numeric = analysis.extract_text_metrics(transcription)

        # Combined numeric metrics
        numeric_metrics = {
            **facial_numeric,
            **vocal_numeric,
            **text_numeric
        }

        alerts = []
        alerts.extend(facial_metrics)
        alerts.extend(vocal_metrics)

        if filler_count > 3:
            alerts.append({
                "type": "Speech Hesitation",
                "value": filler_count,
                "details": "Increased filler-word usage"
            })

        return {
            "id": str(uuid.uuid4()),
            "question": question_num,
            "transcription": transcription,
            "alerts": alerts,
            "metrics": numeric_metrics,  # ✅ Research-grade numeric data
        }

    finally:
        if os.path.exists(filename):
            os.remove(filename)


# =========================================================
# MULTIPART UPLOAD (video + optional audio)
# =========================================================
@app.post("/upload_and_assess")
async def upload_and_assess(
    question_num: int = Form(...),
    video: UploadFile = File(...),
    audio: UploadFile = File(None),
):
    video_path = f"temp_{uuid.uuid4()}.webm"
    with open(video_path, "wb") as f:
        f.write(await video.read())

    audio_path = None
    if audio:
        audio_path = f"temp_{uuid.uuid4()}.wav"
        with open(audio_path, "wb") as f:
            f.write(await audio.read())

    try:
        frames = extract_frames(video_path)

        alerts = []
        alerts.extend(analysis.analyze_facial_features(frames))
        alerts.extend(analysis.analyze_vocal_features(audio_path or video_path))

        transcription = await analysis.transcribe_audio(audio_path or video_path)

        return {
            "id": str(uuid.uuid4()),
            "question": question_num,
            "transcription": transcription,
            "alerts": alerts,
        }

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


# =========================================================
# REPORT GENERATION
# =========================================================
@app.post("/generate_report")
async def generate_report(payload: dict):
    analysis_data = payload.get("analysis_data", [])

    # =========================================================
    # RESEARCH ANALYTICS - Compute session-level insights
    # =========================================================
    
    # Extract per-question numeric metrics
    questions_data = []
    for item in analysis_data:
        q_metrics = item.get("metrics", {})
        questions_data.append({
            "question_num": item.get("question", 0),
            "metrics": q_metrics,
            "transcription": item.get("transcription", ""),
            "alerts": item.get("alerts", []),
        })

    # Compute wellness index (0-100)
    session_metrics = {}
    for qd in questions_data:
        for key, val in qd.get("metrics", {}).items():
            if key not in session_metrics:
                session_metrics[key] = []
            if val is not None:
                session_metrics[key].append(val)
    
    # Average metrics for wellness computation
    avg_metrics = {k: (sum(v)/len(v) if v else None) for k, v in session_metrics.items()}
    
    wellness_result = compute_wellness_score(avg_metrics)

    # Compute stress map per question (questions_data has correct structure)
    stress_result = compute_stress_map(questions_data)

    # Compute emotional trend from audio metrics over time
    audio_segments = [qd.get("metrics", {}) for qd in questions_data]
    emotional_timeline = compute_emotional_timeline(audio_segments)

    # Detect behavioral inconsistencies
    inconsistencies = detect_inconsistencies(questions_data)

    # =========================================================
    # LLM Report Generation
    # =========================================================
    report_text = llm.generate_report(analysis_data)

    # Generate a fallback UUID in case DB fails
    fallback_id = str(uuid.uuid4())
    report_id = fallback_id

    # Try to persist to Supabase (non-blocking)
    try:
        session_id = db.create_session()
        if session_id:
            saved = db.save_report(session_id, report_text, analysis_data)
            if saved and saved[0].get("id"):
                report_id = saved[0]["id"]
    except Exception as e:
        print(f"⚠️ DB save skipped: {e}")

    return {
        "report": report_text,
        "report_id": report_id,
        "raw_data": analysis_data,
        
        # ✅ RESEARCH ANALYTICS
        "analytics": {
            "wellness": wellness_result,
            "stress_map": stress_result.get("stress_map", []),
            "peak_stress_question": stress_result.get("peak_stress_question"),
            "stress_trend": stress_result.get("stress_trend"),
            "emotional_timeline": emotional_timeline,
            "inconsistencies": inconsistencies,
        }
    }


# =========================================================
# DATABASE ROUTES
# =========================================================
@app.get("/recent")
async def recent():
    return {"results": db.get_recent_reports()}


@app.get("/analysis/{report_id}")
async def get_analysis(report_id: str):
    report = db.get_report_by_id(report_id)
    if not report:
        raise HTTPException(404)
    return report


# =========================================================
# ASR HEALTH CHECK
# =========================================================
@app.get("/health/asr")
async def health_asr():
    whispercpp_bin = os.getenv("WHISPERCPP_BIN")
    whispercpp_model = os.getenv("WHISPERCPP_MODEL")

    return {
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "whispercpp": {
            "bin_exists": os.path.exists(whispercpp_bin) if whispercpp_bin else False,
            "model_exists": os.path.exists(whispercpp_model) if whispercpp_model else False,
        },
        "python_whisper": importlib_util.find_spec("whisper") is not None,
        "ffmpeg_on_path": shutil.which("ffmpeg") is not None,
    }


# =========================================================
# DEV RUN
# =========================================================
# =========================================================
# SERVE FRONTEND STATIC FILES (fallback for SPA)
# =========================================================
frontend_dist_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist_path), html=True), name="static")
    logger.info(f"✅ Serving frontend from {frontend_dist_path}")
else:
    logger.warning(f"⚠️ Frontend dist folder not found at {frontend_dist_path}. Only API endpoints available.")


# =========================================================
# DEV RUN
# =========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
