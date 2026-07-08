from django.core.management.base import BaseCommand
from core.backup import restore_db


class Command(BaseCommand):
    help = 'Restore db.sqlite3 from the latest Google Drive backup, if the local DB is missing.'

    def handle(self, *args, **options):
        if restore_db():
            self.stdout.write(self.style.SUCCESS('Database restored from Google Drive backup.'))
        else:
            self.stdout.write(self.style.WARNING(
                'No restore performed (DB already exists, no backup found, or Drive not configured).'
            ))
