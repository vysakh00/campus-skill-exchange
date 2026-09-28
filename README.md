# Campus Skill Exchange Platform

A Django and SQLite app for students to list skills, find peer teachers, coordinate learning sessions, and leave feedback. The UI uses Bootstrap 5 with responsive custom styling.

## Requirements

- Python 3.10 or newer
- pip

## Run locally

1. Create and activate a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
2. Install packages: `pip install -r requirements.txt`
3. Create the database tables from the included initial migration: `python manage.py migrate`
4. Add example students and skills: `python manage.py seed_demo` (demo password: `campus-demo`)
5. Create an administrator: `python manage.py createsuperuser`
6. Start the site: `python manage.py runserver` and visit http://127.0.0.1:8000/

## Main pages

- `/` home, `/marketplace/` skill search and category filters
- `/register/`, `/login/`, `/profile/`, `/dashboard/`
- `/requests/`, `/sessions/`, `/notifications/`
- `/admin-dashboard/` staff statistics and `/admin/` content management

Users can create skills to offer or learn, request an offered skill, accept or reject incoming requests, schedule sessions, mark sessions complete, and review their exchange partner. New requests, decisions, and scheduled sessions create notifications.

## Notes

This is a local development configuration. Before deployment, set a private `SECRET_KEY`, turn off `DEBUG`, configure allowed hosts and HTTPS, and use a production database and media storage. Uploaded profile images are served locally in development. Bootstrap and fonts load from CDNs.
