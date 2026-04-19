from django.core.management.base import BaseCommand, CommandError
from core.utils import prerender_daf_yomi, prerender_all_pages, prerender_page


class Command(BaseCommand):
    help = 'Pre-render and cache pages for improved performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daf-yomi',
            action='store_true',
            help='Pre-render today\'s Daf Yomi pages'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Pre-render all available pages (resource-intensive)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of pages to pre-render (with --all)'
        )
        parser.add_argument(
            '--ref',
            type=str,
            default=None,
            help='Pre-render a specific page reference'
        )
        parser.add_argument(
            '--duration',
            type=int,
            default=86400,
            help='Cache duration in seconds (default: 86400 = 24h)'
        )

    def handle(self, *args, **options):
        duration = options['duration']
        
        if options['daf_yomi']:
            self.stdout.write(self.style.SUCCESS('Pre-rendering today\'s Daf Yomi...'))
            results = prerender_daf_yomi(cache_duration=duration)
            self._print_results(results)
            
        elif options['all']:
            limit = options['limit']
            msg = 'Pre-rendering all pages'
            if limit:
                msg += f' (limit: {limit})'
            self.stdout.write(self.style.SUCCESS(msg + '...'))
            results = prerender_all_pages(cache_duration=duration, limit=limit)
            self._print_results(results)
            
        elif options['ref']:
            ref = options['ref']
            self.stdout.write(self.style.SUCCESS(f'Pre-rendering {ref}...'))
            success, message = prerender_page(ref, cache_duration=duration)
            if success:
                self.stdout.write(self.style.SUCCESS(f'✓ {message}'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ {message}'))
            
        else:
            # Default: pre-render Daf Yomi
            self.stdout.write(self.style.SUCCESS('Pre-rendering today\'s Daf Yomi...'))
            results = prerender_daf_yomi(cache_duration=duration)
            self._print_results(results)

    def _print_results(self, results):
        """Print pre-render results"""
        success_count = 0
        error_count = 0
        
        for ref, (success, message) in results.items():
            if ref == 'error':
                self.stdout.write(self.style.ERROR(f'✗ {message}'))
                error_count += 1
            elif success:
                self.stdout.write(self.style.SUCCESS(f'✓ {message}'))
                success_count += 1
            else:
                self.stdout.write(self.style.WARNING(f'⚠ {message}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\nSummary: {success_count} successful, {error_count} errors'))
