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
| `MONGODB_HOST` | Atlas cluster host (e.g. `cluster0.xxxxx.mongodb.net`) |
| `MONGODB_USER` | Atlas database user (in .env, not in code) |
| `MONGODB_PASSWORD` | Atlas database password (in .env, not in code) |
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
# Collect static files (served by your reverse proxy in production)
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

## 4. Docker deployment (Django + Redis; Mongo = Atlas)

The stack runs in Docker. MongoDB is **Atlas** (no mongo container). Nginx is managed outside this repo.

### What runs in Docker

- **django** – Gunicorn on port 8000; uses Atlas (env), Redis, and the SSR service.
- **redis** – Cache.

### Run locally

```bash
docker compose up -d --build
```

Open `http://localhost:8000`.

### Deploy (production)

1. In `.env` set at least: `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `MONGODB_HOST`, `MONGODB_USER`, `MONGODB_PASSWORD` (Atlas). Optionally `MONGODB_NAME`, `DJANGO_DEBUG`, `SECURE_SSL_REDIRECT`.
2. Build and start:

```bash
docker compose up -d --build
```

3. Point your external reverse proxy at port 8000.

### MongoDB Atlas

Mongo is **not** in Docker; use **MongoDB Atlas**. Set in `.env`:

- `MONGODB_NAME` – database name (e.g. `tzuratlink`)
- `MONGODB_HOST` – Atlas cluster host (e.g. `cluster0.xxxxx.mongodb.net`)
- `MONGODB_USER` – Atlas user
- `MONGODB_PASSWORD` – Atlas password

## 5. Reverse proxy

Nginx (or another reverse proxy) is managed outside this repo. Point it at port 8000 (Gunicorn). Serve `/static/` from `STATIC_ROOT` (after `collectstatic`). For HTTPS set `SECURE_SSL_REDIRECT=true` in `.env`.

## 6. Production readiness

**In place:** Settings from env (no secrets in code), DEBUG default false, security headers when DEBUG=False, Atlas for Mongo, Redis, healthchecks, restart policies.

**Before go-live:**

1. **`.env`** – Set `DJANGO_SECRET_KEY` (random, 50+ chars), `DJANGO_ALLOWED_HOSTS` to your real host(s), and Atlas `MONGODB_HOST` / `MONGODB_USER` / `MONGODB_PASSWORD`.
2. **HTTPS** – Terminate at your reverse proxy and set `SECURE_SSL_REDIRECT=true`.
3. **Optional** – Add tests; pin exact dependency versions if not already.

## 7. Checklist

- [ ] `settings.py` from `settings.example.py`, all secrets from environment
- [ ] `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS` set for production
- [ ] Docker: `docker compose up -d --build`; Atlas vars in `.env`
- [ ] HTTPS terminated at reverse proxy, `SECURE_SSL_REDIRECT=true`
- [ ] Static files served by reverse proxy (after `collectstatic`)
