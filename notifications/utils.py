from datetime import timedelta
from django.utils import timezone
from twilio.rest import Client
from django.conf import settings

def get_next_send_at(current_time, repeat_type):
    if repeat_type == 'daily':
        return current_time + timedelta(days=1)
    elif repeat_type == 'weekly':
        return current_time + timedelta(weeks=1)
    elif repeat_type == 'monthly':
        # Simple approximation: add 30 days
        return current_time + timedelta(days=30)
    return None


def send_sms(to_number, message):
    try:
        # Twilio credentials from settings
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_from_number = settings.TWILIO_PHONE_NUMBER

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            from_=twilio_from_number,
            to=to_number
        )

        print(f"✅ SMS sent to {to_number}")
        return True

    except Exception as e:
        print(f"❌ SMS sending failed: {e}")
        return False
