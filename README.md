# RoutineX

**Personal Life Operating System** — a premium habit, study, and routine tracker built with Flask.

Track your daily routine, study sessions, streaks, and progress — all in one clean, installable web app.

## Features

- 📅 **Daily Logging** — Track morning/evening routines, skincare, hydration, meals, mood, and journal entries (one entry per day, auto-updates instead of duplicating)
- 🔥 **Streak System** — Current streak + best streak tracking based on consistent daily logging
- 📊 **Analytics Dashboard** — Weekly and monthly completion rates, water intake averages, mood trends, and visual charts
- 📝 **Auto-Save Drafts** — Form data saves automatically as you type and restores if you leave and come back
- 📚 **Study Tracker** — Log study sessions with subject, topic, and time blocks
- 🗒️ **Planner** — Add and track assignments/tasks with submission deadlines and priority
- ⬇️ **Data Export** — Download your full data backup as JSON or CSV anytime
- 📱 **PWA Support** — Installable on mobile/desktop with offline support via service worker
- 🎨 **Premium Dark UI** — Glassmorphism design with neon purple/cyan accents

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Charts:** Chart.js
- **PWA:** Service Worker + Web App Manifest

## Project Structure

```
RoutineX/
├── app.py                  # Flask app, routes, database logic
├── requirements.txt        # Python dependencies
├── Procfile                # Render/Heroku deployment config
├── database.db              # SQLite database (auto-created on first run)
├── static/
│   ├── css/
│   │   └── style.css       # App-wide stylesheet
│   ├── js/
│   │   ├── script.js       # Frontend logic, autosave, streaks
│   │   └── sw.js           # Service worker for PWA/offline support
│   ├── icons/               # PWA app icons
│   └── manifest.json        # PWA manifest
└── templates/
    ├── index.html           # Landing page
    ├── dashboard.html       # Main daily tracker
    ├── planner.html         # Task/assignment planner
    ├── analytics.html       # Weekly/monthly analytics
    └── offline.html         # PWA offline fallback page
```

## Live link: https://routinex-0282.onrender.com

## Author

Built and maintained by Niranjana.
```
