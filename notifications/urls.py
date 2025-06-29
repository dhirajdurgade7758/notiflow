from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('create/', views.create_reminder, name='create_reminder'),
    path('list/', views.reminder_list, name='reminder_list'),
    path('cancel/<uuid:pk>/', views.cancel_reminder, name='cancel_reminder'),
    path('alerts/', views.inapp_notifications, name='inapp_notifications'),
    path('toasts/', views.fetch_toasts, name='fetch_toasts'),
    path('alerts/read/<int:pk>/', views.mark_as_read, name='mark_as_read'),
    path('alerts/unread/<int:pk>/', views.mark_as_unread, name='mark_as_unread'),
    path('history/', views.reminder_history, name='reminder_history'),
    path('admin-reminders/', views.admin_reminder_monitor, name='admin_reminders'),
    path('smart-reminder/', views.smart_reminder_view, name='smart_reminder'),
    path('smart-reminder/modal/', views.smart_reminder_view, name='smart-reminder-modal'),


]
