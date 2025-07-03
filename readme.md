# 🔔 Notiflow – AI-Powered Smart Reminder & Notification System

Notiflow is a **production-ready Django project** that combines real-time notifications, scheduled tasks, and AI capabilities. It helps users stay productive by automating reminders via **email**, **in-app**, and **SMS**, powered by **Celery, Redis**, and **LLMs (LLaMA3 via Groq)**.

---

## 🚀 Features

### 💡 AI Automation

* 🤖 **Natural Language Reminder Parser** (e.g. “Remind me to drink water daily at 9 AM”)
* ✍️ **Tone-Adjusted Reminders** using LLM (rewrite in friendly/formal tone)
* 🧠 **Weekly Smart Suggestions** via AI (analyzes your usage + suggests habits)

### 📬 Multi-Channel Notifications

* ✉️ Email Notifications (via SMTP)
* 🔔 In-App Real-time Alerts (via Django Channels + Redis + HTMX)
* 📱 SMS Notifications (Twilio Integration)

### ♻️ Scheduling System (Celery + Beat)

* ⏰ Schedule reminders one-time or recurring (daily, weekly, monthly)
* 🗕 Celery Beat for periodic tasks like:

  * Weekly analytics
  * Failed job retries
  * Reminder cleanup
* 🧪 Retry logic, task monitoring, failure alerts

### 🛠 Admin & Monitoring

* 🤩 Admin dashboard for all user reminders
* 📊 Weekly analytics for users via email
* 🗜 Reminder history tab
* 🔍 Logs for failures with auto-alert to admins

### ⚙️ Technology Stack

| Stack    | Tools Used                                   |
| -------- | -------------------------------------------- |
| Backend  | Django, Django Channels, Celery, Celery Beat |
| Database | PostgreSQL / SQLite                          |
| Queue    | Redis                                        |
| Realtime | WebSockets + HTMX                            |
| AI Layer | Groq LLaMA 3 (via API)                       |
| Email    | SMTP + Gmail                                 |
| SMS      | Twilio API                                   |
| DevOps   | Docker, Whitenoise, Gunicorn-ready           |
| Auth     | AllAuth + Custom Authentication App          |

---

## 📸 Demo Screenshots

| Screenshot                                                  | Description                                                          |
| ----------------------------------------------------------- | -------------------------------------------------------------------- |
| ![User Dashboard](screenshots/user_dashboard.png)           | 👤 **User Dashboard** – Overview of reminders, alerts, and activity  |
| ![Admin Dashboard](screenshots/admin_dashboard.png)         | 🛠️ **Admin Panel** – Monitor all user reminders and failures         |
| ![Smart Reminder](screenshots/smart_reminder.png)           | 🤖 **AI Reminder Creation** – Natural language input + LLM rewriting |
| ![Reminder List](screenshots/reminder_list.png)             | 📋 **Reminder List View** – Upcoming and past reminders              |
| ![In-App Toasts](screenshots/inapp_toast.png)               | 🔔 **In-App Toasts** – Real-time alerts via WebSocket & HTMX         |
| ![In-App Notification](screenshots/inapp_notifications.png) | 🔔 **In-App Notification** – list of all inapp notifications         |
| ![Reminder History](screenshots/reminder_history.png)       | 📜 **History Tab** – Log of all completed and failed reminders       |
| ![Reminder Form](screenshots/reminder_form.png)             | ✍️ **Manual Reminder Form** – Traditional form-based entry           |

---

## ⚙️ Project Setup (Development)

```bash
git clone https://github.com/dhirajdurgade7758/notiflow.git
cd notiflow

# Setup virtualenv
python -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Load environment variables
cp .env.example .env  # then edit with your API keys & credentials

# Run migrations
python manage.py migrate

# Start Redis (must be running)
redis-server

# Run Django + Celery workers
python manage.py runserver
celery -A notiflow worker --loglevel=info
celery -A notiflow beat --loglevel=info

# Access admin
python manage.py createsuperuser
```

---

## 🔐 Environment Variables (`.env`)

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Email
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=yourpassword

# Redis / Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# AI - Groq LLaMA 3
GROQ_API_KEY=sk-...
```

---

## 🧪 Sample Natural Language Prompts

> ✅ “Remind me to take a break every day at 4 PM in a friendly tone”
> ✅ “Set a weekly status update reminder next Monday 10 AM”
> ✅ “I want to review goals monthly on the 1st in a formal tone”

---

## 📈 Showcase Use Cases

* 🗕 Task scheduling & deadline reminders
* 🢘 Wellness nudges via AI (hydration, posture, breaks)
* 💬 Realtime customer support systems (extendable)
* 🧪 Background job & queue orchestration demo

---

## 👨‍💻 Author

> **Dhiraj Durgade**
> Python • Django • Full Stack Dev
> [LinkedIn](https://www.linkedin.com/in/dhiraj-durgade/) • [GitHub](https://github.com/dhirajdurgade7758)

---

## ⭐️ Want to Contribute?

* Clone this repo
* Create a feature branch
* Submit a PR 🚀

---

## 🛆 Production Notes

* Dockerized & Gunicorn-ready
* Celery Beat scheduler for retry, cleanup, auto-reporting
* HTMX used for reactive alerts without heavy JS
* LLM-backed AI utilities via Groq or OpenAI
