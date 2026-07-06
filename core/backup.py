import os
import datetime
import json
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

LATEST_NAME = 'tzuratlink-latest.db'


def _drive_service():
    from googleapiclient.discovery import build
    from google.oauth2 import service_account

    creds_json = os.environ.get('GDRIVE_CREDENTIALS', '')
    if not creds_json:
        raise EnvironmentError('GDRIVE_CREDENTIALS env var is not set.')
    try:
        creds_info = json.loads(creds_json)
    except json.JSONDecodeError as e:
        raise ValueError(f'GDRIVE_CREDENTIALS is not valid JSON: {e}') from e
    creds = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=['https://www.googleapis.com/auth/drive.file'],
    )
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


def _find_file(service, name, folder_id):
    resp = service.files().list(
        q=f"name='{name}' and '{folder_id}' in parents and trashed=false",
        fields='files(id)',
        pageSize=1,
    ).execute()
    files = resp.get('files', [])
    return files[0]['id'] if files else None


def _upload(service, db_path, name, folder_id):
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(db_path), mimetype='application/x-sqlite3', resumable=False)
    existing_id = _find_file(service, name, folder_id)
    if existing_id:
        service.files().update(fileId=existing_id, media_body=media).execute()
    else:
        service.files().create(
            body={'name': name, 'parents': [folder_id]},
            media_body=media,
            fields='id',
        ).execute()


def backup_db(dated=True):
    """Upload db.sqlite3 to Google Drive. Raises on misconfiguration."""
    from django.conf import settings

    folder_id = os.environ.get('GDRIVE_BACKUP_FOLDER_ID', '')
    if not folder_id:
        raise EnvironmentError('GDRIVE_BACKUP_FOLDER_ID env var is not set.')

    db_path = Path(settings.DATABASES['default']['NAME'])
    if not db_path.exists():
        raise FileNotFoundError(f'Database file not found: {db_path}')

    service = _drive_service()
    _upload(service, db_path, LATEST_NAME, folder_id)

    if dated:
        dated_name = f"tzuratlink-{datetime.date.today().isoformat()}.db"
        _upload(service, db_path, dated_name, folder_id)


def backup_async(dated=True):
    """Fire-and-forget: run backup_db in a background thread. No-op if Drive is not configured."""
    if not os.environ.get('GDRIVE_BACKUP_FOLDER_ID'):
        return

    def run():
        try:
            backup_db(dated=dated)
        except Exception:
            logger.exception('DB backup to Google Drive failed')

    threading.Thread(target=run, daemon=True).start()
