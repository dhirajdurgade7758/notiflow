from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from .models import Reminder, InAppNotification
from .serializers import ReminderSerializer, NotificationSerializer
from .tasks import schedule_reminder_task


# 📌 List + Create Reminders
class ReminderListCreateAPI(generics.ListCreateAPIView):
    serializer_class = ReminderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user).order_by('-send_at')

    def perform_create(self, serializer):
        reminder = serializer.save(user=self.request.user, status='scheduled')

        # Schedule Celery task
        schedule_reminder_task.apply_async(
            args=[reminder.id],
            eta=reminder.send_at
        )


# 📌 Retrieve / Update Reminder
class ReminderDetailAPI(generics.RetrieveUpdateAPIView):
    serializer_class = ReminderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)


# 📌 Cancel Reminder
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def cancel_reminder_api(request, pk):
    try:
        reminder = Reminder.objects.get(pk=pk, user=request.user)
    except Reminder.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    reminder.status = 'cancelled'
    reminder.is_active = False
    reminder.save()

    return Response({"message": "Reminder cancelled"})


# 📌 List Notifications
class NotificationListAPI(generics.ListAPIView):
    serializer_class = NotificationSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InAppNotification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


# 📌 Mark Notification Read
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def mark_read_api(request, pk):
    try:
        notif = InAppNotification.objects.get(id=pk, user=request.user)
    except InAppNotification.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    notif.is_read = True
    notif.save()

    return Response({"message": "Marked as read"})


# 📌 Mark Notification Unread
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def mark_unread_api(request, pk):
    try:
        notif = InAppNotification.objects.get(id=pk, user=request.user)
    except InAppNotification.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    notif.is_read = False
    notif.save()

    return Response({"message": "Marked as unread"})


# 📌 Get Unread Notifications (For Real-Time Alerts)
@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_unread_notifications(request):
    """Get all unread notifications for real-time alert popup"""
    unread = InAppNotification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')
    
    serializer = NotificationSerializer(unread, many=True)
    return Response({
        "count": unread.count(),
        "notifications": serializer.data
    })


# 📌 Snooze Reminder
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def snooze_reminder(request):
    """Create a new reminder for X minutes from now"""
    from datetime import timedelta
    from django.utils import timezone
    
    reminder_id = request.data.get('reminder_id')
    snooze_minutes = request.data.get('snooze_minutes', 5)  # Default 5 minutes
    
    try:
        reminder = Reminder.objects.get(id=reminder_id, user=request.user)
    except Reminder.DoesNotExist:
        return Response({"error": "Reminder not found"}, status=404)
    
    # Create new snoozed reminder
    snooze_time = timezone.now() + timedelta(minutes=snooze_minutes)
    snoozed_reminder = Reminder.objects.create(
        user=request.user,
        title=reminder.title,
        message=reminder.message,
        notify_type=reminder.notify_type,
        send_at=snooze_time,
        repeat='none',
        status='scheduled'
    )
    
    # Schedule the snoozed reminder
    schedule_reminder_task.apply_async(
        args=[snoozed_reminder.id],
        eta=snooze_time
    )
    
    return Response({
        "message": f"Reminder snoozed for {snooze_minutes} minutes",
        "snooze_time": snooze_time.isoformat(),
        "new_reminder_id": str(snoozed_reminder.id)
    })
