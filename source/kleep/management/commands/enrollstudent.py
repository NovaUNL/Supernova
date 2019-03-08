import logging

from django.core.management.base import BaseCommand
from college.clip_synchronization import student_enrollments
from college.models import Student

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Synchronizes the crawled enrollments and turns for a given student.'

    def add_arguments(self, parser):
        parser.add_argument('abbreviation', nargs='+', type=str)

    def handle(self, *args, **options):
        student = Student.objects.get(abbreviation=options['abbreviation'][0])
        student_enrollments(student)
