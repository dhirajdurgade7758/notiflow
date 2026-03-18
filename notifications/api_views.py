from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
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
@authentication_classes([TokenAuthentication])
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InAppNotification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


# 📌 Mark Notification Read
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
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
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def mark_unread_api(request, pk):
    try:
        notif = InAppNotification.objects.get(id=pk, user=request.user)
    except InAppNotification.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    notif.is_read = False
    notif.save()

    return Response({"message": "Marked as unread"})
