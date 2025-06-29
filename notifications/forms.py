from django import forms
from .models import Reminder
from django.utils import timezone

class ReminderForm(forms.ModelForm):
    send_at = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }
        ),
        label="Send At (Date & Time)",
    )

    class Meta:
        model = Reminder
        fields = ['title', 'message', 'notify_type', 'send_at', 'repeat']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter reminder title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter message content'
            }),
            'notify_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'repeat': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'title': 'Reminder Title',
            'message': 'Message Content',
            'notify_type': 'Notification Type',
            'repeat': 'Repeat Frequency',
        }

    def clean_send_at(self):
        send_at = self.cleaned_data.get('send_at')
        if send_at < timezone.now():
            raise forms.ValidationError("Scheduled time cannot be in the past.")
        return send_at
