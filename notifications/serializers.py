from rest_framework import serializers
from .models import Reminder, InAppNotification

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InAppNotification
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
