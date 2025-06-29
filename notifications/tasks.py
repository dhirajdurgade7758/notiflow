from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .models import Reminder, ReminderFailureLog, InAppNotification
from .utils import get_next_send_at, send_sms


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
