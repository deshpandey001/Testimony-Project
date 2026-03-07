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
import cv2
import shutil
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from importlib import util as importlib_util

# Load env FIRST
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

import analysis_helpers as analysis
import llm_reporter as llm
import database as db

# =========================================================
# APP INIT
# =========================================================
app = FastAPI(title="Student Psychological Wellness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# UTIL
# =========================================================
def extract_frames(video_path: str):
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

        # ✅ NEW CONTRACT
        facial_metrics = analysis.analyze_facial_features(frames)
        vocal_metrics = analysis.analyze_vocal_features(filename)
        transcription = await analysis.transcribe_audio(filename)
        filler_count = analysis.analyze_text(transcription)

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

    report_text = llm.generate_report(analysis_data)

    session_id = db.create_session("Student")
    report_id = None

    if session_id:
        saved = db.save_report(session_id, report_text, analysis_data)
        if saved:
            report_id = saved[0]["id"]

    return {
        "report": report_text,
        "report_id": report_id,
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
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
