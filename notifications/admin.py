from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Reminder)
admin.site.register(InAppNotification)

@admin.register(ReminderFailureLog)
class ReminderFailureLogAdmin(admin.ModelAdmin):
    list_display = ('reminder', 'timestamp', 'error_message')
    list_filter = ('timestamp',)
    search_fields = ('error_message', 'reminder__title')