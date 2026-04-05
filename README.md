# ExpenseFlow

ExpenseFlow is a Django-based personal finance app with:

- wallet-style saved cards
- expense and credit tracking
- automatic category detection from expense titles
- per-card balance tracking
- protected card detail reveal using your account password

## Features

- User accounts with login and signup
- Apple Pay-inspired card wallet UI
- Bank-based card themes
- Card network detection such as Visa and Mastercard
- Starting balance support for cards
- Credit and debit transaction tracking
- Auto-categorization for common expense titles
- Secure note field for each card
- Swipe-to-delete card interaction

## Tech Stack

- Python
- Django 5
- SQLite for local development
- PostgreSQL for production on Render
- HTML, CSS, and JavaScript

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver
```

6. Open:

```text
http://127.0.0.1:8000/
```

## Deploy To Render With PostgreSQL

This project is already prepared for Render with:

- `render.yaml` for infrastructure setup
- `gunicorn` for production serving
- `whitenoise` for static files
- `dj-database-url` for parsing `DATABASE_URL`
- PostgreSQL support through `psycopg`

### Option 1: Recommended Automatic Deploy With `render.yaml`

1. Push this project to GitHub.
2. Sign in to Render.
3. Click `New +`.
4. Choose `Blueprint`.
5. Connect your GitHub repository.
6. Select this repository.
7. Render will detect `render.yaml`.
8. Confirm the blueprint creation.
9. Render will create:
   - one web service named `expenseflow`
   - one PostgreSQL database named `expenseflow-db`
10. Wait for the first deploy to finish.

Render uses these commands from the repo:

- Build command: `bash build.sh`
- Start command: `gunicorn config.wsgi:application`

During build, Render will:

- install Python packages
- collect static files
- run database migrations
- create a superuser automatically if `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD` are set

### Option 2: Manual Render Setup

If you do not want to use the blueprint file, create the resources manually:

1. Push the repository to GitHub.
2. In Render, create a new `PostgreSQL` database.
3. After the database is ready, copy its `External Database URL` or use the internal connection string Render provides to the web service.
4. Create a new `Web Service`.
5. Connect the same GitHub repo.
6. Set:
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn config.wsgi:application`
7. Add environment variables:
   - `DJANGO_SECRET_KEY` = any long random secret
   - `DEBUG` = `False`
   - `DATABASE_URL` = your Render PostgreSQL connection string
   - `ALLOWED_HOSTS` = `.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` = `https://your-service-name.onrender.com`
   - `DJANGO_SUPERUSER_USERNAME` = your admin username
   - `DJANGO_SUPERUSER_EMAIL` = your admin email
   - `DJANGO_SUPERUSER_PASSWORD` = your admin password
8. Save and deploy.

## How The Production Config Works

### Database

- Local development uses SQLite when `DATABASE_URL` is not set.
- Render production uses PostgreSQL automatically when `DATABASE_URL` exists.

### Static Files

- Django collects static files into `staticfiles/`.
- WhiteNoise serves them directly from the Django app.
- No separate storage service is required for CSS and JavaScript.

### Security

- `DEBUG` is off in production.
- HTTPS headers are trusted behind Render's proxy.
- secure cookies are enabled when `DEBUG=False`.

## Important Deployment Notes

1. On Render free tier there is no shell for web services, so the project can create the superuser automatically during deploy when these environment variables are set:

```text
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD
```

2. If you later change models, commit the new migration files and redeploy.

3. If your Render URL changes, update:

- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

4. The free Render plan may spin down after inactivity.

## Files Added For Deployment

- `render.yaml`
- `build.sh`
- `.env.example`

## Repository

GitHub remote:

```text
https://github.com/mohammed-rihan-c-234/My_Pay.git
```
