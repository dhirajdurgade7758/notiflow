from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string

from .forms import ReminderForm
from .models import *
from .tasks import schedule_reminder_task       


from django.db.models import Count, Q

from django.utils import timezone
from django.db.models import Q

@login_required
def user_dashboard(request):
    user = request.user

    # Get today's alerts for counter (for correct alert count)
    today = timezone.now().date()
    todays_alerts = InAppNotification.objects.filter(user=user, created_at__date=today)

    # For preview purposes, show only 5 recent alerts
    recent_alerts = todays_alerts.order_by('-created_at')[:5]

    upcoming_reminders = Reminder.objects.filter(
        user=user,
        is_active=True,
        send_at__gte=timezone.now()
    ).order_by('send_at')[:5]

    stats = {
        'total': Reminder.objects.filter(user=user).count(),
        'scheduled': Reminder.objects.filter(user=user, status='scheduled').count(),
        'sent': Reminder.objects.filter(user=user, status='sent').count(),
        'failed': Reminder.objects.filter(user=user, status='failed').count(),
        'cancelled': Reminder.objects.filter(user=user, status='cancelled').count(),
    }
    print(f"Dashboard stats for {user.username}: {stats}")

    return render(request, 'notifications/dashboard.html', {
        'alerts': todays_alerts,            # for alert counter and list
        'reminders': upcoming_reminders,
        'stats': stats
    })



@login_required
def create_reminder(request):
    form = ReminderForm(request.POST or None)
    unread_alerts = InAppNotification.objects.filter(user=request.user, is_read=False)

    if form.is_valid():
        if form.cleaned_data['notify_type'] == 'sms':
            if not request.user.profile.phone:
                form.add_error('notify_type', "Add your phone number to use SMS.")

        reminder = form.save(commit=False)
        reminder.user = request.user
        reminder.status = 'scheduled'
        reminder.save()

        schedule_reminder_task.apply_async(
            args=[reminder.id],
            eta=reminder.send_at
        )
        print(f"Reminder {reminder.id} scheduled for {reminder.send_at}")

        messages.success(request, "Reminder scheduled successfully!")
        return redirect('reminder_list')

    return render(request, 'notifications/create_reminder.html', {
        'form': form,
        'unread_alerts': unread_alerts,
    })


@login_required
def reminder_list(request):
    reminders = Reminder.objects.filter(user=request.user).order_by('-send_at')
    return render(request, 'notifications/reminder_list.html', {'reminders': reminders})

@login_required
def reminder_history(request):
    filter_status = request.GET.get("status")
    qs = Reminder.objects.filter(user=request.user, status__in=['sent', 'failed', 'cancelled'])

    if filter_status in ['sent', 'failed', 'cancelled']:
        qs = qs.filter(status=filter_status)

    history = qs.order_by('-send_at')

    return render(request, 'notifications/reminder_history.html', {'history': history})

@login_required
def cancel_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    reminder.status = 'cancelled'
    reminder.is_active = False
    reminder.save()
    messages.info(request, "Reminder cancelled.")
    return redirect('reminder_list')

@login_required
def inapp_notifications(request):
    filter_val = request.GET.get("filter", "all")

    if filter_val == "read":
        notifications = InAppNotification.objects.filter(user=request.user, is_read=True)
    elif filter_val == "unread":
        notifications = InAppNotification.objects.filter(user=request.user, is_read=False)
    else:
        notifications = InAppNotification.objects.filter(user=request.user)

    notifications = notifications.order_by('-created_at')

    return render(request, 'notifications/inapp_notifications.html', {
        'notifications': notifications,
        'filter_val': filter_val
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

@staff_member_required
def admin_reminder_monitor(request):
    status_filter = request.GET.get("status")
    user_filter = request.GET.get("user")

    reminders = Reminder.objects.all().select_related('user')

    if status_filter in ['scheduled', 'sent', 'failed', 'cancelled']:
        reminders = reminders.filter(status=status_filter)

    if user_filter:
        reminders = reminders.filter(user__username__icontains=user_filter)

    reminders = reminders.order_by('-send_at')

    stats = {
        'total': Reminder.objects.count(),
        'scheduled': Reminder.objects.filter(status='scheduled').count(),
        'sent': Reminder.objects.filter(status='sent').count(),
        'failed': Reminder.objects.filter(status='failed').count(),
        'cancelled': Reminder.objects.filter(status='cancelled').count(),
        'recurring': Reminder.objects.exclude(repeat='none').count(),
    }

    return render(request, 'notifications/admin_panel.html', {
        'reminders': reminders,
        'stats': stats,
        'status_filter': status_filter,
        'user_filter': user_filter,
    })


@login_required
def fetch_toasts(request):
    unread_qs = InAppNotification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    unread = list(unread_qs[:5])  # Slice to get objects (not queryset)

    # Render template
    html = render_to_string('notifications/_toasts.html', {'alerts': unread})

    # Get IDs and bulk update
    ids = [n.id for n in unread]
    if ids:
        InAppNotification.objects.filter(id__in=ids).update(is_read=True)

    return HttpResponse(html)



from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def mark_as_read(request, pk):
    notif = get_object_or_404(InAppNotification, id=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return HttpResponseRedirect(reverse('inapp_notifications'))

@login_required
def mark_as_unread(request, pk):
    notif = get_object_or_404(InAppNotification, id=pk, user=request.user)
    notif.is_read = False
    notif.save()
    return HttpResponseRedirect(reverse('inapp_notifications'))


from django.shortcuts import render, redirect
from .forms import ReminderForm
from .ai import parse_natural_reminder, rewrite_message_tone
import dateparser
from django.http import HttpResponse

@login_required
def smart_reminder_view(request):
    if request.method == 'POST' and request.POST.get('input'):
        raw_input = request.POST.get('input')
        ai_data = parse_natural_reminder(raw_input)

        # ⏰ Fix parsed time
        raw_time = ai_data.get('datetime')
        parsed_time = dateparser.parse(raw_time) if raw_time else None
        if not parsed_time:
            parsed_time = timezone.now() + timezone.timedelta(minutes=5)

        # ✍️ Rewritten message
        rewritten_message = rewrite_message_tone(ai_data.get('message'), ai_data.get('tone') or 'friendly')

        # 🛡️ Default notify_type
        notify_type = ai_data.get('notify_type') or 'email'

        Reminder.objects.create(
            user=request.user,
            title=ai_data.get('title'),
            message=rewritten_message,
            repeat=ai_data.get('repeat', 'none'),
            send_at=parsed_time,
            notify_type=notify_type,
        )

        if request.headers.get('HX-Request'):
            # HTMX → Tell client to redirect via JS
            response = HttpResponse()
            response['HX-Redirect'] = reverse('reminder_list')
            return response
        else:
            # Normal fallback
            messages.success(request, "✅ Smart reminder created successfully!")
            return redirect('reminder_list')

    return render(request, 'notifications/partials/smart_input_modal.html')
