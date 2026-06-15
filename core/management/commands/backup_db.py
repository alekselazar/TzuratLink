from django.core.management.base import BaseCommand, CommandError
from core.backup import backup_db


class Command(BaseCommand):
    help = 'Back up db.sqlite3 to Google Drive.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-dated',
            action='store_true',
            help='Only update tzuratlink-latest.db, skip the dated snapshot.',
        )

    def handle(self, *args, **options):
        try:
            backup_db(dated=not options['no_dated'])
            self.stdout.write(self.style.SUCCESS('Backup complete.'))
        except Exception as e:
            raise CommandError(str(e))
