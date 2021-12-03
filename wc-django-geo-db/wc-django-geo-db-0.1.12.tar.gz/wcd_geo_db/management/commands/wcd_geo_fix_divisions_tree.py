from django.core.management.base import BaseCommand
from wcd_geo_db.modules.bank.db import Division


class Command(BaseCommand):
    help = 'Runs import for a specified source'

    def add_arguments(self, parser):
        parser.add_argument('--times', nargs=1, type=int, default=3)

    def handle(self, *args, **options):
        fixed = Division.objects.update_roughly_invalid_tree(
            repeat_times=options['times']
        )

        if fixed > 0:
            self.stdout.write(self.style.WARNING(f'Successfully fixed {fixed} nodes.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'No fix required.'))
