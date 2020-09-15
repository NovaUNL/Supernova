import logging

from django.core.management.base import BaseCommand

logging.basicConfig(level=logging.INFO)
from users import models as users


class Command(BaseCommand):
    help = 'Updates the cached fields.'

    def handle(self, *args, **options):
        for user in users.User.objects.all():
            user.updated_cached()
            user.calculate_missing_info()
