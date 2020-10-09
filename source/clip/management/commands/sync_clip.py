import logging

from django.core.management.base import BaseCommand
from django.db.models import Q

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

        # Very fast
        sync.assert_buildings_inserted()
        sync.sync_rooms()
        logging.info("Syncing students")
        sync.sync_students()
        logging.info("Syncing teachers")
        # TODO move teacher<->department sync to the sync_department method
        #  as this needs to run twice to sync a new teacher to a department
        sync.sync_teachers()
        sync.sync_classes(recurse=True)

        if sync_type == "fast":
            logging.info("Syncing class instances")
            class_instances = m.ClassInstance.objects \
                .exclude(disappeared=True, external_id=None) \
                .select_related('parent')
            for class_instance in class_instances.all():
                sync.sync_class_instance(class_instance.external_id, klass=class_instance.parent, recurse=True)
                class_instance.refresh_from_db()
                for shift in class_instance.shifts.exclude(Q(disappeared=True) | Q(external_id=None)).all():
                    sync.sync_shift(shift.external_id, class_inst=shift.class_instance, recurse=True)
                    shift.refresh_from_db()
                    for shift_instance in shift.instances.exclude(Q(disappeared=True) | Q(external_id=None)).all():
                        sync.sync_shift_instance(shift_instance.external_id, shift=shift)
        elif sync_type == "slow":
            for klass in m.Class.objects.exclude(Q(disappeared=True) | Q(external_id=None)):
                sync.sync_class(klass.external_id, recurse=True)
                klass.refresh_from_db()
                for instance in klass.instances \
                        .filter(year__gte=settings.COLLEGE_YEAR - 8) \
                        .exclude(Q(disappeared=True) | Q(external_id=None)).all():
                    sync.sync_class_instance(instance.external_id, klass=klass, recurse=True)
                    instance.refresh_from_db()
                    for enrollment in instance.enrollments.exclude(disappeared=True, external_id=None).all():
                        sync.sync_enrollment(enrollment.external_id, class_inst=instance)
                    sync.sync_class_instance_files(instance.external_id, class_inst=instance)
            update_cached()
        elif sync_type == "full":
            for klass in m.Class.objects.exclude(Q(disappeared=True) | Q(external_id=None)):
                sync.sync_class(klass.external_id, recurse=True)
                klass.refresh_from_db()
                for instance in klass.instances.exclude(disappeared=True, external_id=None).all():
                    sync.sync_class_instance(instance.external_id, klass=klass, recurse=True)
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
