import logging

from django.core.management.base import BaseCommand

import settings
from clip import synchronization as sync
from college import models as m

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Update the service entities with the clip crawled entities.'

    def add_arguments(self, parser):
        parser.add_argument('type', nargs='+', type=str)

    def handle(self, *args, **options):
        sync_type = options['type'][0]
        if sync_type not in ("fast", "slow", "full"):
            print("Bad type. Available types are: 'fast', 'slow' and 'full'.")
            exit(-1)

        # # Very fast
        sync.assert_buildings_inserted()
        sync.sync_rooms()
        logging.info("Syncing students")
        sync.sync_students()
        logging.info("Syncing teachers")
        # # TODO move teacher<->department sync to the sync_department method
        # #  as this needs to run twice to sync a new teacher to a department
        sync.sync_teachers()
        sync.sync_departments(recurse=True)

        if sync_type == "fast":
            logging.info("Syncing class instances")
            class_instances = m.ClassInstance.objects \
                .filter(year=settings.COLLEGE_YEAR, period=settings.COLLEGE_PERIOD) \
                .exclude(disappeared=True, external_id=None) \
                .select_related('parent')
            for class_instance in class_instances.all():
                sync.sync_class_instance(class_instance.external_id, class_=class_instance.parent, recurse=True)
                class_instance.refresh_from_db()
                for turn in class_instance.turns.exclude(disappeared=True, external_id=None).all():
                    sync.sync_turn(turn.external_id, class_inst=turn.class_instance, recurse=True)
                    turn.refresh_from_db()
                    for turn_instance in turn.instances.exclude(disappeared=True, external_id=None).all():
                        sync.sync_turn_instance(turn_instance.external_id, turn=turn)
        elif sync_type == "slow":
            for class_ in m.Class.objects.select_related('department').exclude(disappeared=True, external_id=None):
                sync.sync_class(class_.external_id, department=class_.department, recurse=True)
                class_.refresh_from_db()
                for instance in class_.instances \
                        .filter(year__gte=settings.COLLEGE_YEAR - 2) \
                        .exclude(disappeared=True, external_id=None).all():
                    sync.sync_class_instance(instance.external_id, class_=class_, recurse=True)
                    instance.refresh_from_db()
                    for enrollment in instance.enrollments.exclude(disappeared=True, external_id=None).all():
                        sync.sync_enrollment(enrollment.external_id, class_inst=instance)
                    for class_file in instance.files.exclude(disappeared=True, external_id=None).all():
                        sync.sync_class_instance_files(class_file.external_id, class_inst=instance)
            update_cached()
        elif sync_type == "full":
            for class_ in m.Class.objects.select_related('department').exclude(disappeared=True, external_id=None):
                sync.sync_class(class_.external_id, department=class_.department, recurse=True)
                class_.refresh_from_db()
                for instance in class_.instances.exclude(disappeared=True, external_id=None).all():
                    sync.sync_class_instance(instance.external_id, class_=class_, recurse=True)
                    instance.refresh_from_db()
                    for enrollment in instance.enrollments.exclude(disappeared=True, external_id=None).all():
                        sync.sync_enrollment(enrollment.external_id, class_inst=instance)
                    sync.sync_class_instance_files(instance.external_id, class_inst=instance)
            update_cached()


def update_cached():
    sync.calculate_active_classes()
    for student in m.Student.objects.all():
        student.update_yearspan()
        student.save()
    for teacher in m.Teacher.objects.all():
        teacher.update_yearspan()
