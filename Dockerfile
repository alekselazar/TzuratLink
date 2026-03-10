# TzuratLink – Django app (Gunicorn)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY core/ ./core/
COPY reader/ ./reader/
COPY templates/ ./templates/
COPY static/ ./static/
COPY tzuratlink/ ./tzuratlink/

# manage.py is often gitignored – create default (overwrite with COPY in CI if you add it to repo)
RUN python -c "open('manage.py','w').write('''#!/usr/bin/env python\nimport os,sys\nif __name__==\"__main__\":\n  os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\",\"tzuratlink.settings\")\n  from django.core.management import execute_from_command_line\n  execute_from_command_line(sys.argv)\n''')"
RUN test -f tzuratlink/settings.py || cp tzuratlink/settings.example.py tzuratlink/settings.py

EXPOSE 8000
# Copy static into volume first, then migrate, collectstatic, gunicorn (all in Docker CMD)
CMD ["sh", "-c", "cp -r /app/static/. /static/ 2>/dev/null || true && python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn tzuratlink.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
