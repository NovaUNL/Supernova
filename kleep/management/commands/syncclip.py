import logging

from django.core.management.base import BaseCommand

from college.clip_synchronization import sync_classrooms, sync_departments, sync_class_and_instances
from clip import models as clip

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Update the service entities with the clip crawled entities.'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='+', type=int)
        parser.add_argument('period', nargs='+', type=int)

    def handle(self, *args, **options):
        year = options['year'][0]
        period = clip.Period.objects.get(id=options['period'][0])

        sync_classrooms()
        sync_departments()
        sync_class_and_instances(year, period, bootstrap=True)
