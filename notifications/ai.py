import requests
import json
import dateparser
from django.conf import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = settings.GROQ_API_KEY  # Set this in your Django settings

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "llama3-70b-8192"




import requests
import json
import re
from ast import literal_eval
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

MODEL = "llama3-70b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = settings.GROQ_API_KEY

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}


def parse_natural_reminder(text):
    prompt = (
        "You are a helpful assistant. Extract structured reminder details from the user's instruction below:\n\n"
        f"'{text}'\n\n"
        "Return ONLY a valid JSON object with the following keys:\n"
        "- title: short title of the reminder\n"
        "- message: full message to send\n"
        "- notify_type: one of 'email', 'inapp', or 'sms'. If user didn't specify, return 'email'.\n"
        "- repeat: one of 'none', 'daily', 'weekly', 'monthly'\n"
        "- datetime: ISO format datetime string like '2025-06-25T21:00:00'. If user didn't specify, return null.\n"
        "- tone: one of 'friendly', 'formal', 'motivational', 'gentle', or null if unspecified.\n\n"
        "Wrap the JSON in a code block like ```json ... ```"
    )

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }

    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if settings.DEBUG:
            logger.debug(f"🧠 LLM Response: {content}")

        # Extract JSON from markdown/code block
        match = re.search(r"```(?:json)?\s*({.*?})\s*```", content, re.DOTALL)
        if match:
            json_block = match.group(1)
        else:
            match = re.search(r"({.*})", content, re.DOTALL)
            if not match:
                raise ValueError("No JSON found in LLM response.")
            json_block = match.group(1)

        json_block = re.sub(r"//.*", "", json_block)

        try:
            return json.loads(json_block)
        except json.JSONDecodeError:
            return literal_eval(json_block)

    except Exception as e:
        logger.error(f"❌ Failed to parse natural reminder: {e}", exc_info=True)
        raise


def rewrite_message_tone(message, tone="friendly"):
    prompt = (
        f"Rewrite the following reminder message in a {tone} tone.\n"
        "Only return the rewritten message, no explanation or intro:\n\n"
        f"{message}"
    )

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6
    }

    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()
        rewritten = response.json()["choices"][0]["message"]["content"].strip()

        if settings.DEBUG:
            logger.debug(f"📝 Rewritten message [{tone}]: {rewritten}")

        return rewritten

    except Exception as e:
        logger.error(f"❌ Failed to rewrite message tone: {e}", exc_info=True)
        return message  # fallback: return original message



def generate_ai_prompt(user, reminders):
    reminder_data = "\n".join(
        f"- {r.title} at {r.send_at.strftime('%A %I:%M %p')} ({r.notify_type})"
        for r in reminders.order_by('-send_at')[:10]
    )

    return (
        f"This user has set the following reminders:\n"
        f"{reminder_data}\n\n"
        "Based on their activity, suggest 2–3 new helpful reminders to improve productivity or wellness. "
        "Return a JSON list with items having title, message, and datetime (optional)."
    )


def call_llm_api(prompt):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(GROQ_API_URL, headers=HEADERS, data=json.dumps(payload))
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    match = re.search(r"\[.*\]", content, re.DOTALL)
    if not match:
        raise ValueError("No JSON list found.")

    suggestions = match.group(0)
    return json.loads(suggestions)
