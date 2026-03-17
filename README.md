# SyllabusEngine

SyllabusEngine is an AI-powered study planning web app built with Flask. It helps students turn raw syllabus PDFs into structured weekly plans, track progress, and manage study tasks from a single dashboard.

## What it does

- Authentication for students and admin users
- Upload and parse syllabus PDFs
- Generate AI-assisted study plans
- Weekly view, progress tracking, and calendar support
- Admin dashboard for user and parsing management

## Tech stack

- Python 3.11
- Flask, Flask-Login, Flask-SQLAlchemy
- SQLAlchemy
- Gunicorn
- Groq API

## Clone and run locally

### 1) Clone repository

```bash
git clone https://github.com/Code-With-Topper/SyllabusEngine.git
cd SyllabusEngine
```

### 2) Create and activate virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Create environment file

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=sqlite:///syllabus_engine.db
GROQ_API_KEY=your_groq_api_key
SENDGRID_API_KEY=
MAIL_FROM=noreply@syllabus-engine.com
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### 5) Start the app

```bash
python app.py
```

or

```bash
flask --app app.py run --debug
```

App URL: `http://127.0.0.1:5000`

## Production run command

```bash
gunicorn "app:create_app()" --workers 2 --bind 0.0.0.0:$PORT --timeout 120
```

## Deploy on Render

This repository includes `render.yaml` for Blueprint deployment.

### Option A: Blueprint (recommended)

1. Push latest code to GitHub.
2. In Render, select New -> Blueprint.
3. Connect this repository.
4. Render will create the web service and database from `render.yaml`.

### Option B: Manual setup

- Environment: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn "app:create_app()" --workers 2 --bind 0.0.0.0:$PORT --timeout 120`

Required environment variables:

- `SECRET_KEY`
- `GROQ_API_KEY`
- `DATABASE_URL`
- `PYTHON_VERSION=3.11`

## Default admin account

On first startup, the app seeds a default admin if not present.

- Email: `soumya@admin.com`
- Name: `Soumya`

Change the default admin password immediately after first login in production.

## Project layout

```text
SyllabusEngine/
|- app.py
|- main.py
|- config.py
|- extensions.py
|- requirements.txt
|- render.yaml
|- ai/
|- database/
|- pdf/
|- routes/
|- static/
|- templates/
`- uploads/
```

## Common commands

Run local server:

```bash
python app.py
```

Run with Gunicorn locally:

```bash
gunicorn "app:create_app()" --bind 127.0.0.1:8000 --workers 2
```

Update pinned dependencies:

```bash
pip freeze > requirements.txt
```

## Troubleshooting

Install/build failures on deploy:

- Keep Python pinned to 3.11 (`.python-version` and `PYTHON_VERSION`).
- Re-deploy after updating dependencies.

Duplicate admin messages during startup:

- Expected with multi-worker boot.
- Startup seeding is protected against race conditions.

Database connection issues:

- Verify `DATABASE_URL` is set correctly.
- On Render, map it from the managed PostgreSQL service.

## Security checklist

- Use a strong `SECRET_KEY`.
- Change default admin credentials.
- Keep sensitive keys only in environment variables.
- Review logs and restrict admin access.

## License

Add a `LICENSE` file (MIT, Apache-2.0, or your preferred license).
