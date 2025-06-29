from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class Reminder(models.Model):
    NOTIFICATION_TYPES = (
        ('email', 'Email'),
        ('inapp', 'In-App'),
         ('sms', 'SMS'),
        # Add more types later like 'sms', 'push', etc.
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    REPEAT_CHOICES = (
        ('none', 'Do not repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reminders")

    title = models.CharField(max_length=255)
    message = models.TextField()
    notify_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='email')

    send_at = models.DateTimeField()  # When to send
    created_at = models.DateTimeField(auto_now_add=True)

    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES, default='none')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.status} - {self.send_at}"

    class Meta:
        ordering = ['-send_at']


class InAppNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inapp_notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"🔔 {self.title} for {self.user}"

class ReminderFailureLog(models.Model):
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, related_name='failure_logs')
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"❌ Failure on {self.reminder.title} at {self.timestamp}"
