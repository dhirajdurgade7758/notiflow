from celery import shared_task
import dateparser
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .models import Reminder, ReminderFailureLog, InAppNotification
from .utils import get_next_send_at, send_sms
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
User = get_user_model()

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def schedule_reminder_task(self, reminder_id):
    try:
        reminder = Reminder.objects.get(id=reminder_id)

        if not reminder.is_active or reminder.status == 'cancelled':
            return f"Reminder {reminder.id} is cancelled or inactive."

        if timezone.now() < reminder.send_at:
            return f"Reminder {reminder.id} not due yet."

        # 🔔 Send the actual notification
        if reminder.notify_type == 'email':
            try:
                send_mail(
                    subject=f"⏰ Reminder: {reminder.title}",
                    message=reminder.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reminder.user.email],
                    fail_silently=False,
                )
                print(f"✅ Email sent to {reminder.user.email}")
            except Exception as email_error:
                _handle_failure(reminder, email_error)
                raise self.retry(exc=email_error)

        elif reminder.notify_type == 'inapp':
            InAppNotification.objects.create(
                user=reminder.user,
                title=f"⏰ Reminder: {reminder.title}",
                message=reminder.message
            )
            print(f"✅ In-app notification sent to {reminder.user.username}")

        elif reminder.notify_type == 'sms':
            user_profile = getattr(reminder.user, 'profile', None)
            phone = getattr(user_profile, 'phone', None)
            print(f"User phone: {phone}")
            if not phone:
                raise ValueError("User has no phone number saved.")
            
            success = send_sms(phone, f"⏰ Reminder: {reminder.title}\n{reminder.message}")
            if not success:
                raise ValueError("SMS failed to send")
            print(f"✅ SMS sent to {phone}")
        
        else:
            error = ValueError("Unsupported notification type.")
            _handle_failure(reminder, error)
            raise error

        # ✅ Mark as sent
        reminder.status = 'sent'
        reminder.save()

        # 🔁 Handle recurring
        if reminder.repeat != 'none':
            next_time = get_next_send_at(reminder.send_at, reminder.repeat)
            if next_time:
                new_reminder = Reminder.objects.create(
                    user=reminder.user,
                    title=reminder.title,
                    message=reminder.message,
                    notify_type=reminder.notify_type,
                    send_at=next_time,
                    repeat=reminder.repeat,
                    status='scheduled',
                    is_active=True,
                )
                schedule_reminder_task.apply_async(
                    args=[str(new_reminder.id)],
                    eta=new_reminder.send_at
                )

        return f"Reminder {reminder.id} sent successfully."

    except Exception as e:
        reminder = Reminder.objects.filter(id=reminder_id).first()
        if reminder:
            _handle_failure(reminder, e)
        raise self.retry(exc=e)


def _handle_failure(reminder, exception_obj):
    """Utility to handle failure logging and alerting."""
    reminder.status = 'failed'
    reminder.save()

    ReminderFailureLog.objects.create(
        reminder=reminder,
        error_message=str(exception_obj)
    )

    try:
        send_mail(
            subject=f"🚨 Reminder Failed: {reminder.title}",
            message=(
                f"Reminder ID: {reminder.id}\n"
                f"User: {reminder.user.email}\n"
                f"Scheduled At: {reminder.send_at}\n"
                f"Error: {str(exception_obj)}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ALERT_EMAILS,
            fail_silently=True,
        )
    except Exception as admin_alert_error:
        print(f"⚠️ Failed to notify admin: {admin_alert_error}")

@shared_task
def cleanup_old_reminders():
    old = Reminder.objects.filter(send_at__lt=timezone.now() - timezone.timedelta(days=30))
    count = old.count()
    old.delete()
    print(f"🧹 Deleted {count} old reminders.")



@shared_task
def send_weekly_analytics():
    now = timezone.now()
    one_week_ago = now - timezone.timedelta(days=7)

    users = User.objects.all()

    for user in users:
        reminders = Reminder.objects.filter(user=user, send_at__gte=one_week_ago)

        total = reminders.count()
        sent = reminders.filter(status='sent').count()
        failed = reminders.filter(status='failed').count()
        upcoming = Reminder.objects.filter(user=user, send_at__gt=now).order_by('send_at')[:3]

        # Determine most used type
        type_counts = reminders.values_list('notify_type', flat=True)
        most_used = max(set(type_counts), key=type_counts.count) if type_counts else "N/A"

        if total == 0 and upcoming.count() == 0:
            continue  # Skip empty users

        context = {
            "user": user,
            "total": total,
            "sent": sent,
            "failed": failed,
            "most_used": most_used,
            "upcoming": upcoming,
        }

        subject = "📊 Your Weekly Reminder Summary"
        html = render_to_string("notifications/email/weekly_summary.html", context)

        try:
            send_mail(
                subject=subject,
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html
            )
            print(f"✅ Sent summary to {user.email}")
        except Exception as e:
            print(f"❌ Failed to send to {user.email}: {e}")


import requests
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Reminder, AISuggestion
from django.core.mail import send_mail
from .ai import generate_ai_prompt, call_llm_api
from django.utils.timezone import make_aware
@shared_task
def sync_ai_recommendations():
    from django.contrib.auth import get_user_model
    User = get_user_model()

    one_month_ago = timezone.now() - timezone.timedelta(days=30)

    for user in User.objects.all():
        past_reminders = Reminder.objects.filter(user=user, send_at__gte=one_month_ago)

        if not past_reminders.exists():
            continue

        prompt = generate_ai_prompt(user, past_reminders)
        suggestions = call_llm_api(prompt)


        for suggestion in suggestions:
            naive_time = dateparser.parse(suggestion.get("datetime"))
            aware_time = make_aware(naive_time) if naive_time and timezone.is_naive(naive_time) else naive_time
            AISuggestion.objects.create(
                user=user,
                suggested_title=suggestion["title"],
                suggested_message=suggestion["message"],
                suggested_time=aware_time,
            )

        # Optional: Send email summary
        html = render_to_string("notifications/email/ai_suggestions.html", {
            "user": user,
            "suggestions": suggestions,
        })

        send_mail(
            subject="🧠 Weekly AI Reminder Suggestions",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html
        )
