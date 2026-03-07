from fastapi import APIRouter, Request, HTTPException
import os
import uuid
import cv2

import analysis_helpers as analysis

router = APIRouter()


@router.post("/upload_recording/{question_num}")
async def upload_recording(question_num: int, request: Request):
    """
    Accepts raw video/webm recording from frontend.
    Performs psychological wellness analysis (NOT lie detection).
    """

    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty request body")

    filename = f"upload_{uuid.uuid4()}.webm"

    try:
        # ----------------------------
        # Save uploaded video
        # ----------------------------
        with open(filename, "wb") as f:
            f.write(body)

        # ----------------------------
        # Extract video frames
        # ----------------------------
        frames = []
        cap = cv2.VideoCapture(filename)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        cap.release()

        # ----------------------------
        # FACIAL WELLNESS
        # ----------------------------
        facial_metrics = analysis.analyze_facial_features(frames)

        # ----------------------------
        # VOCAL WELLNESS
        # ----------------------------
        vocal_metrics = analysis.analyze_vocal_features(filename)

        # ----------------------------
        # SPEECH TRANSCRIPTION (Gemini)
        # ----------------------------
        transcription = await analysis.transcribe_audio(filename)

        # ----------------------------
        # TEXT WELLNESS (hesitation only)
        # ----------------------------
        filler_count = analysis.analyze_text(transcription)

        text_metrics = []
        if filler_count > 3:
            text_metrics.append({
                "type": "Speech Hesitation",
                "value": filler_count,
                "details": "Frequent filler-word usage indicating hesitation or planning"
            })
        else:
            text_metrics.append({
                "type": "Fluent Speech Pattern",
                "value": filler_count,
                "details": "Minimal filler usage, indicating fluent expression"
            })

        # ----------------------------
        # COMBINE WELLNESS METRICS
        # ----------------------------
        wellness_indicators = []
        wellness_indicators.extend(facial_metrics)
        wellness_indicators.extend(vocal_metrics)
        wellness_indicators.extend(text_metrics)

        # ----------------------------
        # FINAL RESPONSE
        # ----------------------------
        return {
            "id": str(uuid.uuid4()),
            "question": question_num,
            "transcription": transcription,
            "alerts": wellness_indicators  # keep key name for frontend compatibility
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception:
                pass
