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

## 4. Docker deployment (Nginx + Django + SSR + Redis; Mongo = Atlas)

The stack runs in Docker with **Nginx as gateway and load balancer**. MongoDB is **Atlas** (no mongo container).

### What runs in Docker

- **nginx** – Listens on 80, proxies to Django, serves `/static/` from a shared volume. Upstream is configurable for multiple Django replicas (load balancing).
- **django** – Gunicorn; uses Atlas (env), Redis, and the SSR service.
- **ssr** – Node.js React SSR server (used only by Django).
- **redis** – Cache.

### Run locally (test the full stack + Nginx)

Use this to check that Nginx, Django, SSR, and Redis work together before deploying. **HTTP only** (no HTTPS); the repo’s default `nginx/nginx.conf` is used.

1. **Create `.env`** in the project root (copy from `.env.example`). For a quick local test set at least:
   - `DJANGO_SECRET_KEY=local-test-secret-key-at-least-50-chars-long`
   - `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`
   - `DJANGO_DEBUG=true` (optional, for easier debugging)
   - Your **MongoDB Atlas** values: `MONGODB_HOST`, `MONGODB_USER`, `MONGODB_PASSWORD` (and `MONGODB_NAME` if you use one). Without valid Atlas credentials the app may fail when loading pages that need the DB.

2. **Build and start everything:**

```bash
docker compose up -d --build
```

3. **Open in browser:** [http://localhost](http://localhost)

   You should see the app. Nginx (port 80) is proxying to Django; static files are served by Nginx from the shared volume. To confirm Nginx is in the path, check that the page loads and that `/static/` URLs (e.g. CSS) work.

4. **Logs if something fails:**

```bash
docker compose logs -f nginx
docker compose logs -f django
docker compose logs -f ssr
```

5. **Stop:**

```bash
docker compose down
```

**Nginx config used locally:** `nginx/nginx.conf` (HTTP, port 80). For HTTPS in production you switch to `nginx/nginx-https.conf` and mount certs; see **nginx/README.md**.

**If `/static/` returns 404 (e.g. "No such file or directory" for `reader.css`):** The static volume is empty—often because Django failed before `collectstatic` on first run (e.g. DB or import error). Fix: run collectstatic to fill the volume, then restart nginx:

```bash
docker compose run --rm django python manage.py collectstatic --noinput
docker compose restart nginx
```

Or remove the static volume and bring the stack up again so Django runs collectstatic on start:

```bash
docker compose down
docker volume rm tzuratlink_static_files
docker compose up -d
```

Nginx is set to start only after Django is healthy, so on a clean start the volume should be populated.

### Deploy (production)

1. In `.env` set at least: `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `MONGODB_HOST`, `MONGODB_USER`, `MONGODB_PASSWORD` (Atlas). Optionally `MONGODB_NAME`, `DJANGO_DEBUG`, `SECURE_SSL_REDIRECT`.
2. Build and start:

```bash
docker compose up -d --build
```

3. Open `http://localhost` (or your host). Nginx fronts the app; Django and SSR are not exposed directly.

### Deploy on Hostinger (VPS)

You need a **Hostinger VPS** (not shared hosting). Shared hosting cannot run Docker or this stack.

1. **Order a VPS** at [Hostinger](https://www.hostinger.com/vps-hosting). Choose a plan with at least 1 GB RAM. Optionally use the **Docker VPS template** so Docker and Docker Compose are pre-installed (see [Hostinger: Docker VPS template](https://www.hostinger.com/support/8306612-how-to-use-the-docker-vps-template-at-hostinger/)).

2. **SSH into the VPS** (credentials in the Hostinger panel). If Docker is not installed:
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install -y docker.io docker-compose-v2
   sudo usermod -aG docker $USER
   # Log out and back in, then:
   docker --version && docker compose version
   ```

3. **Upload or clone the project** on the VPS (e.g. in `~/tzuratlink`):
   ```bash
   git clone https://github.com/YOUR_USER/TzuratLink.git ~/tzuratlink
   cd ~/tzuratlink
   ```
   Or upload the project via SFTP (File Manager in hPanel or an SFTP client).

4. **Create `.env`** in the project root (copy from `.env.example` and set real values):
   - `DJANGO_SECRET_KEY` – long random string
   - `DJANGO_ALLOWED_HOSTS` – your domain, e.g. `yourdomain.com,www.yourdomain.com`
   - `MONGODB_HOST`, `MONGODB_USER`, `MONGODB_PASSWORD` – your MongoDB Atlas credentials

5. **Build and start the stack:**
   ```bash
   cd ~/tzuratlink
   docker compose up -d --build
   ```

6. **Point your domain to the VPS**  
   In Hostinger (hPanel): Domains → your domain → DNS / Nameservers. Add an **A record** pointing to your VPS IP (or use the VPS’s default DNS if Hostinger set it).

7. **HTTPS (recommended)**  
   - **Option A:** In Hostinger hPanel, use **SSL** (e.g. Let’s Encrypt) for the domain. If the panel only issues certs for shared hosting, use Option B.  
   - **Option B:** On the VPS, install certbot and issue a certificate for Nginx, then add an HTTPS server block in `nginx/nginx.conf` and set `SECURE_SSL_REDIRECT=true` in `.env`. Reload Nginx after changing the config.

8. **Open the site** at `http://YOUR_VPS_IP` or `http://yourdomain.com`. After SSL, use `https://yourdomain.com`.

**Note:** Hostinger’s **Docker Manager** (in the VPS dashboard) can run Compose from a Git URL; you can point it at your repo and add the same env vars, then deploy. The steps above use the command line for full control.

### Load balancing

To run multiple Django replicas, scale and point Nginx at them:

```bash
docker compose up -d --scale django=2
```

Then in `nginx/nginx.conf`, add a second `server` line in the `upstream backend` block (e.g. `server django_2:8000;` or use the service name if your Compose/Swarm setup resolves it to multiple backends). Reload nginx config if needed.

### MongoDB Atlas

Mongo is **not** in Docker; use **MongoDB Atlas**. Set in `.env`:

- `MONGODB_NAME` – database name (e.g. `tzuratlink`)
- `MONGODB_HOST` – Atlas cluster host (e.g. `cluster0.xxxxx.mongodb.net`)
- `MONGODB_USER` – Atlas user
- `MONGODB_PASSWORD` – Atlas password

## 5. Other services

For non-Docker runs, Django and the Node SSR server run on the host; see sections 2 and 3.

## 6. Reverse proxy (recommended)

Put Gunicorn behind nginx (or another reverse proxy):

- Proxy HTTP to `127.0.0.1:8000` (Gunicorn).
- Serve `/static/` from `STATIC_ROOT` (after `collectstatic`).
- Optionally enable HTTPS and set `SECURE_SSL_REDIRECT=true` and other security headers (see `settings.example.py`).

The Node SSR server is only used by Django internally; it does not need to be exposed to the internet.

## 7. Production readiness

**In place:** Settings from env (no secrets in code), DEBUG default false, security headers when DEBUG=False, Docker stack with Nginx, Atlas for Mongo, Redis, static via Nginx, healthchecks, restart policies.

**Before go-live:**

1. **`.env`** – Set `DJANGO_SECRET_KEY` (random, 50+ chars), `DJANGO_ALLOWED_HOSTS` to your real host(s) (e.g. `yourdomain.com`), and Atlas `MONGODB_HOST` / `MONGODB_USER` / `MONGODB_PASSWORD`. Do not use the default `SECRET_KEY` from settings.example.
2. **HTTPS** – Use `nginx/nginx-https.conf`, mount SSL certs, expose 443, and set `SECURE_SSL_REDIRECT=true`. Step-by-step: **nginx/README.md** (certbot, mount certs, reload).
3. **Optional** – Add tests; pin exact dependency versions if not already; consider rate limiting and logging.

## 8. Checklist

- [ ] `settings.py` from `settings.example.py`, all secrets from environment
- [ ] `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS` set for production
- [ ] Docker: `docker compose up -d --build`; Atlas vars in `.env`
- [ ] HTTPS in front of Nginx (or plan for it)
- [ ] Static files served (Nginx in Docker handles this)
