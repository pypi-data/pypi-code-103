from django.core.management.base import BaseCommand, CommandError
from wcd_geo_db_sources.modules.process.cases import run_source
from wcd_geo_db_sources.modules.process.models import ProcessState
from wcd_geo_db_sources.modules.process import (
    ProcessParallelExecution, ProcessNoRunner, ProcessCantProceed
)


class Command(BaseCommand):
    help = 'Runs import for a specified source'

    def add_arguments(self, parser):
        parser.add_argument('source', nargs=1, type=str)

    def handle(self, *args, **options):
        result = False

        try:
            result = run_source(options['source'][0])
        except ProcessParallelExecution:
            raise CommandError('Parallel execution happened. Stopped.')
        except ProcessNoRunner:
            raise CommandError('No such runner for this type of source.')
        except ProcessCantProceed as e:
            raise CommandError(str(e))

        if not result:
            self.stdout.write(self.style.ERROR(
                'Execution failed. See details in admin interface.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('Import successful.'))
