# Student Attendance Management System

A small educational Flask application for maintaining student records, recording daily attendance, calculating attendance percentages, and exporting a CSV report.

## Features
- Add student records with a unique roll number.
- Record or update daily attendance (Present, Absent, Late, Excused).
- Calculate attendance percentage (`Present + Late / Recorded sessions × 100`).
- Identify students below a configurable attendance threshold.
- View a summary dashboard and export reports as CSV.
- SQLite persistence, automated tests, and optional Docker support.

## Requirements
- Python 3.10 or later
- pip
- Optional: Docker and Docker Compose

## Run locally
```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; optional
python app.py
```
Open http://127.0.0.1:5000.

Set `SECRET_KEY` to a strong random value before deployment. For local testing, the app can run without a `.env` file. Environment variables are read from the process environment; install `python-dotenv` if you want automatic `.env` loading, or set variables in your shell.

## Tests
```bash
pytest -v
```

## Docker
```bash
docker compose up --build
```
Open http://127.0.0.1:5000. Compose stores the database in a named volume.

## Main routes
- `/` — dashboard
- `/students` — add/list students
- `/attendance` — record attendance
- `/reports` — percentage report
- `/reports.csv` — download CSV report

## Repository layout
- `app.py` — Flask routes and app factory
- `database.py` — SQLite connection, schema, and seed data
- `models.py` — attendance calculations and summary logic
- `templates/` — HTML templates
- `static/` — CSS and JavaScript
- `tests/` — automated tests
- `.github/workflows/` — continuous integration workflow

## Limitations and future work
This educational starter does not implement authentication or role-based access. Do not use real student personal data or deploy publicly without adding authentication, authorization, CSRF protection, stronger validation, backups, and production configuration.
