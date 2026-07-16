import time

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = (
        'Wait until the database accepts real connections before proceeding. '
        'Meant to run before migrate, since container start order between the '
        'app and sidecars (e.g. the Cloud SQL proxy) isn\'t guaranteed.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--timeout', type=int, default=60, help='Max seconds to wait (default: 60)')

    def handle(self, *args, **options):
        timeout = options['timeout']
        self.stdout.write('Waiting for database...')
        start = time.time()
        while True:
            try:
                connections['default'].cursor()
                self.stdout.write(self.style.SUCCESS('Database available.'))
                return
            except OperationalError:
                if time.time() - start > timeout:
                    raise CommandError(f'Database not available after {timeout}s')
                time.sleep(1)
