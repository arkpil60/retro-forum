# Retro Forum 2006 Engine

A lightweight, self-hosted web forum MVP built with Python (Flask) and PostgreSQL 17, designed to mimic the strict tabular structure and environment of mid-2006 forum engines (such as phpBB3 and vBulletin 2.3.6).

## Core Project Feature: Time Capsule
The engine features a dynamic database-level time shift of exactly -20 years (`-7305 days`). Instead of modifying timestamps in the application layer, the PostgreSQL schema shifts the database environment dynamically relative to the current system clock. This ensures the platform continuously operates in a rolling mid-2006 chronological wrapper.

## System Architecture & Tech Stack
- **Backend:** Python 3.13 + Flask.
- **Database:** PostgreSQL 17 (Isolated via `scram-sha-256` authentication).
- **Frontend:** Pure HTML/CSS with zero modern layouts (Flexbox/Grid). Uses strict `<table>` tags for layouts and full page reloads for all actions.
- **Session Management:** Secure cookie-based sessions with password hashing via `werkzeug.security`.
- **Infrastructure:** Containerized via Docker Compose (pgAdmin 4 and Cloudflare Workers proxy setup).
- **Automation:** Cron-managed automated nightly database dumps (`pg_dumpall`) compressed and pushed to a private Telegram channel via Cloudflare Workers.

## Dynamic Themes
Includes a real-time style switcher backed by `localStorage` persistence:
- **Classic Blue:** Traditional phpBB3 gradient style.
- **Yotsuba Green:** Dark-beige legacy imageboard palette inspired by old-school legacy imageboards.

## Directory Structure
```text
forum/
├── docker-compose.yml       # Production pgAdmin 4 environment
├── .gitignore               # Deployment filters
├── LICENSE                  # MIT License
├── README.md                # System documentation
└── backend/
    ├── app.py               # Core application routing & database connection
    ├── templates/           # Jinja2 tabular templates (index, topic, auth)
    └── static/              # Visual assets (style.css, default_avatar.jpg)
```

## Local Development Setup
1. Ensure PostgreSQL 17 is active and a database named `forum_db` is created.
2. Navigate to the backend directory and initialize the virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install Flask psycopg2-binary
   ```
3. Execute the database schema provided in the SQL setup files.
4. Launch the application server:
   ```bash
   python app.py
   ```
