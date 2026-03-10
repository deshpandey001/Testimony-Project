# =========================================================
# WELLNESS REPORT GENERATOR (Gemini + Local Fallback)
# Student / HR Psychological Wellness Domain
# =========================================================

import os
import time
import re
import google.generativeai as genai
from textblob import TextBlob
from analysis_helpers import analyze_text as count_fillers


# =========================================================
# LOCAL FALLBACK (NO API DEPENDENCY)
# =========================================================
def _local_report_fallback(analysis_data):
    """
    Deterministic psychological wellness report.
    Safe for students, HR, research, and patent use.
    """

    total_indicators = sum(len(item.get("alerts") or []) for item in analysis_data)

    fillers = []
    sentiments = []

    for item in analysis_data:
        text = item.get("transcription") or ""
        fillers.append(count_fillers(text))
        try:
            sentiments.append(TextBlob(text).sentiment.polarity)
        except Exception:
            sentiments.append(0.0)

    filler_total = sum(fillers)
    avg_sentiment = sum(sentiments) / max(1, len(sentiments))

    lines = []

    # =====================================================
    # OVERALL EMOTIONAL STATE
    # =====================================================
    lines.append("Overall Emotional State:\n")

    if total_indicators == 0:
        lines.append(
            "The participant demonstrated stable verbal and non-verbal behavior throughout the session, "
            "suggesting comfort, engagement, and emotional balance.\n"
        )
    else:
        lines.append(
            f"A total of {total_indicators} wellness-related behavioral indicators were observed. "
            "These patterns may reflect temporary cognitive effort, mild stress, or adaptive response behaviors.\n"
        )

    # =====================================================
    # SPEECH & COMMUNICATION
    # =====================================================
    lines.append("\nSpeech & Communication Patterns:\n")

    if filler_total > 6:
        lines.append("Frequent filler-word usage suggests hesitation or increased cognitive load.\n")
    elif filler_total > 3:
        lines.append("Moderate filler usage indicates mild uncertainty during responses.\n")
    else:
        lines.append("Speech appeared fluent and well-articulated.\n")

    if avg_sentiment > 0.1:
        lines.append("Overall tone was positive and engaged.\n")
    elif avg_sentiment < -0.1:
        lines.append("Tone occasionally reflected tension or cautious expression.\n")
    else:
        lines.append("Tone remained largely neutral and steady.\n")

    # =====================================================
    # BEHAVIORAL & PHYSIOLOGICAL INDICATORS
    # =====================================================
    lines.append("\nBehavioral & Physiological Indicators:\n")

    for item in analysis_data:
        for m in item.get("alerts", []):
            lines.append(f"- {m.get('type')}: {m.get('details')}\n")

    if total_indicators == 0:
        lines.append("No notable stress or fatigue indicators detected.\n")

    # =====================================================
    # PER-QUESTION REFLECTION
    # =====================================================
    lines.append("\nPer-Question Reflection:\n")

    for item in analysis_data:
        q = item.get("question")
        lines.append(f"\nQuestion {q}:\n")
        lines.append(f"Response: {item.get('transcription') or '[No transcription]'}\n")

        indicators = item.get("alerts", [])
        if indicators:
            for m in indicators:
                lines.append(f"• {m.get('type')} observed\n")
        else:
            lines.append("• Behavioral patterns remained stable\n")

    # =====================================================
    # WELLNESS SUGGESTIONS
    # =====================================================
    lines.append(
        "\nWellness Suggestions:\n"
        "Encouraging a relaxed environment, sufficient response time, and psychological safety "
        "may further enhance communication clarity and emotional comfort."
    )

    return "\n".join(lines)


# =========================================================
# GEMINI-POWERED REPORT GENERATION
# =========================================================
def generate_report(analysis_data):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "text/plain"
            }
        )

        prompt = """
You are a Psychological Wellness Assessment Assistant.

Rules:
- This is NOT lie detection
- Do NOT mention deception, truth, or dishonesty
- Focus on stress, confidence, engagement, and communication patterns
- Use supportive, neutral, research-appropriate language

SESSION DATA:
"""

        for item in analysis_data:
            prompt += f"\n--- Question {item.get('question')} ---\n"
            prompt += f"Transcription: {item.get('transcription') or '[No transcription]'}\n"

            for m in item.get("alerts", []):
                prompt += f"{m.get('type')} → {m.get('details')}\n"

        prompt += """
Generate sections:
1. Overall Emotional State
2. Speech & Communication Patterns
3. Behavioral & Physiological Indicators
4. Per-Question Reflection
5. Wellness Suggestions
"""

        response = model.generate_content(prompt)

        if response and response.text:
            return response.text

        return _local_report_fallback(analysis_data)

    except Exception as e:
        print("Gemini report generation failed:", e)
        return _local_report_fallback(analysis_data)
