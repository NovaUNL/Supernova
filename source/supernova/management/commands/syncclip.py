import logging

from django.core.management.base import BaseCommand

from college import clip_synchronization as sync

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Update the service entities with the clip crawled entities.'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='+', type=int)
        parser.add_argument('period', nargs='+', type=int)

    def handle(self, *args, **options):
        year = options['year'][0]
        period = options['period'][0]

        sync.rooms()
        sync.departments()
        sync.courses()
        sync.teachers()
        sync.class_and_instances(year, period, bootstrap=True)
