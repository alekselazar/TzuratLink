# TzuratLink – Production Deployment

## Prerequisites

- Python 3.10+
- Node.js 18+ (for SSR)
- MongoDB
- Redis

## 1. Settings

- Copy `tzuratlink/settings.example.py` to `tzuratlink/settings.py` (or create `settings.py` that mirrors it).
- Copy `.env.example` to `.env` and set values. Do **not** commit `.env` or `settings.py`.

Required environment variables:

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Long random string (e.g. `openssl rand -base64 50`) |
| `DJANGO_DEBUG` | Set to `false` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames (e.g. `tzuratlink.example.com`) |
| `MONGODB_NAME` | MongoDB database name |
| `MONGODB_HOST` | MongoDB connection string (e.g. `mongodb://localhost:27017`) |
| `REDIS_URL` | Redis URL (e.g. `redis://localhost:6379/0`) |
| `SSR_SERVICE_URL` | Base URL of the Node SSR server (e.g. `http://127.0.0.1:3000`) |

## 2. Python app (Django)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

Load env vars (e.g. from `.env` via `python-dotenv` or your process manager), then:

```bash
# Collect static files (served by your web server in production)
python manage.py collectstatic --noinput

# Run with Gunicorn (recommended for production)
gunicorn tzuratlink.wsgi:application --bind 0.0.0.0:8000
```

For local development you can use `python manage.py runserver` and skip Gunicorn.

## 3. Node.js SSR server

The React app is server-side rendered by a small Node server. It must be running for SSR; if it is down, the site falls back to client-side rendering.

```bash
cd node
npm install
node server.js
```

By default it listens on port 3000. Set `SSR_SERVICE_URL` in Django to match (e.g. `http://127.0.0.1:3000` if Django and Node run on the same host).

## 4. Services

- **MongoDB**: Ensure it is running and reachable at `MONGODB_HOST`.
- **Redis**: Ensure it is running and reachable at `REDIS_URL`.

## 5. Reverse proxy (recommended)

Put Gunicorn behind nginx (or another reverse proxy):

- Proxy HTTP to `127.0.0.1:8000` (Gunicorn).
- Serve `/static/` from `STATIC_ROOT` (after `collectstatic`).
- Optionally enable HTTPS and set `SECURE_SSL_REDIRECT=true` and other security headers (see `settings.example.py`).

The Node SSR server is only used by Django internally; it does not need to be exposed to the internet.

## 6. Checklist

- [ ] `settings.py` created from `settings.example.py`, secrets from environment
- [ ] `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS` set
- [ ] MongoDB and Redis running and configured
- [ ] Node SSR server running and `SSR_SERVICE_URL` set
- [ ] `collectstatic` run, static files served by web server
- [ ] Django run with Gunicorn (or equivalent ASGI/WSGI server)
