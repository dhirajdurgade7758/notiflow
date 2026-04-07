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
    from datetime import datetime, timedelta
    
    # Get current date/time for context
    now = datetime.now()
    today = now.date()
    current_year = now.year
    current_month = now.month
    current_day = now.day
    current_weekday = today.strftime('%A')  # e.g., "Tuesday"
    
    # Pre-calculate common dates for examples
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    next_week = today + timedelta(days=7)
    next_month = today + timedelta(days=30)
    
    # Find next occurrence of each weekday
    weekday_dates = {}
    for day_offset in range(1, 8):
        future_date = today + timedelta(days=day_offset)
        weekday_name = future_date.strftime('%A')
        if weekday_name not in weekday_dates:
            weekday_dates[weekday_name] = future_date
    
    prompt = (
        "You are a reminder parsing expert. Extract reminder details from natural language.\n\n"
        f"SYSTEM CONTEXT (IMPORTANT - Use this to calculate dates):\n"
        f"- Current date: {today.strftime('%A, %B %d, %Y')} (Day {current_day} of Month {current_month}, Year {current_year})\n"
        f"- Current time: {now.strftime('%I:%M %p')} ({now.strftime('%H:%M:%S')} in 24-hour format)\n\n"
        
        f"DATE CALCULATION RULES (Parse user's relative dates using today's context):\n"
        f"✓ 'today' → {today.isoformat()}\n"
        f"✓ 'tomorrow' → {tomorrow.isoformat()}\n"
        f"✓ 'day after tomorrow' → {day_after_tomorrow.isoformat()}\n"
        f"✓ 'next Monday' → {weekday_dates.get('Monday', today + timedelta(days=1)).isoformat()}\n"
        f"✓ 'next Tuesday' → {weekday_dates.get('Tuesday', today + timedelta(days=1)).isoformat()}\n"
        f"✓ 'next week' → {next_week.isoformat()}\n"
        f"✓ If user says day name (e.g., 'Monday'), calculate to NEXT occurrence using today as reference\n"
        f"✓ If user says 'next Monday' and today IS Monday, treat as 7 days from now\n"
        f"✓ If user says 'this Friday' and today is Tuesday (April 8), that means April 12 (4 days away)\n"
        f"✓ ALWAYS include FULL YEAR {current_year} in dates (unless explicitly mentioning next year)\n\n"
        
        f"TIME CALCULATION RULES:\n"
        f"✓ If no time mentioned → Default to 09:00:00 (9 AM)\n"
        f"✓ '5 PM' or '17:00' → 17:00:00\n"
        f"✓ '3:30 PM' → 15:30:00\n"
        f"✓ 'in 30 minutes' → Add 30 min to current time {now.strftime('%H:%M:%S')}\n"
        f"✓ 'in 2 hours' → Add 2 hours to current time\n"
        f"✓ 'at noon' → 12:00:00\n"
        f"✓ 'at midnight' → 00:00:00 (next day)\n"
        f"✓ 'in the evening' → 18:00:00\n"
        f"✓ 'in the morning' → 08:00:00\n\n"
        
        f"WORKED EXAMPLES (Learn from these):\n"
        f"Example 1:\n"
        f"  User: 'Remind me tomorrow at 5 PM to exercise'\n"
        f"  Today is: {today.strftime('%A, %B %d, %Y')}\n"
        f"  Tomorrow is: {tomorrow.strftime('%A, %B %d, %Y')}\n"
        f"  Expected datetime: '{tomorrow.isoformat()}T17:00:00'\n\n"
        
        f"Example 2:\n"
        f"  User: 'Call mom day after tomorrow'\n"
        f"  Today is: {today.strftime('%A, %B %d, %Y')}\n"
        f"  Day after tomorrow is: {day_after_tomorrow.strftime('%A, %B %d, %Y')}\n"
        f"  No time specified → Default to 9 AM\n"
        f"  Expected datetime: '{day_after_tomorrow.isoformat()}T09:00:00'\n\n"
        
        f"Example 3:\n"
        f"  User: 'Next Monday at 3 PM meeting'\n"
        f"  Today is: {today.strftime('%A, %B %d, %Y')}\n"
        f"  Next Monday is: {weekday_dates.get('Monday', today + timedelta(days=1)).strftime('%A, %B %d, %Y')}\n"
        f"  Expected datetime: '{weekday_dates.get('Monday', today + timedelta(days=1)).isoformat()}T15:00:00'\n\n"
        
        f"Example 4:\n"
        f"  User: 'In 2 hours drink water' (said at {now.strftime('%I:%M %p')})\n"
        f"  Current time: {now.strftime('%I:%M %p')}\n"
        f"  In 2 hours: {(now + timedelta(hours=2)).strftime('%I:%M %p')}\n"
        f"  Same day: {today.isoformat()}\n"
        f"  Expected datetime: '{today.isoformat()}T{(now + timedelta(hours=2)).strftime('%H:%M:%S')}'\n\n"
        
        f"User's request:\n{text}\n\n"
        
        "Extract and return a valid JSON object with:\n"
        "- title: Short action title (max 10 words)\n"
        "- message: Full reminder text\n"
        "- notify_type: 'email', 'inapp', or 'sms' (default: 'inapp')\n"
        "- repeat: 'none', 'daily', 'weekly', 'monthly' (default: 'none')\n"
        "- datetime: ISO 8601 format 'YYYY-MM-DDTHH:MM:SS' - MUST include date AND time\n"
        "- tone: 'friendly', 'formal', 'motivational', 'gentle', or null\n\n"
        
        "CRITICAL RULES:\n"
        "⚠️ ALWAYS include 'datetime' field\n"
        "⚠️ ALWAYS use correct year {year}\n"
        "⚠️ ALWAYS calculate relative dates based on today ({today})\n"
        "⚠️ If time not specified, use 09:00:00\n"
        "⚠️ Return ONLY valid JSON inside ```json``` code block\n"
        "⚠️ No additional text\n\n"
        
        "Return format:\n```json\n{{\n  \"title\": \"...\",\n  \"message\": \"...\",\n  \"notify_type\": \"inapp\",\n  \"repeat\": \"none\",\n  \"datetime\": \"2026-MM-DDTHH:MM:SS\",\n  \"tone\": \"friendly\"\n}}\n```".format(year=current_year, today=today.isoformat())
    )

    try:
        model = genai.GenerativeModel(MODEL)

        response = model.generate_content(prompt)
        content = _extract_text(response)

        if settings.DEBUG:
            logger.debug(f"🧠 Gemini Prompt Context: Today={today}, CurrentTime={now.strftime('%H:%M:%S')}")
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
            result = json.loads(json_block)
            if settings.DEBUG:
                logger.debug(f"✅ Parsed reminder: {result}")
            return result
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
