from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    """ Получение токена для суперпользователя """
    help = 'Print admin token'

    def handle(self, *args, **options):
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            print('no superuser found')
        else:
            token, _ = Token.objects.get_or_create(user=superuser)
            print(token.key)
