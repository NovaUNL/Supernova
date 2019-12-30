import logging

from django.core.management.base import BaseCommand
from supernova.models import Catchphrase

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Adds a catchphrase.'

    def add_arguments(self, parser):
        parser.add_argument('phrase', nargs='+', type=str)

    def handle(self, *args, **options):
        phrase = options['phrase'][0].strip()
        phrase = Catchphrase(phrase=phrase)
        phrase.save()
