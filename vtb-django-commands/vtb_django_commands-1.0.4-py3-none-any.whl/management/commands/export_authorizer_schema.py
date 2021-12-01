import json

from django.core.management import BaseCommand
from vtb_authorizer_utils.authorizer_schema_builder import AuthorizerSchemaBuilder


class Command(BaseCommand):
    """ Генерация конфигурации сервиса в json файл для authorizer """
    help = "Register service configuration"

    def add_arguments(self, parser):
        parser.add_argument('--file', help='File with json service configuration', required=True)

    def handle(self, *args, **options):
        file = options['file']
        builder = AuthorizerSchemaBuilder()

        with open(file, 'w', encoding="utf-8") as outfile:
            json.dump(builder.data, outfile, ensure_ascii=False)
