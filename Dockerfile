# ── Stage 1: build webpack bundle ────────────────────────
FROM node:20-alpine AS bundle-builder
WORKDIR /project
# Install deps (needs devDependencies for webpack/babel)
COPY node/package.json ./node/
RUN cd node && npm install
# Copy source so webpack can resolve relative paths correctly
COPY node/ ./node/
# webpack outputs to ../../static/js relative to node/webpack/ → /project/static/js
RUN mkdir -p static/js && cd node && npm run build

# ── Stage 2: Django app (Gunicorn) ───────────────────────
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Baked into the image at build time so the container has them regardless of how
# it's started (no -e flags required from whatever pulls/runs this image).
ARG DJANGO_SECRET_KEY=""
ARG DJANGO_DEBUG="false"
ARG DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
ARG SITE_URL="http://localhost:8000"
ARG MONGODB_NAME="tzuratlink"
ARG MONGODB_HOST=""
ARG MONGODB_USER=""
ARG MONGODB_PASSWORD=""
ARG REDIS_URL=""
ARG SSR_SERVICE_URL=""
ARG SECURE_SSL_REDIRECT="false"
ARG GOOGLE_CLIENT_ID=""
ARG GOOGLE_CLIENT_SECRET=""
ARG GDRIVE_BACKUP_FOLDER_ID=""
ARG GDRIVE_CREDENTIALS=""

ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} \
    DJANGO_DEBUG=${DJANGO_DEBUG} \
    DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} \
    SITE_URL=${SITE_URL} \
    MONGODB_NAME=${MONGODB_NAME} \
    MONGODB_HOST=${MONGODB_HOST} \
    MONGODB_USER=${MONGODB_USER} \
    MONGODB_PASSWORD=${MONGODB_PASSWORD} \
    REDIS_URL=${REDIS_URL} \
    SSR_SERVICE_URL=${SSR_SERVICE_URL} \
    SECURE_SSL_REDIRECT=${SECURE_SSL_REDIRECT} \
    GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID} \
    GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET} \
    GDRIVE_BACKUP_FOLDER_ID=${GDRIVE_BACKUP_FOLDER_ID} \
    GDRIVE_CREDENTIALS=${GDRIVE_CREDENTIALS}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ ./core/
COPY reader/ ./reader/
COPY accounts/ ./accounts/
COPY templates/ ./templates/
COPY static/ ./static/
COPY tzuratlink/ ./tzuratlink/

# Overwrite any stale committed bundle with the freshly compiled one
COPY --from=bundle-builder /project/static/js/bundle.js ./static/js/bundle.js

RUN python -c "open('manage.py','w').write('''#!/usr/bin/env python\nimport os,sys\nif __name__==\"__main__\":\n  os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\",\"tzuratlink.settings\")\n  from django.core.management import execute_from_command_line\n  execute_from_command_line(sys.argv)\n''')"
RUN test -f tzuratlink/settings.py || cp tzuratlink/settings.example.py tzuratlink/settings.py

EXPOSE 8000
CMD ["sh", "-c", "cp -r /app/static/. /static/ 2>/dev/null || true && python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn tzuratlink.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
