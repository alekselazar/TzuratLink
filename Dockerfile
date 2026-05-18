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

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ ./core/
COPY reader/ ./reader/
COPY templates/ ./templates/
COPY static/ ./static/
COPY tzuratlink/ ./tzuratlink/

# Overwrite any stale committed bundle with the freshly compiled one
COPY --from=bundle-builder /project/static/js/bundle.js ./static/js/bundle.js

RUN python -c "open('manage.py','w').write('''#!/usr/bin/env python\nimport os,sys\nif __name__==\"__main__\":\n  os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\",\"tzuratlink.settings\")\n  from django.core.management import execute_from_command_line\n  execute_from_command_line(sys.argv)\n''')"
RUN test -f tzuratlink/settings.py || cp tzuratlink/settings.example.py tzuratlink/settings.py

EXPOSE 8000
CMD ["sh", "-c", "cp -r /app/static/. /static/ 2>/dev/null || true && python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn tzuratlink.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
