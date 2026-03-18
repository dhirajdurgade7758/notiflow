from django.urls import path
from . import api_views

urlpatterns = [
    # Reminders
    path('reminders/', api_views.ReminderListCreateAPI.as_view(), name="api_reminders"),
    path('reminders/<uuid:pk>/', api_views.ReminderDetailAPI.as_view(), name="api_reminder_detail"),
    path('reminders/<uuid:pk>/cancel/', api_views.cancel_reminder_api, name="api_cancel_reminder"),

    # Notifications
    path('notifications/', api_views.NotificationListAPI.as_view(), name="api_notifications"),
    path('notifications/<int:pk>/read/', api_views.mark_read_api, name="api_notif_read"),
    path('notifications/<int:pk>/unread/', api_views.mark_unread_api, name="api_notif_unread"),
]

# Reminder APIs
# GET /api/reminders/
# POST /api/reminders/
# GET /api/reminders/<id>/
# PUT /api/reminders/<id>/
# POST /api/reminders/<id>/cancel/

# Notification APIs
# GET /api/notifications/
# POST /api/notifications/<id>/read/
# POST /api/notifications/<id>/unread/