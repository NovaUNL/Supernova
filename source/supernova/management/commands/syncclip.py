import logging

from django.core.management.base import BaseCommand

from college import clip_synchronization as sync
from college.models import Student, Teacher, Course, ClassInstance
from users.models import User
from clip import models as clip

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
        sync.classes_(year, period, bootstrap=True)
        sync.calculate_active_classes()
        for student in Student.objects.all():
            sync.student_enrollments(student)
            student.update_yearspan()
            student.save()

        # Annex remaining "students" to every user's abbreviations
        for user in User.objects.all():
            user.update_primary()
            primary = user.primary_student
            if primary is not None:
                clip_students = clip.Student.objects.filter(abbreviation=primary.abbreviation).all()
                for clip_student in clip_students:
                    student = sync.create_student(clip_student)
                    student.user = user
                    student.save()
                user.update_primary()
            user.save()

        for teacher in Teacher.objects.all():
            sync.teacher_turns(teacher)

        for course in Course.objects.all():
            course.active = \
                clip.Course.objects\
                    .filter(course=course, students__enrollments__class_instance__year=2020)\
                    .exists()
            course.save()