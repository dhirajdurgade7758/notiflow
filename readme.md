# Notiflow 🔔 AI-Powered Voice & Smart Reminder System

## 🎥 Project Demo (YouTube)

[![Watch the demo](https://img.youtube.com/vi/gUYD-nBeeJw/maxresdefault.jpg)](https://youtu.be/gUYD-nBeeJw)

> 🚀 Click above to watch the full project demo, system design explanation, and live walkthrough.

---

Notiflow is a comprehensive Django application that combines scheduled tasks, multi-channel notifications, AI capabilities, and **voice-activated controls**. It helps users stay productive by creating reminders via **voice commands**, **email**, **in-app alerts**, and **SMS**, powered by **Celery, Redis**, **Google Gemini AI**, and **Web Speech API**.

## ✨ Key Features

### 🎤 Voice-Activated Smart Reminders (NEW!)

- **"Okay Flow" Wake Word Detection** - Say "Okay Flow" to activate voice reminder creation
- **Natural Speech Recognition** - Speak reminder details naturally
  - Example: *"Remind me to call mom tomorrow at 5 PM"*
  - Example: *"Buy groceries day after tomorrow morning"*
  - Example: *"Team meeting next Monday at 10 AM"*
- **Fuzzy Matching Algorithm** - Handles speech recognition variations using Levenshtein distance
  - 65% similarity threshold for wake word detection
  - Handles variations: "okay flo", "o flow", "okay flow", etc.
- **Real-Time Transcript Display** - Shows recognized text as you speak
- **Text-to-Speech Confirmation** - AI confirms the reminder by speaking it back

### 🔔 Real-Time In-App Notification Alerts (NEW!)

- **Notification Sound** - Plays beep alert using Web Audio API when reminder triggers
- **Spoken Reminders (4x Repetition)** - Message is spoken 4 times with counter display
  - Display: "🔊 Speaking... (1/4)" progresses to "(4/4)"
  - 800ms delay between repetitions for clarity
- **Stop Button** - Instantly stop sound and speech synthesis
- **Snooze Button (5 min)** - Snooze with automatic confirmation speech
- **Auto-Dismiss** - Automatically closes after 30 seconds if not interacted
- **Beautiful Gradient Modal** - Purple gradient popup with animated bell emoji
  - Fully responsive design
  - Centered on screen with backdrop blur effect

### 🧠 AI-Powered Date/Time Parsing (Enhanced)

- **Context-Aware Date Calculation** - LLM considers current date and time
  - Understands: "tomorrow", "day after tomorrow", "next week", "next Monday"
  - Handles specific dates: "April 15", "next month on the 1st"
  - Auto-calculates: Today's date, weekday names, relative dates
- **Relative Date Support** with examples provided to LLM:
  - *"today"* → YYYY-MM-DD
  - *"tomorrow"* → Next calendar day
  - *"day after tomorrow"* → +2 days
  - *"next week"* → +7 days
  - *"next Monday"* → Next occurrence of Monday
- **Time Format Support**:
  - Spoken times: "5 PM", "3:30 PM", "twenty past five"
  - Duration: "in 30 minutes", "in 2 hours"
  - Named times: "noon", "midnight", "morning", "evening"
- **ISO 8601 Format** - All datetimes stored as YYYY-MM-DDTHH:MM:SS
- **Default Time Handling** - 9:00 AM if only date specified

### AI Automation

- **Natural Language Reminder Parser** - Convert spoken text to structured reminders
- **Tone-Adjusted Reminders** - LLM rewrites in friendly/formal/motivational tone
- **Extract Action & Message** - Intelligently separates task from metadata
- **Recurring Reminders** - Support for daily, weekly, monthly, yearly repeat patterns

### 📬 Multi-Channel Notifications

- **Email Notifications** - SMTP integration with custom templates
- **In-App Notifications** - Real-time alerts with sound and speech
- **SMS Notifications** - Twilio API integration

### ⏱️ Scheduling System (Celery + Beat)

- One-time or recurring reminders (daily, weekly, monthly)
- Celery Beat periodic tasks:
  - Weekly analytics email
  - Failed job retries with exponential backoff
  - Reminder cleanup and archival
- Task retry logic with detailed failure tracking
- Task monitoring and status updates

### 📊 Admin & Monitoring

- Admin dashboard showing all user reminders
- Weekly analytics and usage reports
- Reminder history with filtering
- Failure logs with error details
- Auto-alerts to admins for critical failures
- Flower dashboard for real-time Celery task monitoring

### 🔗 REST API with Session & Token Auth

- `GET /api/notifications/unread/` - Real-time alert polling
- `POST /api/notifications/<id>/read/` - Mark notification as read
- `POST /api/notifications/<id>/unread/` - Mark as unread
- `POST /api/reminders/snooze/` - Create snoozed reminder
- `POST /api/reminders/<id>/cancel/` - Cancel scheduled reminder
- Supports both Token Authentication and Session Authentication

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 5.1, Celery, Celery Beat |
| **Frontend** | HTML5, Bootstrap 5, HTMX, Alpine.js, Tailwind CSS |
| **Voice** | Web Speech API (Chrome, Edge, Safari) |
| **Audio** | Web Audio API (Notification sounds) |
| **Database** | PostgreSQL 17 (fallback: SQLite3) |
| **Queue** | Redis 7+ |
| **AI** | Google Gemini 2.5-flash API |
| **Email** | SMTP (Gmail/custom provider) |
| **SMS** | Twilio API |
| **Monitoring** | Flower (Celery UI) |
| **DevOps** | Docker, Docker Compose, Gunicorn, WhiteNoise |
| **Auth** | django-allauth (social + email auth) |
| **API** | Django REST Framework with Token Auth |

## 📂 Project Structure

```
notiflow/
├── notifications/               # Core app
│   ├── models.py               # Reminder, InAppNotification, AISuggestion
│   ├── views.py                # Dashboard, smart reminder, notifications
│   ├── api_views.py            # REST endpoints for real-time polling
│   ├── api_urls.py             # API routing
│   ├── ai.py                   # LLM integration (Gemini API)
│   ├── tasks.py                # Celery tasks for email/SMS/in-app
│   ├── templates/notifications/
│   │   ├── base.html           # Main base with voice assistant + alert system
│   │   ├── dashboard.html      # User dashboard
│   │   └── partials/           # HTMX components
│   └── migrations/             # Database migrations
├── a_users/                     # User auth & profiles
│   ├── models.py               # User profile with avatar, phone
│   └── signals.py              # Auto-create profile on user creation
├── notiflow/                    # Project settings
│   ├── settings.py             # Django config
│   ├── celery.py               # Celery config
│   ├── urls.py                 # Main URL routing
│   └── wsgi.py                 # WSGI entry point
├── templates/                   # Global templates
│   ├── base.html               # Auth pages base
│   └── account_base.html       # Account/allauth base
├── static/                      # CSS, images, fonts
├── docker-compose.yml          # Multi-container setup
├── Dockerfile                  # Container image
├── manage.py                   # Django CLI
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/notiflow.git
cd notiflow

# Build and start all services
docker-compose up -d

# Services will be available at:
# - Django: http://localhost:8001
# - Flower (Celery): http://localhost:5555 (admin/password123)
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379

# Run migrations
docker-compose exec app python manage.py migrate

# Create superuser
docker-compose exec app python manage.py createsuperuser

# View logs
docker-compose logs -f app
```

### Local Development Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file with required variables
cp .env.example .env
# Edit .env with your API keys

# Setup database
python manage.py migrate

# Start Redis server (in separate terminal)
redis-server

# Start Django development server (in separate terminal)
python manage.py runserver

# Start Celery worker (in separate terminal)
celery -A notiflow worker --loglevel=info

# Start Celery Beat scheduler (in separate terminal)
celery -A notiflow beat --loglevel=info

# Create superuser
python manage.py createsuperuser
```

## 🔑 Environment Variables (.env)

```env
# Django
SECRET_KEY=your-very-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,yourdomain.com

# Database (Optional - uses SQLite by default)
DATABASE_URL=postgresql://user:password@localhost:5432/notiflow

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=notiflow@example.com

# Redis & Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890

# Google Gemini AI (for LLM)
GEMINI_API_KEY=AIzaSy...

# Django Allauth
SOCIALACCOUNT_PROVIDERS={...}  # Optional social auth
```

## 🎤 How to Use Voice Features

### Creating a Reminder via Voice

1. **Click "🎤 Okay Flow" button** in the header navbar
2. **Say "Okay Flow"** to activate voice mode
3. A beautiful gradient modal appears saying *"Listening for Reminder..."*
4. **Speak your reminder naturally**, such as:
   - "Remind me to drink water tomorrow at 9 AM"
   - "Call mom day after tomorrow"
   - "Team meeting next Monday at 10 AM"
5. **The AI processes your speech** and extracts:
   - Title/Action: "Drink water"
   - Time: Tomorrow, 09:00 AM (ISO 8601 format)
   - Notification type: "inapp" (default)
6. **Confirmation speech** plays back: *"Perfect! I'll remind you to drink water tomorrow at 9 AM"*
7. Modal closes and reminder is created

### Receiving In-App Alerts

When a reminder triggers at scheduled time:

1. **Beep sound** plays from Web Audio API
2. **Beautiful modal appears** with reminder title and message
3. **Message is spoken 4 times**:
   - Display shows: "🔊 Speaking... (1/4)" → "(4/4)"
   - 800ms pause between repetitions
4. **Two action buttons**:
   - **✋ Stop** - Stops audio immediately, closes modal
   - **😴 Snooze 5 min** - Marks as read, speaks "Reminder snoozed for 5 minutes"
5. **Auto-dismiss** after 30 seconds without interaction

## 📊 Sample Natural Language Inputs

```
"Remind me to take a break every day at 4 PM"
"Set a weekly status update reminder next Monday 10 AM"
"Call the dentist in 2 weeks at 3 PM"
"Review goals monthly on the 1st in a formal tone"
"Morning workout tomorrow at 6 AM in a motivational tone"
"Team meeting day after tomorrow at 2 PM"
"Pay bills next Friday in a gentle tone"
"Learn JavaScript in 30 minutes"
```

## 🔌 REST API Endpoints

### Notifications (Real-Time Polling)

```bash
# Get unread notifications (for alert system polling)
GET /api/notifications/unread/
Authorization: Token YOUR_TOKEN or Session

Response:
{
  "count": 2,
  "notifications": [
    {
      "id": 1,
      "title": "Reminder: Take a break",
      "message": "You've been working for 2 hours...",
      "is_read": false,
      "created_at": "2026-04-08T10:30:00Z"
    },
    ...
  ]
}

# Mark as read
POST /api/notifications/{id}/read/

# Mark as unread
POST /api/notifications/{id}/unread/
```

### Reminders

```bash
# Snooze a reminder (create new reminder 5 min later)
POST /api/reminders/snooze/
{
  "reminder_id": "uuid-string",
  "snooze_minutes": 5
}

# Cancel reminder
POST /api/reminders/{id}/cancel/
```

## 🌐 Browser Support

- Chrome 25+ ✓ (Full support)
- Edge 79+ ✓ (Full support)
- Safari 14.1+ ✓ (Full support)
- Firefox 25+ ✓ (Limited - Speech Synthesis works, Speech Recognition needs flag)

## 📱 Responsive Design

- Mobile-first Bootstrap design
- Adapts to all screen sizes
- Touch-friendly voice button
- Mobile notification alerts work on all browsers

## 🔐 Security Features

- CSRF protection on all forms
- Session authentication with secure cookies
- Token authentication for API clients
- Input validation and sanitization
- SQL injection prevention (Django ORM)
- XSS protection with template escaping
- Rate limiting on API endpoints (configurable)

## 📈 Performance Optimizations

- Asynchronous task processing with Celery
- Redis caching for frequently accessed data
- Database indexes on commonly filtered fields
- Static file compression with WhiteNoise
- Lazy loading of notification polls (2-second interval)
- Efficient fuzzy matching algorithm (O(n*m) complexity)

## 🐛 Debugging & Monitoring

### View Celery Tasks in Flower

```
http://localhost:5555/
Username: admin
Password: password123
```

### View Django Logs

```bash
# In Docker
docker-compose logs -f app

# Locally
python manage.py runserver  # Shows request logs
```

### Check API Logs

```bash
# Enable Django DEBUG in .env
DEBUG=True

# All API requests will be logged to console
```

## 🎯 Use Cases

1. **Daily Wellness Reminders** - "Take your medicine at 8 AM every day"
2. **Meeting Alerts** - "Team standup tomorrow at 9:30 AM with Slack notification"
3. **Task Reminders** - "Call John next Friday at 2 PM"
4. **Event Reminders** - "Anniversary day after tomorrow"
5. **Habit Tracking** - "Workout daily at 6 AM in motivational tone"
6. **Payment Reminders** - "Pay bills on the 1st of every month"
7. **Appointment Alerts** - "Doctor appointment next month"
8. **Smart Notifications** - Receive alerts via email, SMS, or in-app

## 📚 API Documentation

Full API documentation available at:
- Swagger UI: `/api/schema/swagger/` (when DEBUG=False)
- ReDoc: `/api/schema/redoc/`

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Author

**Dhiraj Durgade**
- Full Stack Developer | Python | Django | JavaScript
- LinkedIn: https://www.linkedin.com/in/dhiraj-durgade/
- GitHub: https://github.com/dhirajdurgade7758

## 🙏 Acknowledgments

- Django community for the excellent framework
- Google Gemini for powerful LLM capabilities
- Web Speech API for voice features
- Bootstrap for responsive design
- Celery & Redis for background tasks

## ⭐ Star & Follow

If you find this project useful, please give it a ⭐ and follow for updates!

---

## 🔄 Recent Updates (v2.0)

### New in This Release

- ✅ Voice-activated "Okay Flow" wake word detection
- ✅ Real-time in-app notification alerts with sound
- ✅ Text-to-speech confirmation messages (4x repetition)
- ✅ Fuzzy matching algorithm for speech recognition
- ✅ Enhanced LLM prompt with context-aware date parsing
- ✅ REST API endpoints for real-time polling
- ✅ Session + Token authentication support
- ✅ Snooze and stop buttons for notifications
- ✅ Auto-dismiss alerts after 30 seconds

### Roadmap (v3.0)

- [ ] Recurring voice reminders ("Every Monday at 10 AM")
- [ ] Timezone aware reminders
- [ ] Voice command for other actions (mark read, delete, etc.)
- [ ] Mobile app with Cordova/React Native
- [ ] WebSocket support for live notifications
- [ ] Analytics dashboard for reminder patterns
- [ ] Machine learning for smart reminder suggestions
- [ ] Multi-language support
- [ ] Calendar integration (Google Calendar, Outlook)

---

Last Updated: April 2026
