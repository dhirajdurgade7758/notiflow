import re
import json
import logging
from ast import literal_eval
from django.conf import settings

import google.generativeai as genai

logger = logging.getLogger(__name__)

# -------------------------------------------------
# 🔐 GEMINI API SETUP
# -------------------------------------------------
genai.configure(api_key=settings.GEMINI_API_KEY)

# Choose the model you prefer:
# - "gemini-1.5-flash" → fast + cheap
# - "gemini-1.5-pro" → better reasoning
MODEL = "gemini-2.5-flash"


# -------------------------------------------------
# 🔧 Helper: Unified Gemini Response Extractor
# -------------------------------------------------
def _extract_text(response):
    """Extracts clean text from Gemini responses."""
    try:
        if hasattr(response, "text"):
            return response.text
        elif isinstance(response, dict):
            return response.get("text", "")
        else:
            return str(response)
    except Exception:
        return str(response)


# -------------------------------------------------
# 🧠 1. PARSE NATURAL REMINDER (MAIN FUNCTION)
# -------------------------------------------------
def parse_natural_reminder(text):
    prompt = (
        "Extract structured reminder details from the user's message.\n\n"
        f"User said:\n{text}\n\n"
        "Return ONLY a valid JSON object with keys:\n"
        "- title\n"
        "- message\n"
        "- notify_type ('email','inapp','sms')\n"
        "- repeat ('none','daily','weekly','monthly')\n"
        "- datetime (ISO timestamp or null)\n"
        "- tone ('friendly','formal','motivational','gentle' or null)\n\n"
        "Wrap JSON inside a markdown code block like:\n```json\n{...}\n```"
    )

    try:
        model = genai.GenerativeModel(MODEL)

        response = model.generate_content(prompt)
        content = _extract_text(response)

        if settings.DEBUG:
            logger.debug(f"🧠 Gemini Response: {content}")

        # Extract JSON from ```json ``` code block
        match = re.search(r"```(?:json)?\s*({.*?})\s*```", content, re.DOTALL)
        if match:
            json_block = match.group(1)
        else:
            # fallback: find first {...}
            match = re.search(r"({.*})", content, re.DOTALL)
            if not match:
                raise ValueError("No JSON found in Gemini response.")
            json_block = match.group(1)

        # Remove comments if any
        json_block = re.sub(r"//.*", "", json_block)

        try:
            return json.loads(json_block)
        except json.JSONDecodeError:
            return literal_eval(json_block)

    except Exception as e:
        logger.error(f"❌ Failed to parse natural reminder: {e}", exc_info=True)
        raise



# -------------------------------------------------
# 💬 2. REWRITE MESSAGE TONE
# -------------------------------------------------
def rewrite_message_tone(message, tone="friendly"):
    prompt = (
        f"Rewrite the reminder message below in a {tone} tone.\n"
        "Return ONLY the rewritten text. No explanation.\n\n"
        f"Message:\n{message}"
    )

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        rewritten = _extract_text(response).strip()

        if settings.DEBUG:
            logger.debug(f"📝 Rewritten [{tone}]: {rewritten}")

        return rewritten

    except Exception as e:
        logger.error(f"❌ Failed to rewrite tone: {e}", exc_info=True)
        return message  # fallback



# -------------------------------------------------
# 🤖 3. GENERATE AI SUGGESTED REMINDERS
# -------------------------------------------------
def generate_ai_prompt(user, reminders):
    reminder_data = "\n".join(
        f"- {r.title} at {r.send_at.strftime('%A %I:%M %p')} ({r.notify_type})"
        for r in reminders.order_by('-send_at')[:10]
    )

    return (
        f"The user has these reminders:\n{reminder_data}\n\n"
        "Suggest 2–3 new helpful reminders.\n"
        "Return a JSON list like:\n"
        "[ {\"title\":..., \"message\":..., \"datetime\":...}, ... ]"
    )



def call_llm_api(prompt):
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        content = _extract_text(response)

        # Extract list [...]
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if not match:
            raise ValueError("No JSON list found in Gemini response.")

        return json.loads(match.group(0))

    except Exception as e:
        logger.error(f"❌ Failed to generate suggestions: {e}", exc_info=True)
        raise
