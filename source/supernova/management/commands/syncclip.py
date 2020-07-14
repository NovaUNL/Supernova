import logging

from django.core.management.base import BaseCommand

from clip import synchronization as sync
from college import models as m

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Update the service entities with the clip crawled entities.'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='+', type=int)
        parser.add_argument('period', nargs='+', type=int)

    def handle(self, *args, **options):
        # TODO filter iterated objects
        year = options['year'][0]
        period = options['period'][0]

        sync.assert_buildings_inserted()
        logging.info("Syncing students")
        sync.sync_students()
        logging.info("Syncing teachers")
        sync.sync_teachers()
        logging.info("Syncing departments (recursive creation)")
        for department in m.Department.objects.all():
            sync.sync_department(department, recurse=True)
        logging.info("Syncing classes (recursive creation)")
        for class_ in m.Class.objects.select_related('department').all():
            sync.sync_class(class_.external_id, class_.department, recurse=True)
        logging.info("Syncing class instances (recursive creation)")
        for class_instance in m.ClassInstance.objects.select_related('parent').all():
            sync.sync_class_instance(class_instance.external_id, class_=class_instance.parent, recurse=True)

        # TODO re-enable following code
        # sync.calculate_active_classes()
        # for student in Student.objects.all():
        #     sync.student_enrollments(student)
        #     student.update_yearspan()
        #     student.save()
        #
        # # Annex remaining "students" to every user's abbreviations
        # for user in User.objects.all():
        #     user.update_primary()
        #     primary = user.primary_student
        #     if primary is not None:
        #         clip_students = clip.Student.objects.filter(abbreviation=primary.abbreviation).all()
        #         for clip_student in clip_students:
        #             student = sync.create_student(clip_student)
        #             student.user = user
        #             student.save()
        #         user.update_primary()
        #     user.save()
        #
        # for teacher in Teacher.objects.all():
        #     sync.teacher_turns(teacher)
        #
        # for course in Course.objects.all():
        #     course.active = \
        #         clip.Course.objects\
        #             .filter(course=course, students__enrollments__class_instance__year=2020)\
        #             .exists()
        #     course.save()
