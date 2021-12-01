import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    """ Создание администратора """
    help = 'Create project superuser from env'

    def handle(self, *args, **options):
        username = os.environ.get('SUPERUSER_USERNAME', 'admin')
        superuser = User.objects.filter(username=username).first()
        if superuser and not superuser.is_superuser:
            raise CommandError(f'User with username "{username}" already exists and isn\'t superuser')
        elif not superuser:
            User.objects.create_superuser(
                username,
                email=os.environ.get('SUPERUSER_EMAIL'),
                password=os.environ.get('SUPERUSER_PASSWORD', 'Qq654321'))
            self.stdout.write(self.style.SUCCESS(f'New superuser "{username}" has been created'))
        else:
            self.stdout.write(self.style.NOTICE(f'Superuser "{username}" already exists'))
