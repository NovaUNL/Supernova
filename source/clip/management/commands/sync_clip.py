import logging
from datetime import timedelta, datetime
from queue import Queue
from threading import Lock, Thread
from time import sleep

from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings

from clip import synchronization as sync
from college import models as m

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

THREADS = 10


class Command(BaseCommand):
    help = 'Update the service entities with the clip crawled entities.'

    def add_arguments(self, parser):
        parser.add_argument('type', nargs='+', type=str)
        parser.add_argument('--no_update', action='store_true',
                            help='Do not request CLIPy to update itself when prompting for data')
        parser.add_argument('--no_optimize', action='store_true',
                            help='Do not attempt to skip redundant work or updates to recently updated entities.')
        parser.add_argument('--assert_buildings', action='store_true', help='Assert buildings are inserted')
        parser.add_argument('--rooms', action='store_true', help='Synchronize rooms')
        parser.add_argument('--departments', action='store_true', help='Synchronize departments')
        parser.add_argument('--courses', action='store_true', help='Synchronize courses')
        parser.add_argument('--force_class_info', action='store_true', help='Enforces that the class info is sync\'d')

    def handle(self, *args, **options):
        sync_type = options['type'][0]
        if sync_type not in ("fast", "slow", "full"):
            print("Bad type. Available types are: 'fast', 'slow' and 'full'.")
            exit(-1)

        update = not options['no_update']
        optimize = not options['no_optimize']
        assert_buildings = options['assert_buildings']
        room_sync = options['rooms']
        department_sync = options['departments']
        course_sync = options['courses']
        force_class_info = options['force_class_info']

        # Very fast
        if assert_buildings:
            sync.assert_buildings_inserted()
        if room_sync or sync_type == "full":
            if update:
                sync.request_rooms_update()
            log.info("Syncing rooms")
            sync.sync_rooms()
        if course_sync or sync_type == "full":
            if update:
                sync.request_courses_update()
            log.info("Syncing courses")
            sync.sync_courses()
        if department_sync or sync_type == "full":
            log.info("Syncing departments")
            sync.sync_departments()

        today = datetime.today()

        if sync_type == "fast":
            # Update (upstream) particularly relevant class instances
            logging.info("Syncing class instances")
            period_instances = m.PeriodInstance.objects.filter(date_from__lte=today, date_to__gte=today)
            class_instances = m.ClassInstance.objects \
                .select_related('parent') \
                .annotate(enrollment_count=Count('enrollments')) \
                .annotate(shift_count=Count('shifts')) \
                .filter(Q(enrollment_count__gt=0) | Q(shift_count__gt=0),
                        period_instance__in=period_instances,
                        external_update__lt=timezone.now() - timedelta(hours=4 if optimize else 0)) \
                .exclude(Q(disappeared=True) | Q(external_id=None)) \
                .all()
            if update:
                parallel_run(
                    class_instances,
                    lambda i: sync.request_class_instance_update(
                        external_id=i.external_id,
                        update_info=force_class_info,
                        update_enrollments=True,
                        update_shifts=True,
                        update_files=True))
            # Synchronize them
            parallel_run(class_instances, fast_instance_update)

            propagate_disappearances()

        elif sync_type == "slow":
            # Update upstream class data, will create related data but it wont update existing data
            if update:
                log.info("Updating upstream classes")
                sync.request_classes_update()
                log.info("Requesting teachers update")

                parallel_run(
                    m.Department.objects.values_list('external_id', flat=True)[3:],
                    lambda d: sync.request_teachers_update(d))
                for department in m.Department.objects.values_list('external_id', flat=True):
                    sync.request_teachers_update(department)

            sync.sync_classes(sync.Recursivity.CREATION)

            # Sync classes with recursive creation
            log.info("Synchronizing classes")
            for klass in m.Class.objects \
                    .exclude(Q(disappeared=True) | Q(external_id=None),
                             external_update__lt=timezone.now() - timedelta(days=1 if optimize else 0)):
                sync.sync_class(klass.external_id, recurse=sync.Recursivity.CREATION)

            # Update class instances upstream data and synchronize
            # the updated data with every class instance derivative
            class_instances = m.ClassInstance.objects \
                .select_related('parent') \
                .filter(year__gte=settings.COLLEGE_YEAR - settings.CLIPY_RECENT_YEAR_MARGIN,
                        external_update__lt=timezone.now() - timedelta(days=1 if optimize else 0)) \
                .exclude(Q(disappeared=True) | Q(external_id=None)) \
                .all()

            if update:
                log.info("Updating class instances")
                parallel_run(
                    class_instances,
                    lambda i: sync.request_class_instance_update(
                        external_id=i.external_id,
                        update_info=force_class_info,
                        update_enrollments=True,
                        update_shifts=True,
                        update_events=True,
                        update_grades=True,
                        update_files=True))

            # Synchronize found students
            log.info("Syncing students")
            sync.sync_students()

            logging.info("Syncing class instances")
            parallel_run(class_instances, slow_instance_update)
            propagate_disappearances()

            if update or not optimize:
                log.info("Syncing teachers")
                sync.sync_teachers()

        elif sync_type == "full":
            if update:
                # Update the National access contest, no dependencies
                log.info("Updating upstream admission data")
                sync.request_admissions_update()

                # Update upstream class data, will create related data but it wont update existing data
                log.info("Updating upstream classes")
                sync.request_classes_update()

                log.info("Requesting teachers update")
                for department in m.Department.objects.values_list('external_id', flat=True):
                    sync.request_teachers_update(department)

            # Store the current class instance data to request eventual update after the classes are updated
            # (to avoid duplicated updates)
            current_class_instance_ids = m.ClassInstance.objects \
                .exclude(Q(disappeared=True) | Q(external_id=None)) \
                .values_list('id', flat=True)

            log.info("Synchronizing classes")
            sync.sync_classes(sync.Recursivity.FULL)

            log.info("Synchronizing leftover class instances")
            # Sync classes with recursive creation
            parallel_run(
                m.Class.objects.exclude(Q(disappeared=True) | Q(external_id=None) | Q(
                    external_update__gt=timezone.now() - timedelta(days=5 if optimize else 0))),
                lambda klass: sync.sync_class(klass.external_id, recurse=sync.Recursivity.CREATION))

            # Propagate disappearances here to ensure that disappeared class derivatives are synchronized
            propagate_disappearances()

            # Subtract disappeared from the previously inserted class instances
            # Update their upstream data and synchronize the updated data with every class instance derivative
            logging.info("Updating class instances")
            previous_class_instances = m.ClassInstance.objects \
                .filter(id__in=current_class_instance_ids) \
                .select_related('parent') \
                .exclude(disappeared=True) \
                .all()
            if update:
                parallel_run(
                    previous_class_instances,
                    lambda i: sync.request_class_instance_update(
                        external_id=i.external_id,
                        update_info=True,
                        update_enrollments=True,
                        update_shifts=True,
                        update_events=True,
                        update_grades=True,
                        update_files=True))

            # Synchronize leftover students
            log.info("Syncing students")
            sync.sync_students()

            logging.info("Syncing class instances")
            parallel_run(
                previous_class_instances,
                lambda i: sync.sync_class_instance(i.external_id, recurse=sync.Recursivity.FULL))

            # By now every shift is known
            log.info("Syncing teachers")
            if update:
                for department in m.Department.objects.values_list('external_id', flat=True):
                    sync.request_teachers_update(department)
            sync.sync_teachers()
        else:
            raise Exception("Invalid option")

        update_cached()


def update_cached():
    log.info("Updating cached data")
    sync.calculate_active_classes()
    for student in m.Student.objects.all():
        student.update_progress_info()
    for teacher in m.Teacher.objects.all():
        teacher.update_yearspan()


def fast_instance_update(instance):
    sync.sync_class_instance(
        instance.external_id,
        klass=instance.parent,
        recurse=sync.Recursivity.CREATION)


def slow_instance_update(instance):
    sync.sync_class_instance(
        instance.external_id,
        klass=instance.parent,
        recurse=sync.Recursivity.FULL)


class ParallelQueueProcessor(Thread):
    def __init__(self, queue, lock, function):
        Thread.__init__(self)
        self.queue = queue
        self.lock = lock
        self.function = function

    def run(self):
        failures = 0
        while True:
            self.lock.acquire()
            remaining = self.queue.qsize()
            if remaining:
                object = self.queue.get()
                self.lock.release()
                try:
                    log.debug(f'Synchronizing {object}')
                    print(f"{remaining} objects remaining")
                    self.function(object)
                except sync.NetworkException:
                    log.error(f'Failed to sync {object}')
                    failures += 1
                    if failures > 5:
                        log.error(f"Failed to synchronize {object} for more than 5 times")
                        sleep(5)
            else:
                self.lock.release()
                break


def propagate_disappearances():
    m.ClassInstance.objects.filter(disappeared=False, parent__disappeared=True).update(disappeared=True)
    m.Shift.objects.filter(disappeared=False, class_instance__disappeared=True).update(disappeared=True)
    m.ShiftInstance.objects.filter(disappeared=False, shift__disappeared=True).update(disappeared=True)
    m.Enrollment.objects.filter(disappeared=False, class_instance__disappeared=True).update(disappeared=True)
    m.ClassFile.objects.filter(disappeared=False, class_instance__disappeared=True).update(disappeared=True)


def parallel_run(iterable, function):
    lock = Lock()
    item_queue = Queue()
    [item_queue.put(obj) for obj in iterable]
    threads = []
    for thread in range(0, THREADS):
        synchronizer = ParallelQueueProcessor(item_queue, lock, function)
        threads.append(synchronizer)
        synchronizer.start()
    for thread in threads:
        thread.join()
