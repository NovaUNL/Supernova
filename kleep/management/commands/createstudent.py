import logging

from django.core.management.base import BaseCommand
from college.clip_synchronization import create_student
from clip import models as clip

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Creates a student from crawled information.'

    def add_arguments(self, parser):
        parser.add_argument('abbreviation', nargs='+', type=str)

    def handle(self, *args, **options):
        clip_student = clip.Student.objects.get(abbreviation=options['abbreviation'][0])
        create_student(clip_student)
